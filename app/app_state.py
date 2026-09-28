import os
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from PySide6.QtCore import QObject, Signal

from config.settings import settings
from stimuli.generator import StimulusGenerator, StimulusConfig
from altered_state.engine import AlteredStateEngine
from experiments.engine import ExperimentEngine
from reports.reporter import ReportGenerator, PerceptionReport
from storage.experiment_store import ExperimentStore
from storage.exporter import Exporter
from analysis.metrics import PerceptionMetrics, compute_perception_divergence
from statistics.stats import StatisticsEngine


class AppState(QObject):
    experiment_finished = Signal(dict)
    experiment_started = Signal(str)
    status_updated = Signal(str)
    progress_updated = Signal(int)

    def __init__(self):
        super().__init__()
        self.engine = ExperimentEngine()
        self.store = self.engine.store
        self.exporter = Exporter(self.store.experiments_dir)
        self.reporter = ReportGenerator()
        self.altered_engine = AlteredStateEngine()
        self.stimulus_gen = StimulusGenerator()
        self.stats = self.engine.stats

        self.current_stimulus_config: Optional[StimulusConfig] = None
        self.current_experiment_id: Optional[str] = None
        self.experiment_results: Dict[str, Any] = {}
        self.experiment_history: List[Dict[str, Any]] = []

        self.safety_disclaimer = (
            "This software simulates computational changes in AI perception. "
            "It does not reproduce a biological psychedelic state and does not establish subjective consciousness."
        )

        self.hardware_info = _detect_hw()
        settings.cpu_count = self.hardware_info.cpu_count
        settings.ram_mb = self.hardware_info.ram_mb
        settings.cuda_available = self.hardware_info.cuda_available
        settings.vram_mb = self.hardware_info.vram_mb
        settings.hardware_mode = self.hardware_info.hardware_mode

    def run_experiment(self, config: StimulusConfig, params: Dict[str, float] = None):
        self.experiment_started.emit("running_experiment")
        self.status_updated.emit("Generating stimulus...")
        self.progress_updated.emit(10)

        result = self.engine.run_experiment(config, params)
        self.current_experiment_id = result["experiment_id"]
        self.current_stimulus_config = config

        self.status_updated.emit("Generating report...")
        self.progress_updated.emit(80)

        measurements = self.store.get_experiment_data(self.current_experiment_id, "measurements")
        baseline = self.store.get_experiment_data(self.current_experiment_id, "baseline")
        altered = self.store.get_experiment_data(self.current_experiment_id, "altered")

        report = self.reporter.generate(
            self.current_experiment_id,
            baseline or {}, altered or {},
            result.get("divergence", {}),
            measurements or {},
        )

        from storage.exporter import Exporter
        exporter = Exporter(self.store.experiments_dir)
        report_dict = report.to_dict()
        exporter.export_json(self.current_experiment_id, {
            **self.experiment_results, "report": report_dict,
        })
        exporter.export_csv(self.current_experiment_id, self.experiment_results)
        exporter.export_html_report(self.current_experiment_id, report_dict)
        exporter.export_markdown_report(self.current_experiment_id, report_dict)

        self.experiment_results = {
            "experiment_id": self.current_experiment_id,
            "baseline": result.get("baseline", {}),
            "altered": result.get("altered", {}),
            "divergence": result.get("divergence", {}),
            "summary": result.get("summary", {}),
            "report": report.to_dict(),
            "stimulus_path": result.get("stimulus_path", ""),
        }

        self.experiment_history.append(self.experiment_results.copy())
        self.experiment_finished.emit(self.experiment_results)
        self.status_updated.emit("Experiment complete")
        self.progress_updated.emit(100)
        return self.experiment_results

    def replay_experiment(self, exp_id: str) -> Optional[Dict[str, Any]]:
        result = self.engine.replay_experiment(exp_id)
        if result:
            self.experiment_results = result
        return result

    def get_experiment_data(self, exp_id: str, category: str) -> Optional[Dict[str, Any]]:
        data = self.store.get_experiment(exp_id)
        return data.get(category) if data else None

    def get_all_experiments(self) -> List[Dict[str, Any]]:
        return self.store.list_experiments()

    def get_stats_report(self) -> Dict[str, Any]:
        return self.stats.get_aggregate_report()

    def get_stimulus_preview(self, config: StimulusConfig) -> Optional[any]:
        try:
            img, meta = self.stimulus_gen.generate(config)
            return img
        except Exception:
            return None


def _detect_hw():
    from models.hardware import detect_hardware
    return detect_hardware()
