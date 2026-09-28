import os
import json
import numpy as np
from PIL import Image
from typing import Dict, Any, Optional

from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QGroupBox, QSplitter, QTextEdit,
    QProgressBar, QComboBox, QMessageBox,
)
from PySide6.QtGui import QPainter, QImage, QFont

from app.app_state import AppState
from stimuli.generator import StimulusConfig, StimulusGenerator
from altered_state.engine import AlteredStateEngine
from ui.components import ImageViewer, ExperimentThread


class ControlPanel(QWidget):
    params_changed = Signal(dict)
    experiment_finished = Signal(dict)
    status_updated = Signal(str)
    progress_updated = Signal(int)

    def __init__(self, app_state=None, parent=None):
        super().__init__(parent)
        self.state = app_state
        self.altered_engine = AlteredStateEngine()
        self.exp_thread = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        title = QLabel("ALTERED STATE CONTROL PANEL")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setStyleSheet("color: #00ffff;")
        layout.addWidget(title)

        self.sliders = {}
        for param in AlteredStateEngine.PARAMS:
            group = QGroupBox(param.display_name)
            glayout = QVBoxLayout(group)
            glayout.setSpacing(4)

            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 100)
            slider.setValue(int(param.default))
            slider.setStyleSheet("""
                QSlider::groove:horizontal { height: 6px; background: #1a1a2e; border-radius: 3px; }
                QSlider::handle:horizontal { width: 14px; background: #00ffff; border-radius: 7px; margin: -4px 0; }
                QSlider::sub-page:horizontal { background: #00ffff; border-radius: 3px; }
            """)
            slider.valueChanged.connect(lambda v, n=param.name: self._on_slider_changed(n, v))

            label = QLabel(f"{param.explanation} [{int(param.default)}]")
            label.setStyleSheet("color: #aaa; font-size: 10px;")

            glayout.addWidget(slider)
            glayout.addWidget(label)
            self.sliders[param.name] = slider
            layout.addWidget(group)

        btn_layout = QHBoxLayout()
        for btn_text, slot in [
            ("RESET", self._reset),
            ("RANDOMIZE", self._randomize),
            ("SAVE PRESET", self._save_preset),
            ("LOAD PRESET", self._load_preset),
            ("RUN EXPERIMENT", self._run_experiment),
        ]:
            btn = QPushButton(btn_text)
            btn.setStyleSheet("""
                QPushButton { background: #0a0a12; color: #00ffff; border: 1px solid #00ffff;
                    padding: 6px 12px; font-size: 11px; border-radius: 4px; }
                QPushButton:hover { background: #00ffff; color: #0a0a12; }
            """)
            btn.clicked.connect(slot)
            btn_layout.addWidget(btn)

        layout.addLayout(btn_layout)

        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("PRESETS:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["BASELINE", "LOW PERTURBATION", "HIGH SENSORY GAIN",
                                      "HIGH PREDICTION ERROR", "PATTERN AMPLIFICATION", "MAXIMUM EXPLORATION"])
        self.preset_combo.currentTextChanged.connect(self._apply_preset)
        self.preset_combo.setStyleSheet("color: #e0e0e0; background: #0a0a12; padding: 4px;")
        preset_layout.addWidget(self.preset_combo)
        layout.addLayout(preset_layout)

    def _on_slider_changed(self, name: str, value: int):
        self.altered_engine.set_param(name, float(value))
        if name in self.sliders:
            lbl = self.sliders[name].parent().findChild(QLabel)
            if lbl:
                lbl.setText(f"{AlteredStateEngine.PARAMS[[p.name for p in AlteredStateEngine.PARAMS].index(name)].description} [{value}]")
        self.params_changed.emit(self.altered_engine.to_dict())

    def _reset(self):
        self.altered_engine.reset()
        for name, slider in self.sliders.items():
            slider.setValue(int(self.altered_engine.get_param(name)))
        self.params_changed.emit(self.altered_engine.to_dict())

    def _randomize(self):
        self.altered_engine.randomize()
        for name, slider in self.sliders.items():
            slider.setValue(int(self.altered_engine.get_param(name)))
        self.params_changed.emit(self.altered_engine.to_dict())

    def _apply_preset(self, preset: str):
        self.altered_engine.apply_preset(preset)
        for name, slider in self.sliders.items():
            slider.setValue(int(self.altered_engine.get_param(name)))
        self.params_changed.emit(self.altered_engine.to_dict())

    def _save_preset(self):
        if self.state is None:
            return
        preset_name = self.preset_combo.currentText()
        preset_data = self.altered_engine.to_dict()
        preset_path = os.path.join(
            self.state.store.experiments_dir, f"preset_{preset_name.replace(' ', '_').upper()}.json")
        with open(preset_path, "w") as f:
            json.dump(preset_data, f, indent=2)
        self.status_updated.emit(f"Preset saved: {preset_name}")

    def _load_preset(self):
        if self.state is None:
            return
        preset_name = self.preset_combo.currentText()
        preset_path = os.path.join(
            self.state.store.experiments_dir, f"preset_{preset_name.replace(' ', '_').upper()}.json")
        if os.path.exists(preset_path):
            with open(preset_path, "r") as f:
                data = json.load(f)
            for k, v in data.items():
                self.altered_engine.set_param(k, float(v))
            for name, slider in self.sliders.items():
                slider.setValue(int(self.altered_engine.get_param(name)))
            self.params_changed.emit(self.altered_engine.to_dict())
            self.status_updated.emit(f"Preset loaded: {preset_name}")
        else:
            self.status_updated.emit(f"Preset not found: {preset_name}")

    def _run_experiment(self):
        if self.state is None:
            return
        if self.exp_thread is not None and self.exp_thread.isRunning():
            self.status_updated.emit("Experiment already running...")
            return
        params = self.altered_engine.to_dict()
        stim_config = StimulusConfig(seed=42)
        self.exp_thread = ExperimentThread(self.state, stim_config, params)
        self.exp_thread.finished.connect(self._on_experiment_done)
        self.exp_thread.status.connect(self.status_updated)
        self.exp_thread.progress.connect(self.progress_updated)
        self.exp_thread.start()

    def _on_experiment_done(self, results: dict):
        self.exp_thread = None
        self.experiment_finished.emit(results)

    def get_params(self) -> Dict[str, float]:
        return self.altered_engine.to_dict()
