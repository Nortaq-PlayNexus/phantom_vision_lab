import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import numpy as np
from PIL import Image

from config.settings import settings
from storage.experiment_store import ExperimentStore
from stimuli.generator import StimulusGenerator, StimulusConfig
from altered_state.engine import AlteredStateEngine
from vision import VisionModelProvider
from analysis.metrics import PerceptionMetrics, compute_perception_divergence
from statistics.stats import ExperimentSummary, StatisticsEngine


class ExperimentEngine:
    def __init__(self):
        self.store = ExperimentStore()
        self.stimulus_gen = StimulusGenerator()
        self.vision = VisionModelProvider()
        self.stats = StatisticsEngine()

    def run_experiment(
        self,
        stimulus_config: StimulusConfig,
        altered_params: Dict[str, float] = None,
    ) -> Dict[str, Any]:
        exp_id = self.store.create_experiment(
            stimulus_id=stimulus_config.seed,
            params={**stimulus_config.__dict__, **(altered_params or {})},
        )
        rng_seed = np.random.RandomState().randint(0, 100000)

        img, stim_meta = self.stimulus_gen.generate(stimulus_config)
        stim_path = os.path.join(self.store.experiments_dir, exp_id, "stimulus.png")
        self.stimulus_gen.save(img, stim_meta, stim_path)

        baseline_result = self.vision.analyze(img)
        altered_params_obj = AlteredStateEngine(seed=stimulus_config.seed)
        if altered_params:
            for k, v in altered_params.items():
                altered_params_obj.set_param(k, v)

        baseline_dict = baseline_result.to_dict()
        altered_metrics_dict = altered_params_obj.apply_to_metrics(baseline_dict, rng_seed)
        altered_result = self._dict_to_metrics(altered_metrics_dict)

        divergence = compute_perception_divergence(baseline_result, altered_result)

        baseline_data = {
            "metrics": baseline_dict,
            "model": settings.model_name,
            "model_version": settings.model_version,
        }
        altered_data = {
            "metrics": altered_metrics_dict,
            "params": altered_params_obj.to_dict(),
            "model": settings.model_name,
            "model_version": settings.model_version,
        }
        measurements = {
            "divergence": divergence,
            "baseline": baseline_dict,
            "altered": altered_metrics_dict,
            "stimulus_metadata": stim_meta,
            "random_seed": rng_seed,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "timestamp_unix": datetime.now(timezone.utc).timestamp(),
        }

        self.store.save_experiment_data(exp_id, {
            "experiment_id": exp_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": settings.model_name,
            "model_version": settings.model_version,
            "stimulus_id": str(stimulus_config.seed),
            "random_seed": rng_seed,
            "altered_params": altered_params_obj.to_dict(),
            "stimulus_config": stimulus_config.__dict__,
        }, "metadata")
        self.store.save_experiment_data(exp_id, baseline_data, "baseline")
        self.store.save_experiment_data(exp_id, altered_data, "altered")
        self.store.save_experiment_data(exp_id, measurements, "measurements")

        summary = ExperimentSummary(
            experiment_id=exp_id,
            baseline_geometry=baseline_result.geometry_score,
            altered_geometry=altered_result.geometry_score,
            baseline_novelty=baseline_result.novelty,
            altered_novelty=altered_result.novelty,
            baseline_uncertainty=baseline_result.uncertainty,
            altered_uncertainty=altered_result.uncertainty,
            baseline_confidence=baseline_result.confidence,
            altered_confidence=altered_result.confidence,
            perception_divergence=divergence.get("perception_divergence_score", 0),
            baseline_code_like=len(baseline_result.code_like_structures),
            altered_code_like=len(altered_result.code_like_structures),
        )
        self.stats.add_experiment(summary)

        return {
            "experiment_id": exp_id,
            "stimulus_path": stim_path,
            "baseline": baseline_result.to_dict(),
            "altered": altered_result.to_dict(),
            "divergence": divergence,
            "summary": {
                "perception_divergence_score": divergence.get("perception_divergence_score", 0),
                "geometry_diff": divergence.get("geometry_diff", 0),
                "novelty_diff": divergence.get("novelty_diff", 0),
                "embedding_distance": divergence.get("embedding_distance", 0),
            },
        }

    def replay_experiment(self, exp_id: str) -> Optional[Dict[str, Any]]:
        data = self.store.get_experiment(exp_id)
        if not data:
            return None
        metadata = data.get("metadata", {})
        stim_cfg_dict = metadata.get("stimulus_config", {})
        stim_cfg = StimulusConfig(**{k: v for k, v in stim_cfg_dict.items()
                                      if k in StimulusConfig.__dataclass_fields__})
        img_path = os.path.join(self.store.experiments_dir, exp_id, "stimulus.png")
        if os.path.exists(img_path):
            img = np.array(Image.open(img_path))
        else:
            img, _ = self.stimulus_gen.generate(stim_cfg)

        altered_params = metadata.get("altered_params", {})
        baseline = self.vision.analyze(img)
        rng_seed = metadata.get("random_seed", 42)

        altered_state = AlteredStateEngine(seed=stim_cfg.seed)
        for k, v in altered_params.items():
            altered_state.set_param(k, v)
        altered_dict = altered_state.apply_to_metrics(baseline.to_dict(), rng_seed)
        altered = self._dict_to_metrics(altered_dict)

        divergence = compute_perception_divergence(baseline, altered)

        return {
            "experiment_id": exp_id,
            "baseline": baseline.to_dict(),
            "altered": altered.to_dict(),
            "divergence": divergence,
            "replayed": True,
        }

    def _dict_to_metrics(self, d: Dict) -> PerceptionMetrics:
        return PerceptionMetrics(
            objects=d.get("objects", []),
            patterns=d.get("patterns", []),
            geometry_score=d.get("geometry_score", 0),
            symmetry_score=d.get("symmetry_score", 0),
            color_palette=[tuple(c) for c in d.get("color_palette", [])],
            spatial_relationships=d.get("spatial_relationships", []),
            text_like_structures=d.get("text_like_structures", []),
            symbols=d.get("symbols", []),
            code_like_structures=d.get("code_like_structures", []),
            semantic_concepts=d.get("semantic_concepts", []),
            confidence=d.get("confidence", 0),
            novelty=d.get("novelty", 0),
            uncertainty=d.get("uncertainty", 0),
        )
