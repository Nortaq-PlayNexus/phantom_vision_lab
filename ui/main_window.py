import os
import numpy as np
from typing import Dict, Any, Optional
from PIL import Image

from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QGroupBox, QSplitter, QTextEdit, QProgressBar,
    QTabWidget, QTableWidget, QTableWidgetItem, QComboBox,
    QSpinBox, QMessageBox, QScrollArea, QFrame, QSizePolicy, QHeaderView,
)
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPixmap, QImage
from PySide6.QtCore import QRectF, QPointF

from app.app_state import AppState
from stimuli.generator import StimulusConfig, StimulusGenerator
from altered_state.engine import AlteredStateEngine
from experiments.engine import ExperimentEngine
from ui.components import ImageViewer, StimulusAnimationThread, ExperimentThread


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PHANTOM VISION LAB")
        self.setMinimumSize(1400, 900)
        self.setStyleSheet("""
            QMainWindow { background: #0a0a12; }
            QWidget { background: #0a0a12; color: #e0e0e0; }
            QLabel { color: #e0e0e0; }
        """)

        self.state = AppState()
        self.stim_thread: Optional[StimulusAnimationThread] = None
        self.exp_thread: Optional[ExperimentThread] = None
        self._animating = False

        self._build_ui()
        self._connect_signals()
        self._init_stimulus()
        self._start_animation()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(4)
        main_layout.setContentsMargins(4, 4, 4, 4)

        header = QHBoxLayout()
        title = QLabel("PHANTOM VISION LAB")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #00ffff;")
        subtitle = QLabel("AI Altered-State & Structured-Light Perception Simulator")
        subtitle.setStyleSheet("color: #ff00ff; font-size: 11px;")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(subtitle)
        main_layout.addLayout(header)

        disclaimer = QLabel(self.state.safety_disclaimer)
        disclaimer.setStyleSheet("color: #666; font-size: 9px; border: 1px solid #333; padding: 2px;")
        main_layout.addWidget(disclaimer)

        # Tab widget for multiple views
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #00ffff33; border-radius: 4px; }
            QTabBar::tab { background: #14141f; color: #00ffff; padding: 6px 16px; margin-right: 2px;
                border: 1px solid #00ffff33; border-bottom: none; border-radius: 4px 4px 0 0; }
            QTabBar::tab:selected { background: #0a0a12; border-bottom: 2px solid #00ffff; }
        """)

        # Tab 1: Main view (stimulus + comparison + control)
        main_widget = QWidget()
        main_layout_tab = QHBoxLayout(main_widget)
        main_layout_tab.setSpacing(4)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(4)

        left_layout.addWidget(QLabel("LIVE STIMULUS"))
        self.stimulus_viewer = ImageViewer()
        self.stimulus_viewer.setMinimumWidth(500)
        left_layout.addWidget(self.stimulus_viewer, stretch=3)

        bottom_split = QSplitter(Qt.Horizontal)

        baseline_label = QLabel("BASELINE")
        baseline_label.setStyleSheet("color: #00ffff; font-weight: bold;")
        self._baseline_viewer = ImageViewer()
        self._baseline_viewer.setMinimumWidth(250)
        bottom_split.addWidget(baseline_label)
        bottom_split.addWidget(self._baseline_viewer)

        altered_label = QLabel("ALTERED")
        altered_label.setStyleSheet("color: #ff00ff; font-weight: bold;")
        self._altered_viewer = ImageViewer()
        self._altered_viewer.setMinimumWidth(250)
        bottom_split.addWidget(altered_label)
        bottom_split.addWidget(self._altered_viewer)

        left_layout.addWidget(bottom_split, stretch=2)

        self.divergence_bar = QProgressBar()
        self.divergence_bar.setRange(0, 100)
        self.divergence_bar.setValue(0)
        self.divergence_bar.setStyleSheet("""
            QProgressBar { background: #0a0a12; border: 1px solid #00ffff; border-radius: 4px; text-align: center; }
            QProgressBar::chunk { background: #00ffff; border-radius: 3px; }
        """)
        left_layout.addWidget(self.divergence_bar)

        self.divergence_label = QLabel("PERCEPTION DIVERGENCE: 0%")
        self.divergence_label.setStyleSheet("color: #00ffff; font-size: 12px; font-weight: bold;")
        left_layout.addWidget(self.divergence_label)

        self.metrics_text = QTextEdit()
        self.metrics_text.setReadOnly(True)
        self.metrics_text.setMaximumHeight(120)
        self.metrics_text.setStyleSheet("""
            QTextEdit { background: #0a0a12; color: #00ff88; border: 1px solid #00ffff33; font-family: monospace; font-size: 11px; }
        """)
        self.metrics_text.setPlaceholderText("Geometry | Symbolicity | Code-like | Novelty | Uncertainty")
        left_layout.addWidget(self.metrics_text)

        main_layout_tab.addWidget(left_widget)

        # Right side: Control panel + history
        right_widget = QWidget()
        right_main_layout = QVBoxLayout(right_widget)
        right_main_layout.setSpacing(4)

        # Control panel tab
        from ui.control_panel import ControlPanel
        self.control_panel = ControlPanel(app_state=self.state, parent=self)
        right_main_layout.addWidget(QLabel("CONTROL PANEL"))
        right_main_layout.addWidget(self.control_panel)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #aaa;")
        right_main_layout.addWidget(self.status_label)

        # Experiment history tab
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        history_layout.setSpacing(4)
        history_layout.addWidget(QLabel("EXPERIMENT HISTORY"))

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels([
            "ID", "Stimulus", "Pattern", "Divergence", "Confidence", "Novelty", "Time"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setMinimumHeight(150)
        self.history_table.setStyleSheet("""
            QTableWidget { background: #0a0a12; color: #e0e0e0; gridline-color: #333; }
            QTableWidget::item { padding: 4px; }
            QHeaderView::section { background: #14141f; color: #00ffff; padding: 4px; border: 1px solid #333; }
            QTableWidget::item:selected { background: #00ffff33; }
        """)
        self.history_table.itemSelectionChanged.connect(self._on_history_selected)
        self.history_table.doubleClicked.connect(self._on_history_replay)
        history_layout.addWidget(self.history_table)

        # History action buttons
        history_btn_layout = QHBoxLayout()

        self._selected_exp_id = None

        replay_btn = QPushButton("REPLAY SELECTED")
        replay_btn.setStyleSheet("""
            QPushButton { background: #0a0a12; color: #00ffff; border: 1px solid #00ffff;
                padding: 4px 12px; font-size: 10px; border-radius: 4px; }
            QPushButton:hover { background: #00ffff; color: #0a0a12; }
        """)
        replay_btn.clicked.connect(self._replay_selected)
        history_btn_layout.addWidget(replay_btn)

        view_btn = QPushButton("VIEW DETAILS")
        view_btn.setStyleSheet("""
            QPushButton { background: #0a0a12; color: #00ffff; border: 1px solid #00ffff;
                padding: 4px 12px; font-size: 10px; border-radius: 4px; }
            QPushButton:hover { background: #00ffff; color: #0a0a12; }
        """)
        view_btn.clicked.connect(self._view_selected_details)
        history_btn_layout.addWidget(view_btn)

        refresh_btn = QPushButton("REFRESH")
        refresh_btn.setStyleSheet("""
            QPushButton { background: #0a0a12; color: #00ffff; border: 1px solid #00ffff;
                padding: 4px 12px; font-size: 10px; border-radius: 4px; }
            QPushButton:hover { background: #00ffff; color: #0a0a12; }
        """)
        refresh_btn.clicked.connect(self._refresh_history)
        history_btn_layout.addWidget(refresh_btn)

        history_layout.addLayout(history_btn_layout)

        right_main_layout.addWidget(history_widget, stretch=1)

        main_layout_tab.addWidget(right_widget)

        self.tabs.addTab(main_widget, "Experiment")

        # Tab 2: Statistics Dashboard
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        stats_layout.setSpacing(4)
        stats_layout.addWidget(QLabel("STATISTICS DASHBOARD"))

        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setStyleSheet("""
            QTextEdit { background: #0a0a12; color: #00ff88; border: 1px solid #00ffff33; font-family: monospace; font-size: 11px; }
        """)
        self.stats_text.setPlaceholderText("Run experiments to see aggregate statistics...")
        stats_layout.addWidget(self.stats_text)

        refresh_stats_btn = QPushButton("COMPUTE STATISTICS")
        refresh_stats_btn.setStyleSheet("""
            QPushButton { background: #0a0a12; color: #00ffff; border: 1px solid #00ffff;
                padding: 6px 12px; font-size: 11px; border-radius: 4px; }
            QPushButton:hover { background: #00ffff; color: #0a0a12; }
        """)
        refresh_stats_btn.clicked.connect(self._compute_statistics)
        stats_layout.addWidget(refresh_stats_btn)

        self.tabs.addTab(stats_widget, "Statistics")

        main_layout.addWidget(self.tabs, stretch=1)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

    def _connect_signals(self):
        self.control_panel.experiment_finished.connect(self._on_experiment_finished)
        self.control_panel.status_updated.connect(self._on_status_updated)
        self.control_panel.progress_updated.connect(self._on_progress_updated)

    def _init_stimulus(self):
        self.stim_config = StimulusConfig(seed=42)
        self._update_stimulus_viewer()

    def _update_stimulus_viewer(self):
        img = self.state.get_stimulus_preview(self.stim_config)
        if img is not None:
            self.stimulus_viewer.set_image(img)

    def _start_animation(self):
        if self.stim_thread is not None:
            self.stim_thread.stop()
            self.stim_thread.wait(2000)
        self.stim_thread = StimulusAnimationThread(self.stim_config)
        self.stim_thread.frame_ready.connect(self.stimulus_viewer.set_image)
        self.stim_thread.start()

    def _refresh_history(self):
        self.history_table.setRowCount(0)
        experiments = self.state.get_all_experiments()
        for row, exp in enumerate(experiments):
            exp_id = exp.get("exp_id", exp.get("experiment_id", "N/A"))
            metadata = exp.get("metadata", {})
            if isinstance(metadata, dict):
                stimulus_id = metadata.get("stimulus_id", "N/A")
                config = metadata.get("stimulus_config", {})
                if isinstance(config, dict):
                    pattern = config.get("pattern_type", "N/A")
                else:
                    pattern = "N/A"
                timestamp = metadata.get("timestamp", "N/A")
                if isinstance(timestamp, str) and "T" in timestamp:
                    timestamp = timestamp.split("T")[0] + " " + timestamp.split("T")[1][:8]
            else:
                stimulus_id = "N/A"
                pattern = "N/A"
                timestamp = "N/A"

            measurements = exp.get("measurements", {})
            if isinstance(measurements, dict):
                divergence = measurements.get("divergence", {})
                if isinstance(divergence, dict):
                    div_score = divergence.get("perception_divergence_score", 0)
                else:
                    div_score = 0
                baseline = measurements.get("baseline", {})
                altered = measurements.get("altered", {})
                if isinstance(baseline, dict) and isinstance(altered, dict):
                    conf = altered.get("confidence", 0)
                    nov = altered.get("novelty", 0)
                else:
                    conf = 0
                    nov = 0
            else:
                div_score = 0
                conf = 0
                nov = 0

            self.history_table.insertRow(row)
            self.history_table.setItem(row, 0, QTableWidgetItem(str(exp_id)))
            self.history_table.setItem(row, 1, QTableWidgetItem(str(stimulus_id)))
            self.history_table.setItem(row, 2, QTableWidgetItem(str(pattern)))
            self.history_table.setItem(row, 3, QTableWidgetItem(f"{div_score:.6f}"))
            self.history_table.setItem(row, 4, QTableWidgetItem(f"{conf:.4f}" if isinstance(conf, (int, float)) else str(conf)))
            self.history_table.setItem(row, 5, QTableWidgetItem(f"{nov:.4f}" if isinstance(nov, (int, float)) else str(nov)))
            self.history_table.setItem(row, 6, QTableWidgetItem(str(timestamp)))

    def _on_history_selected(self):
        rows = self.history_table.selectionModel().selectedRows()
        if rows:
            row = rows[0].row()
            item = self.history_table.item(row, 0)
            if item:
                self._selected_exp_id = item.text()

    def _on_history_replay(self, index):
        item = self.history_table.item(index.row(), 0)
        if item:
            self._replay_experiment_by_id(item.text())

    def _replay_experiment_by_id(self, exp_id: str):
        if not exp_id or exp_id == "N/A":
            return
        result = self.state.replay_experiment(exp_id)
        if result:
            self._on_experiment_finished(result)
            self.status_label.setText(f"Replayed: {exp_id}")

    def _replay_selected(self):
        if self._selected_exp_id:
            self._replay_experiment_by_id(self._selected_exp_id)
        else:
            self.status_label.setText("Select an experiment to replay")

    def _view_selected_details(self):
        if not self._selected_exp_id:
            self.status_label.setText("Select an experiment to view")
            return
        data = self.state.get_experiment_data(self._selected_exp_id, "measurements")
        if data:
            divergence = data.get("divergence", {})
            baseline = data.get("baseline", {})
            altered = data.get("altered", {})
            details = f"Experiment: {self._selected_exp_id}\n\n"
            if isinstance(divergence, dict):
                details += f"Divergence: {divergence.get('perception_divergence_score', 0):.6f}\n"
                details += f"Geometry Diff: {divergence.get('geometry_diff', 0):.6f}\n"
                details += f"Novelty Diff: {divergence.get('novelty_diff', 0):.6f}\n"
                details += f"Embedding Distance: {divergence.get('embedding_distance', 0):.6f}\n"
            if isinstance(baseline, dict):
                details += f"\nBaseline Geometry: {baseline.get('geometry_score', 0):.4f}\n"
                details += f"Baseline Confidence: {baseline.get('confidence', 0):.4f}\n"
            if isinstance(altered, dict):
                details += f"\nAltered Geometry: {altered.get('geometry_score', 0):.4f}\n"
                details += f"Altered Confidence: {altered.get('confidence', 0):.4f}\n"
                details += f"Altered Novelty: {altered.get('novelty', 0):.4f}\n"
            msg = QMessageBox(self)
            msg.setWindowTitle(f"Details: {self._selected_exp_id}")
            msg.setText(details)
            msg.exec()
        else:
            self.status_label.setText(f"No data for: {self._selected_exp_id}")

    def _on_experiment_finished(self, results: dict):
        baseline = results.get("baseline", {})
        altered = results.get("altered", {})
        divergence = results.get("divergence", {})

        if "geometry_score" in baseline:
            self.metrics_text.setText(
                f"Geometry:     {baseline['geometry_score']:.2f}\n"
                f"Symbolicity:  {altered.get('symmetry_score', 0):.2f}\n"
                f"Code-like:    {len(altered.get('code_like_structures', []))}\n"
                f"Novelty:      {altered.get('novelty', 0):.2f}\n"
                f"Uncertainty:  {altered.get('uncertainty', 0):.2f}"
            )

        div_score = divergence.get("perception_divergence_score", 0) * 100
        self.divergence_bar.setValue(int(div_score))
        self.divergence_label.setText(f"PERCEPTION DIVERGENCE: {div_score:.1f}%")

        if baseline and "geometry_score" in baseline:
            baseline_img = np.zeros((512, 512, 3), dtype=np.uint8)
            self._baseline_viewer.set_image(baseline_img)

        if altered and "geometry_score" in altered:
            altered_img = np.zeros((512, 512, 3), dtype=np.uint8)
            self._altered_viewer.set_image(altered_img)

        report = results.get("report", {})
        if report:
            self._show_report_dialog(report)

        self._refresh_history()
        self._compute_statistics()

    def _compute_statistics(self):
        report = self.state.get_stats_report()
        if "note" in report:
            self.stats_text.setText(report["note"])
            return

        lines = ["=" * 60]
        lines.append("PHANTOM VISION LAB - AGGREGATE STATISTICS")
        lines.append(f"Total Experiments: {report['total_experiments']}")
        lines.append("=" * 60)

        for metric_name, metric_data in report.items():
            if metric_name == "total_experiments":
                continue
            lines.append("")
            lines.append(f"--- {metric_name.upper()} ---")

            for group_name, group_data in metric_data.items():
                if group_name == "comparison":
                    lines.append(f"  Comparison (t-test):")
                    if "note" in group_data:
                        lines.append(f"    {group_data['note']}")
                    else:
                        lines.append(f"    t-statistic: {group_data.get('t_statistic', 0):.4f}")
                        lines.append(f"    p-value: {group_data.get('p_value', 1):.4f}")
                        lines.append(f"    effect size (Cohen's d): {group_data.get('effect_size', 0):.4f}")
                        lines.append(f"    significant (p<0.05): {group_data.get('significant', False)}")
                elif isinstance(group_data, dict) and "mean" in group_data:
                    lines.append(f"  {group_name}:")
                    lines.append(f"    Mean: {group_data.get('mean', 0):.4f}")
                    lines.append(f"    Median: {group_data.get('median', 0):.4f}")
                    lines.append(f"    Std Dev: {group_data.get('std', 0):.4f}")
                    lines.append(f"    Range: [{group_data.get('min', 0):.4f}, {group_data.get('max', 0):.4f}]")
                    lines.append(f"    Count: {group_data.get('count', 0)}")
                else:
                    lines.append(f"  {group_name}: {group_data}")

        self.stats_text.setText("\n".join(lines))

    def _show_report_dialog(self, report: dict):
        msg = QMessageBox(self)
        msg.setWindowTitle(f"Report - {report.get('experiment_id', '')}")
        text = (
            f"Experiment: {report.get('experiment_id', '')}\n"
            f"Divergence Score: {report.get('perception_divergence_score', 0):.4f}\n"
            f"Confidence: {report.get('confidence', 0):.4f}\n"
            f"Changes: {', '.join(report.get('changes_from_baseline', []))}\n\n"
            f"Interpretation:\n{report.get('scientific_interpretation', 'N/A')}"
        )
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Save)
        msg.exec()

    def _on_status_updated(self, status: str):
        self.status_label.setText(status)

    def _on_progress_updated(self, value: int):
        self.progress_bar.setValue(value)

    def closeEvent(self, event):
        if self.stim_thread:
            self.stim_thread.stop()
            self.stim_thread.wait(2000)
        if self.exp_thread:
            self.exp_thread.wait(5000)
        event.accept()
