import os
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class PerceptionReport:
    experiment_id: str = ""
    timestamp: str = ""
    model: str = ""
    model_version: str = ""
    stimulus_id: str = ""
    random_seed: int = 0
    what_model_saw: str = ""
    what_model_described: str = ""
    patterns_detected: List[str] = field(default_factory=list)
    symbolic_structures: List[str] = field(default_factory=list)
    code_like_structures: List[str] = field(default_factory=list)
    confidence: float = 0.0
    altered_difference: float = 0.0
    changes_from_baseline: List[str] = field(default_factory=list)
    scientific_interpretation: str = ""
    perception_divergence_score: float = 0.0
    baseline_metrics: Dict[str, Any] = field(default_factory=dict)
    altered_metrics: Dict[str, Any] = field(default_factory=dict)
    measurements: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "timestamp": self.timestamp,
            "model": self.model,
            "model_version": self.model_version,
            "stimulus_id": self.stimulus_id,
            "random_seed": self.random_seed,
            "what_model_saw": self.what_model_saw,
            "what_model_described": self.what_model_described,
            "patterns_detected": self.patterns_detected,
            "symbolic_structures": self.symbolic_structures,
            "code_like_structures": self.code_like_structures,
            "confidence": self.confidence,
            "altered_difference": self.altered_difference,
            "changes_from_baseline": self.changes_from_baseline,
            "scientific_interpretation": self.scientific_interpretation,
            "perception_divergence_score": self.perception_divergence_score,
            "baseline_metrics": self.baseline_metrics,
            "altered_metrics": self.altered_metrics,
            "measurements": self.measurements,
        }


