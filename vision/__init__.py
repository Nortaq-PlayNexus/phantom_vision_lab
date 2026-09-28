import numpy as np
from PIL import Image
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import math


@dataclass
class VisionResult:
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


class VisionModelProvider:
    def __init__(self, model_name: str = "phantom-vision-local"):
        self.model_name = model_name
        self.model_version = "0.1.0"

    def analyze(self, image: np.ndarray) -> VisionResult:
        return analyze_image_cv(image)


def analyze_image_cv(image: np.ndarray) -> VisionResult:
    img = np.array(image)
    if len(img.shape) == 2:
        img = np.stack([img] * 3, axis=-1)
    if img.shape[2] == 4:
        img = img[:, :, :3]

    H, W = img.shape[:2]
    result = VisionResult()

    gray = np.mean(img, axis=2).astype(np.float64)

    result.objects = _detect_objects(gray, H, W)
    result.patterns = _detect_patterns(gray, H, W)
    result.geometry_score = _compute_geometry(gray, H, W)
    result.symmetry_score = _compute_symmetry(gray, H, W)
    result.color_palette = _extract_colors(img, H, W)
    result.spatial_relationships = _spatial_relations(gray, H, W)
    result.text_like_structures = _detect_text_like(gray, H, W)
    result.symbols = _detect_symbols(gray, H, W)
    result.code_like_structures = _detect_code_like(gray, H, W)
    result.semantic_concepts = _infer_semantics(result)
    result.confidence = _compute_confidence(result)
    result.novelty = _compute_novelty(result, gray)
    result.uncertainty = _compute_uncertainty(result)

    return result


def _detect_objects(gray, H, W) -> List[Dict]:
    from scipy import ndimage
    threshold = np.mean(gray) * 0.8
    binary = gray > threshold
    labeled, num = ndimage.label(binary)
    objects = []
    for i in range(1, min(num + 1, 20)):
        coords = np.where(labeled == i)
        if len(coords[0]) < 10:
            continue
        y_min, y_max = coords[0].min(), coords[0].max()
        x_min, x_max = coords[1].min(), coords[1].max()
        objects.append({
            "id": i,
            "bbox": [int(x_min), int(y_min), int(x_max), int(y_max)],
            "area": int(len(coords[0])),
            "center": [int(np.mean(coords[1])), int(np.mean(coords[0]))],
            "type": "blob" if len(coords[0]) > 100 else "small_feature",
        })
    return objects


def _detect_patterns(gray, H, W) -> List[Dict]:
    from scipy import ndimage
    patterns = []
    h_freq = np.abs(np.fft.fft2(gray - np.mean(gray)))
    h_shift = np.fft.fftshift(h_freq)
    center_y, center_x = H // 2, W // 2

    angles = np.linspace(0, 2 * np.pi, 36, endpoint=False)
    for i, angle in enumerate(angles):
        dx = int(50 * np.cos(angle))
        dy = int(50 * np.sin(angle))
        y0 = max(0, min(center_y + dy - 5, H - 10))
        x0 = max(0, min(center_x + dx - 5, W - 10))
        patch = h_shift[y0:y0+10, x0:x0+10]
        if patch.size > 0:
            patterns.append({
                "angle": round(angle, 3),
                "frequency_magnitude": float(patch.mean()),
            })

    horizontal = ndimage.gaussian_filter1d(gray, sigma=2, order=0, axis=0)
    vertical = ndimage.gaussian_filter1d(gray, sigma=2, order=0, axis=1)
    h_var = float(np.var(horizontal))
    v_var = float(np.var(vertical))
    patterns.append({"type": "horizontal_variance", "value": h_var})
    patterns.append({"type": "vertical_variance", "value": v_var})
    return patterns


def _compute_geometry(gray, H, W) -> float:
    from scipy import ndimage
    edges = np.abs(ndimage.gaussian_filter(gray, sigma=1, order=1))
    edge_density = float(np.mean(edges > np.mean(edges)))
    symmetry = _compute_symmetry(gray, H, W)
    uniformity = 1.0 - float(np.std(gray) / (np.mean(gray) + 1e-6))
    return float(np.clip(edge_density * 2 + symmetry * 0.5 + uniformity * 0.3, 0, 1))


