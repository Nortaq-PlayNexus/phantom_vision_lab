import os
import json
import numpy as np
from PIL import Image
from typing import Dict, Any, Optional

from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QGroupBox, QSplitter, QTextEdit,
    QProgressBar, QComboBox, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView,
)
from PySide6.QtGui import QPainter, QImage, QFont


class ImageViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = None
        self.setMinimumSize(400, 400)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_image(self, img_array):
        if isinstance(img_array, np.ndarray):
            if len(img_array.shape) == 2:
                self.image = Image.fromarray(img_array, mode="L")
            else:
                self.image = Image.fromarray(img_array.astype(np.uint8))
            self.update()

    def _to_qimage(self):
        if self.image is None:
            return None
        rgb = self.image.convert("RGB")
        data = rgb.tobytes()
        return QImage(data, rgb.width, rgb.height, rgb.width * 3, QImage.Format_RGB888)

    def paintEvent(self, event):
        super().paintEvent(event)
        qimg = self._to_qimage()
        if qimg and qimg.width() > 0 and qimg.height() > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            scaled = qimg.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawImage(x, y, scaled)
            painter.end()


class StimulusAnimationThread(QThread):
    frame_ready = Signal(object)

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.running = True

    def run(self):
        from stimuli.generator import StimulusGenerator, StimulusConfig
        gen = StimulusGenerator()
        t = 0
        while self.running:
            cfg = StimulusConfig(**{k: v for k, v in self.config.__dict__.items()})
            cfg.temporal_modulation = (np.sin(t * 0.05) + 1) / 2
            try:
                img, meta = gen.generate(cfg)
                self.frame_ready.emit(img)
            except Exception:
                pass
            t += 1
            ms = max(16, min(200, int(50 + (1.0 - self.config.brightness) * 200)))
            self.msleep(ms)

    def stop(self):
        self.running = False


class ExperimentThread(QThread):
    finished = Signal(dict)
    progress = Signal(int)
    status = Signal(str)

    def __init__(self, app_state, stimulus_config, altered_params, parent=None):
        super().__init__(parent)
        self.app_state = app_state
        self.stimulus_config = stimulus_config
        self.altered_params = altered_params

    def run(self):
        self.status.emit("Generating stimulus...")
        self.progress.emit(10)
        result = self.app_state.engine.run_experiment(
            self.stimulus_config, altered_params=self.altered_params)
        self.progress.emit(80)
        self.status.emit("Generating report...")
        all_data = self.app_state.store.get_experiment(result["experiment_id"])
        measurements = all_data.get("measurements") if all_data else {}
        baseline = all_data.get("baseline") if all_data else {}
        altered = all_data.get("altered") if all_data else {}
        report = self.app_state.reporter.generate(
            result["experiment_id"], baseline or {}, altered or {},
            result["divergence"], measurements or {})
        result["report"] = report.to_dict()

        from storage.exporter import Exporter
        exporter = Exporter(self.app_state.store.experiments_dir)
        exporter.export_json(result["experiment_id"], result)
        exporter.export_csv(result["experiment_id"], result)
        exporter.export_html_report(result["experiment_id"], report.to_dict())
        exporter.export_markdown_report(result["experiment_id"], report.to_dict())

        self.progress.emit(100)
        self.finished.emit(result)
