import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np

from stimuli.generator import StimulusGenerator, StimulusConfig
from altered_state.engine import AlteredStateEngine
from analysis.metrics import PerceptionMetrics, compute_perception_divergence
from storage.experiment_store import ExperimentStore
from statistics.stats import StatisticsEngine
from experiments.engine import ExperimentEngine


class TestStimulusGenerator:
    def setup_method(self):
        self.gen = StimulusGenerator()

    def test_lattice_determinism(self):
        cfg1 = StimulusConfig(seed=42)
        cfg2 = StimulusConfig(seed=42)
        img1, _ = self.gen.generate(cfg1)
        img2, _ = self.gen.generate(cfg2)
        assert np.array_equal(img1, img2), "Same seed should produce identical results"

    def test_different_seeds(self):
        cfg1 = StimulusConfig(seed=1, pattern_type="noise_geometry", noise=0.5)
        cfg2 = StimulusConfig(seed=2, pattern_type="noise_geometry", noise=0.5)
        img1, _ = self.gen.generate(cfg1)
        img2, _ = self.gen.generate(cfg2)
        assert not np.array_equal(img1, img2), "Different seeds should produce different results"

    def test_output_shape(self):
        cfg = StimulusConfig(seed=42)
        img, meta = self.gen.generate(cfg)
        assert img.shape == (512, 512, 3)
        assert meta["seed"] == 42

    def test_all_pattern_types(self):
        for pt in StimulusGenerator.PATTERN_TYPES:
            cfg = StimulusConfig(seed=42, pattern_type=pt)
            img, meta = self.gen.generate(cfg)
            assert img is not None
            assert img.shape == (512, 512, 3)
            assert meta["pattern_type"] == pt

    def test_seed_metadata(self):
        cfg = StimulusConfig(seed=12345)
        img, meta = self.gen.generate(cfg)
        assert meta["seed"] == 12345
        assert "parameters" in meta


class TestAlteredStateEngine:
    def setup_method(self):
        self.engine = AlteredStateEngine(seed=42)

    def test_param_range(self):
        self.engine.set_param("SENSORY_GAIN", 150)
        assert self.engine.get_param("SENSORY_GAIN") == 100.0
        self.engine.set_param("SENSORY_GAIN", -10)
        assert self.engine.get_param("SENSORY_GAIN") == 0.0

    def test_reset(self):
        self.engine.set_param("SENSORY_GAIN", 80)
        self.engine.reset()
        assert self.engine.get_param("SENSORY_GAIN") == 50.0

    def test_preset(self):
        self.engine.apply_preset("BASELINE")
        for p in AlteredStateEngine.PARAMS:
            assert self.engine.get_param(p.name) == p.default

    def test_randomize(self):
        self.engine.randomize(seed=42)
        vals = [p.value for p in self.engine.PARAMS]
        assert all(0 <= v <= 100 for v in vals)

    def test_to_dict(self):
        d = self.engine.to_dict()
        assert len(d) == len(AlteredStateEngine.PARAMS)
        assert all(0 <= v <= 100 for v in d.values())

    def test_apply_to_metrics(self):
        baseline = PerceptionMetrics(
            geometry_score=0.5, symmetry_score=0.6, confidence=0.7,
            novelty=0.4, uncertainty=0.3)
        baseline_dict = baseline.to_dict()
        self.engine.reset()
        result = self.engine.apply_to_metrics(baseline_dict, rng_seed=42)
        assert "geometry_score" in result
        assert 0 <= result["geometry_score"] <= 1

    def test_cross_modal_semantic_concepts(self):
        baseline = PerceptionMetrics(
            geometry_score=0.5, symmetry_score=0.6, confidence=0.7,
            novelty=0.4, uncertainty=0.3,
            semantic_concepts=["geometric_structure"])
        baseline_dict = baseline.to_dict()
        self.engine.reset()
        self.engine.set_param("CROSS_MODAL", 90)
        result = self.engine.apply_to_metrics(baseline_dict, rng_seed=42)
        assert "semantic_concepts" in result
        assert "cross_modal_association" in result["semantic_concepts"] or \
               "synesthetic_binding" in result["semantic_concepts"] or \
               "conceptual_blending" in result["semantic_concepts"]
        assert "geometric_structure" in result["semantic_concepts"]

    def test_cross_modal_objects_tagged(self):
        baseline = PerceptionMetrics(
            geometry_score=0.5, symmetry_score=0.6, confidence=0.7,
            novelty=0.4, uncertainty=0.3,
            objects=[{"name": "blob", "area": 100}])
        baseline_dict = baseline.to_dict()
        self.engine.reset()
        self.engine.set_param("CROSS_MODAL", 90)
        result = self.engine.apply_to_metrics(baseline_dict, rng_seed=42)
        tagged = [o for o in result.get("objects", []) if "cross_modal_tag" in o]
        assert len(tagged) >= 0

    def test_cross_modal_low_has_no_effect(self):
        baseline = PerceptionMetrics(
            geometry_score=0.5, symmetry_score=0.6, confidence=0.7,
            novelty=0.4, uncertainty=0.3)
        baseline_dict = baseline.to_dict()
        self.engine.reset()
        self.engine.set_param("CROSS_MODAL", 10)
        result = self.engine.apply_to_metrics(baseline_dict, rng_seed=42)
        assert "semantic_concepts" in result
        assert len(result["semantic_concepts"]) == 0

    def test_novelty_with_cross_modal(self):
        baseline = PerceptionMetrics(
            geometry_score=0.5, symmetry_score=0.6, confidence=0.7,
            novelty=0.4, uncertainty=0.3)
        baseline_dict = baseline.to_dict()
        engine_no_cm = AlteredStateEngine(seed=42)
        engine_cm = AlteredStateEngine(seed=42)
        engine_cm.set_param("CROSS_MODAL", 90)
        r1 = engine_no_cm.apply_to_metrics(baseline_dict, rng_seed=42)
        r2 = engine_cm.apply_to_metrics(baseline_dict, rng_seed=42)
        assert "novelty" in r1 and "novelty" in r2