def _compute_symmetry(gray, H, W) -> float:
    left = gray[:, :W//2]
    right = np.fliplr(gray[:, W//2:2*(W//2)])
    min_w = min(left.shape[1], right.shape[1])
    left = left[:, :min_w]
    right = right[:, :min_w]
    diff = np.mean(np.abs(left - right))
    max_diff = 255.0
    return float(1.0 - diff / max_diff)


def _extract_colors(img, H, W) -> List[Tuple[int, int, int]]:
    pixels = img.reshape(-1, 3).astype(np.float64)
    colors = []
    try:
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=5, n_init=10, random_state=42)
        kmeans.fit(pixels)
        colors = [tuple(int(c) for c in center) for center in kmeans.cluster_centers_]
    except Exception:
        step = max(1, H * W // 1000)
        sampled = pixels[::step]
        for i in range(5):
            idx = (i * len(sampled)) // 5
            if idx < len(sampled):
                colors.append(tuple(int(c) for c in sampled[idx]))
    return colors[:5]


def _spatial_relations(gray, H, W) -> List[Dict]:
    return [
        {"relation": "center_density", "value": float(np.mean(gray[H//3:2*H//3, W//3:2*W//3]))},
        {"relation": "edge_density", "value": float(np.mean(np.abs(np.diff(gray, axis=0))))},
        {"relation": "vertical_gradient", "value": float(np.mean(np.abs(np.diff(gray, axis=0))))},
        {"relation": "horizontal_gradient", "value": float(np.mean(np.abs(np.diff(gray, axis=1))))},
    ]


def _detect_text_like(gray, H, W) -> List[Dict]:
    structures = []
    from scipy import ndimage
    binary = gray < np.mean(gray) * 0.7
    labeled, num = ndimage.label(binary)
    for i in range(1, min(num + 1, 50)):
        coords = np.where(labeled == i)
        if len(coords[0]) < 3:
            continue
        aspect = max(coords[1]) - min(coords[1]) + 1
        yspan = max(coords[0]) - min(coords[0]) + 1
        if aspect > 0:
            ratio = yspan / aspect
            if 0.5 < ratio < 6.0 and 2 < yspan < 30 and 2 < aspect < 50:
                structures.append({
                    "bbox": [int(min(coords[1])), int(min(coords[0])),
                             int(max(coords[1])), int(max(coords[0]))],
                    "aspect_ratio": round(ratio, 3),
                    "size": [yspan, aspect],
                })
    return structures


def _detect_symbols(gray, H, W) -> List[Dict]:
    from scipy import ndimage
    symbols = []
    edges = np.abs(ndimage.gaussian_filter(gray, sigma=1, order=1))
    threshold = np.mean(edges) * 1.2
    binary = edges > threshold
    labeled, num = ndimage.label(binary)
    for i in range(1, min(num + 1, 30)):
        coords = np.where(labeled == i)
        if len(coords[0]) < 5:
            continue
        cx = float(np.mean(coords[1]))
        cy = float(np.mean(coords[0]))
        dist = math.sqrt((cx - W/2)**2 + (cy - H/2)**2)
        symbols.append({
            "center": [int(cx), int(cy)],
            "distance_from_center": round(dist, 2),
            "area": int(len(coords[0])),
        })
    return symbols


def _detect_code_like(gray, H, W) -> List[Dict]:
    from scipy import ndimage
    structures = []
    binary = gray < np.mean(gray) * 0.6
    binary = ndimage.binary_opening(binary, iterations=1)
    horizontal = ndimage.gaussian_filter1d(binary.astype(float), sigma=1, axis=1)
    vertical = ndimage.gaussian_filter1d(binary.astype(float), sigma=1, axis=0)

    for y in range(0, H, max(1, H // 20)):
        row = binary[y, :] if y < H else None
        if row is not None:
            count = int(np.sum(row))
            if count > W * 0.1:
                structures.append({
                    "type": "horizontal_line",
                    "y": int(y),
                    "length": int(count),
                })

    segments = []
    for x in range(0, W, max(1, W // 30)):
        col = binary[:, x] if x < W else None
        if col is not None:
            count = int(np.sum(col))
            if count > H * 0.1:
                segments.append({"type": "vertical_line", "x": int(x), "length": int(count)})

    structures.extend(segments[:10])
    return structures


def _infer_semantics(result: VisionResult) -> List[str]:
    concepts = []
    if result.geometry_score > 0.5:
        concepts.append("geometric_structure")
    if result.symmetry_score > 0.5:
        concepts.append("symmetric_pattern")
    if len(result.code_like_structures) > 3:
        concepts.append("structured_arrangement")
    if result.novelty > 0.5:
        concepts.append("novel_visual_feature")
    if len(result.objects) > 5:
        concepts.append("multi_object_scene")
    if result.uncertainty > 0.5:
        concepts.append("ambiguous_interpretation")
    if len(result.text_like_structures) > 2:
        concepts.append("text_like_organization")
    return concepts


def _compute_confidence(result: VisionResult) -> float:
    base = 0.5
    if result.objects:
        base += 0.1 * min(len(result.objects), 10) / 10
    if result.patterns:
        base += 0.05 * min(len(result.patterns), 10) / 10
    base += result.geometry_score * 0.1
    base -= result.uncertainty * 0.2
    return float(np.clip(base, 0, 1))


def _compute_novelty(result: VisionResult, gray) -> float:
    entropy = float(-np.sum((np.histogram(gray, bins=32)[0] / gray.size) *
                            np.log2((np.histogram(gray, bins=32)[0] / gray.size) + 1e-10)))
    norm = entropy / 8.0
    feature_count = len(result.objects) + len(result.code_like_structures) + len(result.symbols)
    return float(np.clip(norm * 0.5 + feature_count * 0.02, 0, 1))


def _compute_uncertainty(result: VisionResult) -> float:
    diversity = 0.0
    if result.objects:
        areas = [o["area"] for o in result.objects]
        diversity = float(np.std(areas) / (np.mean(areas) + 1e-6))
    uncertainty = float(np.clip(0.3 + diversity * 0.2 - result.confidence * 0.15, 0, 1))
    return uncertainty


__all__ = ["VisionModelProvider", "analyze_image_cv", "VisionResult"]
