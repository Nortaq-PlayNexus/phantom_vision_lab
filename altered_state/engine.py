from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class AlteredParam:
    name: str
    display_name: str
    value: float = 50.0
    default: float = 50.0
    explanation: str = ""
    experimental_preset: float = 70.0


class AlteredStateEngine:
    PARAMS: List[AlteredParam] = [
        AlteredParam("SENSORY_GAIN", "Sensory Gain", explanation="Controls strength of incoming visual features"),
        AlteredParam("PRIOR_WEIGHT", "Prior Weight", explanation="Controls influence of previously learned/expected interpretations"),
        AlteredParam("PREDICTION_ERROR", "Prediction Error", explanation="Amplifies differences between expected and observed representations"),
        AlteredParam("CROSS_MODAL", "Cross-Modal Association", explanation="Allows visual representations to trigger semantic/audio/language associations"),
        AlteredParam("REPRESENTATION_DRIFT", "Representation Drift", explanation="Introduces controlled transformations of intermediate representations"),
        AlteredParam("TEMPORAL_INSTABILITY", "Temporal Instability", explanation="Changes how rapidly internal interpretations update"),
        AlteredParam("RECURSIVE_ATTENTION", "Recursive Attention", explanation="Allows representations to repeatedly influence subsequent interpretation"),
        AlteredParam("PATTERN_AMPLIFICATION", "Pattern Amplification", explanation="Amplifies repeating structures and symmetries"),
        AlteredParam("NOVELTY_GAIN", "Novelty Gain", explanation="Increases attention toward unusual features"),
        AlteredParam("SEMANTIC_LOOSE", "Semantic Loose Association", explanation="Allows less-constrained conceptual associations"),
    ]

    PRESETS: Dict[str, Dict[str, float]] = {
        "BASELINE": {p.name: p.default for p in PARAMS},
        "LOW PERTURBATION": {p.name: 20.0 for p in PARAMS},
        "HIGH SENSORY GAIN": {p.name: 50.0 for p in PARAMS},
        "HIGH PREDICTION ERROR": {p.name: 50.0 for p in PARAMS},
        "PATTERN AMPLIFICATION": {p.name: 50.0 for p in PARAMS},
        "MAXIMUM EXPLORATION": {p.name: 80.0 for p in PARAMS},
    }

    PRESETS["HIGH SENSORY GAIN"]["SENSORY_GAIN"] = 95.0
    PRESETS["HIGH SENSORY GAIN"]["PRIOR_WEIGHT"] = 30.0
    PRESETS["HIGH PREDICTION ERROR"]["PREDICTION_ERROR"] = 90.0
    PRESETS["HIGH PREDICTION ERROR"]["PRIOR_WEIGHT"] = 20.0
    PRESETS["PATTERN AMPLIFICATION"]["PATTERN_AMPLIFICATION"] = 95.0
    PRESETS["MAXIMUM EXPLORATION"]["NOVELTY_GAIN"] = 95.0
    PRESETS["MAXIMUM EXPLORATION"]["SEMANTIC_LOOSE"] = 90.0

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.params: Dict[str, AlteredParam] = {}
        for p in self.PARAMS:
            self.params[p.name] = AlteredParam(
                name=p.name, display_name=p.display_name,
                default=p.default, value=p.default,
                explanation=p.explanation, experimental_preset=p.experimental_preset,
            )

    def set_param(self, name: str, value: float):
        if name in self.params:
            self.params[name].value = max(0.0, min(100.0, value))

    def get_param(self, name: str) -> float:
        return self.params.get(name, AlteredParam(name, name)).value

    def reset(self):
        for p in self.PARAMS:
            self.params[p.name].value = p.default

    def apply_preset(self, preset_name: str):
        if preset_name in self.PRESETS:
            for p in self.PARAMS:
                if p.name in self.PRESETS[preset_name]:
                    self.params[p.name].value = self.PRESETS[preset_name][p.name]

    def randomize(self, seed: int = None):
        import random
        s = seed if seed is not None else self.seed
        rng = random.Random(s)
        for p in self.PARAMS:
            self.params[p.name].value = rng.uniform(0, 100)

    def to_dict(self) -> Dict[str, float]:
        return {p.name: p.value for p in self.PARAMS}

    def apply_to_metrics(self, baseline_metrics: Dict[str, float], rng_seed: int = None) -> Dict[str, float]:
        import random
        import numpy as np
        rng = random.Random(rng_seed if rng_seed is not None else self.seed)
        rng2 = np.random.RandomState(rng_seed if rng_seed is not None else self.seed)

        result = dict(baseline_metrics)
        sg = self.params["SENSORY_GAIN"].value / 50.0
        pw = self.params["PRIOR_WEIGHT"].value / 100.0
        pe = self.params["PREDICTION_ERROR"].value / 100.0
        pa = self.params["PATTERN_AMPLIFICATION"].value / 100.0
        ng = self.params["NOVELTY_GAIN"].value / 100.0
        rd = self.params["REPRESENTATION_DRIFT"].value / 100.0
        ti = self.params["TEMPORAL_INSTABILITY"].value / 100.0
        ra = self.params["RECURSIVE_ATTENTION"].value / 100.0
        cm = self.params["CROSS_MODAL"].value / 100.0

        if "geometry_score" in result:
            result["geometry_score"] = min(1.0, max(0.0,
                result["geometry_score"] * sg * (1.0 + pa * 0.5) + rng2.uniform(-rd * 0.1, rd * 0.1)))
            result["geometry_score"] = min(1.0, max(0.0, result["geometry_score"]))
        if "symmetry_score" in result:
            result["symmetry_score"] = min(1.0, max(0.0,
                result["symmetry_score"] * (1.0 + pa * 0.3) + rng2.uniform(-rd * 0.05, rd * 0.05)))
            result["symmetry_score"] = min(1.0, max(0.0, result["symmetry_score"]))
        if "confidence" in result:
            result["confidence"] = min(1.0, max(0.0,
                result["confidence"] * (1.0 - pe * 0.3) * (1.0 - pw * 0.2)))
            result["confidence"] = min(1.0, max(0.0, result["confidence"]))
        if "novelty" in result:
            result["novelty"] = min(1.0, max(0.0,
                result["novelty"] * (1.0 + ng * 0.5 + pe * 0.2 + cm * 0.15)))
            result["novelty"] = min(1.0, max(0.0, result["novelty"]))
        if "uncertainty" in result:
            result["uncertainty"] = min(1.0, max(0.0,
                result["uncertainty"] * (1.0 + pe * 0.4 + ti * 0.3) - ng * 0.1 + cm * 0.08))
            result["uncertainty"] = min(1.0, max(0.0, result["uncertainty"]))

        if "semantic_concepts" in result and cm > 0.2:
            cross_concepts = ["cross_modal_association", "synesthetic_binding", "conceptual_blending"]
            existing = result.get("semantic_concepts", [])
            for concept in cross_concepts:
                if concept not in existing and rng.random() < cm * 0.5:
                    existing.append(concept)
            result["semantic_concepts"] = existing

        if "objects" in result and cm > 0.3:
            for obj in result["objects"]:
                if rng.random() < cm * 0.3:
                    obj["cross_modal_tag"] = rng.choice(["auditory", "tactile", "spatial", "temporal"])

        if "spatial_relationships" in result and cm > 0.2:
            for rel in result["spatial_relationships"]:
                if rng.random() < cm * 0.4:
                    rel["cross_modal_strength"] = round(rng.uniform(0.1, 1.0), 3)

        return result