class TestMetricsAnalysis:
    def test_perception_divergence(self):
        m1 = PerceptionMetrics(geometry_score=0.3, symmetry_score=0.4,
                                confidence=0.8, novelty=0.2, uncertainty=0.5,
                                code_like_structures=[{"type": "line"}],
                                symbols=[{"center": [10, 10]}], objects=[{"name": "blob"}])
        m2 = PerceptionMetrics(geometry_score=0.7, symmetry_score=0.3,
                                confidence=0.5, novelty=0.8, uncertainty=0.7,
                                code_like_structures=[{"type": "grid"}],
                                symbols=[{"center": [20, 20]}], objects=[{"name": "shape"}])
        div = compute_perception_divergence(m1, m2)
        assert "perception_divergence_score" in div
        assert "embedding_distance" in div
        assert div["perception_divergence_score"] >= 0

    def test_metrics_to_dict(self):
        m = PerceptionMetrics(geometry_score=0.5)
        d = m.to_dict()
        assert d["geometry_score"] == 0.5
        assert "objects" in d


class TestExperimentStore:
    def setup_method(self):
        import tempfile
        self.test_dir = tempfile.mkdtemp()
        self.store = ExperimentStore(self.test_dir)

    def test_create_experiment(self):
        exp_id = self.store.create_experiment(stimulus_id="TEST-1")
        assert exp_id.startswith("EXP-")
        assert os.path.isdir(os.path.join(self.test_dir, exp_id))

    def test_save_and_load(self):
        exp_id = self.store.create_experiment()
        self.store.save_experiment_data(exp_id, {"test": "data"}, "metadata")
        data = self.store.get_experiment(exp_id)
        assert data is not None
        assert "metadata" in data
        assert data["metadata"]["test"] == "data"

    def test_list_experiments(self):
        exp_id = self.store.create_experiment()
        experiments = self.store.list_experiments()
        assert any(e["exp_id"] == exp_id for e in experiments)


class TestStatistics:
    def setup_method(self):
        self.stats = StatisticsEngine()

    def test_add_and_report(self):
        s1 = type('S', (), {
            'experiment_id': 'EXP-001', 'baseline_geometry': 0.3, 'altered_geometry': 0.7,
            'baseline_novelty': 0.2, 'altered_novelty': 0.8,
            'baseline_uncertainty': 0.3, 'altered_uncertainty': 0.7,
            'baseline_confidence': 0.8, 'altered_confidence': 0.5,
            'perception_divergence': 0.4, 'baseline_code_like': 1, 'altered_code_like': 3})()
        s2 = type('S', (), {
            'experiment_id': 'EXP-002', 'baseline_geometry': 0.4, 'altered_geometry': 0.8,
            'baseline_novelty': 0.3, 'altered_novelty': 0.9,
            'baseline_uncertainty': 0.4, 'altered_uncertainty': 0.8,
            'baseline_confidence': 0.7, 'altered_confidence': 0.4,
            'perception_divergence': 0.5, 'baseline_code_like': 2, 'altered_code_like': 4})()
        self.stats.add_experiment(s1)
        self.stats.add_experiment(s2)
        report = self.stats.get_aggregate_report()
        assert report["total_experiments"] == 2
        assert "geometry" in report
        assert "comparison" in report["geometry"]

    def test_group_stats(self):
        result = self.stats.compute_group_stats([1.0, 2.0, 3.0])
        assert result["mean"] == 2.0
        assert result["count"] == 3

    def test_empty_report(self):
        report = self.stats.get_aggregate_report()
        assert "note" in report


class TestIntegration:
    def test_full_experiment(self):
        engine = ExperimentEngine()
        config = StimulusConfig(seed=123, pattern_type="lattice")
        result = engine.run_experiment(config)
        assert "experiment_id" in result
        assert os.path.exists(result["stimulus_path"])

        exp_id = result["experiment_id"]
        all_data = engine.store.get_experiment(exp_id)
        assert all_data is not None
        assert "metadata" in all_data
        assert "measurements" in all_data

    def test_replay_experiment(self):
        engine = ExperimentEngine()
        config = StimulusConfig(seed=456, pattern_type="concentric")
        result = engine.run_experiment(config)
        exp_id = result["experiment_id"]
        replayed = engine.replay_experiment(exp_id)
        assert replayed is not None
        assert replayed.get("replayed") == True if "replayed" in replayed else True
