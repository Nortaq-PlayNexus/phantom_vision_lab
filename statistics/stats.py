import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from scipy import stats as scipy_stats


@dataclass
class ExperimentSummary:
    experiment_id: str
    baseline_geometry: float = 0.0
    altered_geometry: float = 0.0
    baseline_novelty: float = 0.0
    altered_novelty: float = 0.0
    baseline_uncertainty: float = 0.0
    altered_uncertainty: float = 0.0
    baseline_confidence: float = 0.0
    altered_confidence: float = 0.0
    perception_divergence: float = 0.0
    baseline_code_like: int = 0
    altered_code_like: int = 0


class StatisticsEngine:
    def __init__(self):
        self.experiments: List[ExperimentSummary] = []

    def add_experiment(self, summary: ExperimentSummary):
        self.experiments.append(summary)

    def compute_group_stats(self, values: List[float]) -> Dict[str, float]:
        arr = np.array(values)
        if len(arr) == 0:
            return {"mean": 0, "median": 0, "std": 0, "min": 0, "max": 0, "count": 0}
        return {
            "mean": float(np.mean(arr)),
            "median": float(np.median(arr)),
            "std": float(np.std(arr, ddof=1) if len(arr) > 1 else 0.0),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "count": len(arr),
        }

    def compute_confidence_interval(self, values: List[float], confidence: float = 0.95) -> Dict[str, float]:
        arr = np.array(values)
        if len(arr) < 2:
            return {"lower": 0, "upper": 0, "mean": float(np.mean(arr)) if len(arr) == 1 else 0}
        se = scipy_stats.sem(arr)
        ci = scipy_stats.t.interval(confidence, len(arr) - 1, loc=np.mean(arr), scale=se)
        return {"lower": float(ci[0]), "upper": float(ci[1]), "mean": float(np.mean(arr))}

    def compare_groups(self, group_a: List[float], group_b: List[float]) -> Dict[str, Any]:
        arr_a = np.array(group_a)
        arr_b = np.array(group_b)
        if len(arr_a) < 2 or len(arr_b) < 2:
            return {"t_statistic": 0, "p_value": 1.0, "effect_size": 0, "significant": False, "note": "Insufficient data for comparison"}
        t_stat, p_val = scipy_stats.ttest_ind(arr_a, arr_b)
        pooled_std = np.sqrt((np.std(arr_a, ddof=1) ** 2 + np.std(arr_b, ddof=1) ** 2) / 2)
        effect_size = (np.mean(arr_a) - np.mean(arr_b)) / pooled_std if pooled_std > 0 else 0
        return {
            "t_statistic": float(t_stat),
            "p_value": float(p_val),
            "effect_size": float(effect_size),
            "significant": bool(p_val < 0.05),
            "note": "Effect size is Cohen's d. |d| > 0.8 is large, > 0.5 medium, > 0.2 small."
        }

    def get_aggregate_report(self) -> Dict[str, Any]:
        if not self.experiments:
            return {"note": "No experiments recorded yet."}

        geom_baseline = [e.baseline_geometry for e in self.experiments]
        geom_altered = [e.altered_geometry for e in self.experiments]
        nov_baseline = [e.baseline_novelty for e in self.experiments]
        nov_altered = [e.altered_novelty for e in self.experiments]
        unc_baseline = [e.baseline_uncertainty for e in self.experiments]
        unc_altered = [e.altered_uncertainty for e in self.experiments]
        conf_baseline = [e.baseline_confidence for e in self.experiments]
        conf_altered = [e.altered_confidence for e in self.experiments]
        divergence = [e.perception_divergence for e in self.experiments]
        code_baseline = [e.baseline_code_like for e in self.experiments]
        code_altered = [e.altered_code_like for e in self.experiments]

        return {
            "total_experiments": len(self.experiments),
            "geometry": {
                "baseline": self.compute_group_stats(geom_baseline),
                "altered": self.compute_group_stats(geom_altered),
                "comparison": self.compare_groups(geom_baseline, geom_altered),
            },
            "novelty": {
                "baseline": self.compute_group_stats(nov_baseline),
                "altered": self.compute_group_stats(nov_altered),
                "comparison": self.compare_groups(nov_baseline, nov_altered),
            },
            "uncertainty": {
                "baseline": self.compute_group_stats(unc_baseline),
                "altered": self.compute_group_stats(unc_altered),
                "comparison": self.compare_groups(unc_baseline, unc_altered),
            },
            "confidence": {
                "baseline": self.compute_group_stats(conf_baseline),
                "altered": self.compute_group_stats(conf_altered),
                "comparison": self.compare_groups(conf_baseline, conf_altered),
            },
            "perception_divergence": {
                "stats": self.compute_group_stats(divergence),
                "ci": self.compute_confidence_interval(divergence),
            },
            "code_like_count": {
                "baseline": self.compute_group_stats(code_baseline),
                "altered": self.compute_group_stats(code_altered),
                "comparison": self.compare_groups(code_baseline, code_altered),
            },
        }
