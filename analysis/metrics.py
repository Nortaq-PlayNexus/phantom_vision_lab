import numpy as np
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field


@dataclass
class PerceptionMetrics:
    objects: List[Dict[str, Any]] = field(default_factory=list)
    patterns: List[Dict[str, Any]] = field(default_factory=list)
    geometry_score: float = 0.0
    symmetry_score: float = 0.0
    color_palette: List[Tuple[int, int, int]] = field(default_factory=list)
    spatial_relationships: List[Dict[str, Any]] = field(default_factory=list)
    text_like_structures: List[Dict[str, Any]] = field(default_factory=list)
    symbols: List[Dict[str, Any]] = field(default_factory=list)
    code_like_structures: List[Dict[str, Any]] = field(default_factory=list)
    semantic_concepts: List[str] = field(default_factory=list)
    confidence: float = 0.0
    novelty: float = 0.0
    uncertainty: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "objects": self.objects,
            "patterns": self.patterns,
            "geometry_score": round(self.geometry_score, 4),
            "symmetry_score": round(self.symmetry_score, 4),
            "color_palette": [list(c) for c in self.color_palette],
            "spatial_relationships": self.spatial_relationships,
            "text_like_structures": self.text_like_structures,
            "symbols": self.symbols,
            "code_like_structures": self.code_like_structures,
            "semantic_concepts": self.semantic_concepts,
            "confidence": round(self.confidence, 4),
            "novelty": round(self.novelty, 4),
            "uncertainty": round(self.uncertainty, 4),
        }


def compute_embedding_distance(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    if len(vec_a) != len(vec_b):
        min_len = min(len(vec_a), len(vec_b))
        vec_a = vec_a[:min_len]
        vec_b = vec_b[:min_len]
    return float(np.linalg.norm(vec_a - vec_b))


def compute_perception_divergence(baseline: PerceptionMetrics, altered: PerceptionMetrics) -> Dict[str, float]:
    scores = {}
    scores["geometry_diff"] = abs(altered.geometry_score - baseline.geometry_score)
    scores["symmetry_diff"] = abs(altered.symmetry_score - baseline.symmetry_score)
    scores["confidence_diff"] = abs(altered.confidence - baseline.confidence)
    scores["novelty_diff"] = abs(altered.novelty - baseline.novelty)
    scores["uncertainty_diff"] = abs(altered.uncertainty - baseline.uncertainty)

    baseline_vec = np.array([
        baseline.geometry_score, baseline.symmetry_score, baseline.confidence,
        baseline.novelty, baseline.uncertainty, float(len(baseline.code_like_structures)),
        float(len(baseline.symbols)), float(len(baseline.objects)),
    ])
    altered_vec = np.array([
        altered.geometry_score, altered.symmetry_score, altered.confidence,
        altered.novelty, altered.uncertainty, float(len(altered.code_like_structures)),
        float(len(altered.symbols)), float(len(altered.objects)),
    ])
    scores["embedding_distance"] = compute_embedding_distance(baseline_vec, altered_vec)

    baseline_desc = " ".join([
        *[o.get("name", "") for o in baseline.objects],
        *[p.get("type", "") for p in baseline.patterns],
        " ".join(baseline.semantic_concepts),
    ]).lower()
    altered_desc = " ".join([
        *[o.get("name", "") for o in altered.objects],
        *[p.get("type", "") for p in altered.patterns],
        " ".join(altered.semantic_concepts),
    ]).lower()
    if not baseline_desc or not altered_desc:
        scores["description_similarity"] = 0.0
    else:
        words_a = set(baseline_desc.split())
        words_b = set(altered_desc.split())
        if not words_a or not words_b:
            scores["description_similarity"] = 0.0
        else:
            scores["description_similarity"] = len(words_a & words_b) / len(words_a | words_b)

    max_d = max(1.0, scores["embedding_distance"])
    scores["perception_divergence_score"] = min(1.0, (scores["geometry_diff"] + scores["novelty_diff"] + scores["uncertainty_diff"]) / (3.0 * max_d))

    return {k: round(v, 6) for k, v in scores.items()}