class ReportGenerator:
    def generate(self, experiment_id: str, baseline: Dict, altered: Dict,
                 divergence: Dict, measurements: Dict) -> PerceptionReport:
        baseline_metrics = baseline.get("metrics", baseline) if isinstance(baseline, dict) else {}
        altered_metrics = altered.get("metrics", altered) if isinstance(altered, dict) else {}

        what_saw = self._describe_observations(baseline_metrics)
        what_described = self._describe_interpretation(altered_metrics)
        patterns = self._extract_patterns(baseline_metrics, altered_metrics)
        symbols = self._extract_symbols(altered_metrics)
        code_structures = self._extract_code(altered_metrics)
        changes = self._compute_changes(baseline_metrics, altered_metrics, divergence)
        interpretation = self._scientific_interpretation(divergence, altered_metrics)

        return PerceptionReport(
            experiment_id=experiment_id,
            timestamp=measurements.get("timestamp", ""),
            model=measurements.get("model", ""),
            model_version=measurements.get("model_version", ""),
            stimulus_id=str(measurements.get("stimulus_metadata", {}).get("seed", "")),
            random_seed=measurements.get("random_seed", 0),
            what_model_saw=what_saw,
            what_model_described=what_described,
            patterns_detected=patterns,
            symbolic_structures=symbols,
            code_like_structures=code_structures,
            confidence=float(altered_metrics.get("confidence", 0)),
            altered_difference=float(divergence.get("perception_divergence_score", 0)),
            changes_from_baseline=changes,
            scientific_interpretation=interpretation,
            perception_divergence_score=float(divergence.get("perception_divergence_score", 0)),
            baseline_metrics=baseline_metrics,
            altered_metrics=altered_metrics,
            measurements=measurements,
        )

    def _describe_observations(self, metrics: Dict) -> str:
        obj_count = len(metrics.get("objects", []))
        pat_count = len(metrics.get("patterns", []))
        geo = metrics.get("geometry_score", 0)
        sym = metrics.get("symmetry_score", 0)
        conf = metrics.get("confidence", 0)
        parts = []
        parts.append(f"The system detected {obj_count} distinct objects and {pat_count} pattern categories.")
        if geo > 0.5:
            parts.append("Strong geometric structure was observed.")
        elif geo > 0.2:
            parts.append("Moderate geometric structure was detected.")
        else:
            parts.append("Minimal geometric structure was observed.")
        if sym > 0.5:
            parts.append("The stimulus exhibited notable symmetry properties.")
        return " ".join(parts)

    def _describe_interpretation(self, metrics: Dict) -> str:
        concepts = metrics.get("semantic_concepts", [])
        conf = metrics.get("confidence", 0)
        unc = metrics.get("uncertainty", 0)
        parts = []
        if concepts:
            parts.append(f"Interpretation included: {', '.join(concepts)}.")
        parts.append(f"Confidence level: {conf:.1%}.")
        if unc > 0.5:
            parts.append("High uncertainty suggests ambiguous interpretation.")
        return " ".join(parts)

    def _extract_patterns(self, baseline: Dict, altered: Dict) -> List[str]:
        patterns = set()
        for m in [baseline, altered]:
            for p in m.get("patterns", []):
                if isinstance(p, dict):
                    for k, v in p.items():
                        if k != "angle" and v and str(v) != "0.0":
                            patterns.add(str(v)[:50])
        return list(patterns)[:20]

    def _extract_symbols(self, metrics: Dict) -> List[str]:
        symbols = []
        for s in metrics.get("symbols", []):
            if isinstance(s, dict):
                symbols.append(f"symbol_at_{s.get('center', 'unknown')}_area_{s.get('area', 0)}")
        return symbols[:10]

    def _extract_code(self, metrics: Dict) -> List[str]:
        structures = []
        for c in metrics.get("code_like_structures", []):
            if isinstance(c, dict):
                structures.append(f"{c.get('type', 'unknown')}_{c.get('y', c.get('x', ''))}")
        return structures[:10]

    def _compute_changes(self, baseline: Dict, altered: Dict, divergence: Dict) -> List[str]:
        changes = []
        b_geo = baseline.get("geometry_score", 0)
        a_geo = altered.get("geometry_score", 0)
        if abs(a_geo - b_geo) > 0.1:
            direction = "increased" if a_geo > b_geo else "decreased"
            changes.append(f"Geometry score {direction} by {abs(a_geo - b_geo):.3f}")
        b_nov = baseline.get("novelty", 0)
        a_nov = altered.get("novelty", 0)
        if abs(a_nov - b_nov) > 0.1:
            direction = "increased" if a_nov > b_nov else "decreased"
            changes.append(f"Novelty {direction} by {abs(a_nov - b_nov):.3f}")
        b_con = baseline.get("confidence", 0)
        a_con = altered.get("confidence", 0)
        if abs(a_con - b_con) > 0.1:
            direction = "increased" if a_con > b_con else "decreased"
            changes.append(f"Confidence {direction} by {abs(a_con - b_con):.3f}")
        b_unc = baseline.get("uncertainty", 0)
        a_unc = altered.get("uncertainty", 0)
        if abs(a_unc - b_unc) > 0.1:
            direction = "increased" if a_unc > b_unc else "decreased"
            changes.append(f"Uncertainty {direction} by {abs(a_unc - b_unc):.3f}")
        return changes[:10]

    def _scientific_interpretation(self, divergence: Dict, altered: Dict) -> str:
        pds = divergence.get("perception_divergence_score", 0)
        geo_diff = divergence.get("geometry_diff", 0)
        nov_diff = divergence.get("novelty_diff", 0)
        parts = []
        parts.append("The altered computational configuration produced measurable changes in the model's visual interpretation.")
        if pds > 0.3:
            parts.append(f"The perception divergence score of {pds:.3f} indicates a significant shift in interpretation.")
        elif pds > 0.1:
            parts.append(f"The perception divergence score of {pds:.3f} indicates a moderate shift in interpretation.")
        else:
            parts.append(f"The perception divergence score of {pds:.3f} indicates minimal shift from baseline.")
        if geo_diff > 0.1:
            parts.append(f"Geometry detection changed by {geo_diff:.3f}.")
        if nov_diff > 0.1:
            parts.append(f"Novelty assessment changed by {nov_diff:.3f}.")
        parts.append("These results are consistent with controlled computational perturbation effects on AI perception pipelines.")
        return " ".join(parts)
