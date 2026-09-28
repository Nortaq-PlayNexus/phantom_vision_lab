import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass, field
import os
import json


@dataclass
class StimulusConfig:
    seed: int = 42
    frequency: float = 0.05
    phase: float = 0.0
    rotation: float = 0.0
    symmetry: int = 6
    radial_distortion: float = 0.0
    wave_interference: float = 0.0
    contrast: float = 1.0
    brightness: float = 1.0
    scale: float = 1.0
    recursion_depth: int = 0
    noise: float = 0.0
    motion: float = 0.0
    warp: float = 0.0
    color_channels: str = "RGB"
    temporal_modulation: float = 0.0
    pattern_type: str = "lattice"
    size: Tuple[int, int] = (512, 512)


class StimulusGenerator:
    PATTERN_TYPES = [
        "lattice", "radial_diffraction", "interference", "concentric",
        "fractal", "kaleidoscopic", "rotating_grid", "warped_grid",
        "tunnel", "recursive_corridor", "polygons", "moire",
        "high_frequency", "interference_field", "noise_geometry", "morphing",
    ]

    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "experiments")
        self._cache: Dict[str, np.ndarray] = {}

    def generate(self, config: StimulusConfig) -> Tuple[np.ndarray, Dict[str, Any]]:
        rng = np.random.RandomState(config.seed)
        H, W = config.size

        pattern_type = config.pattern_type
        if pattern_type == "lattice":
            img = self._generate_lattice(W, H, config, rng)
        elif pattern_type == "radial_diffraction":
            img = self._generate_radial_diffraction(W, H, config, rng)
        elif pattern_type == "interference":
            img = self._generate_interference(W, H, config, rng)
        elif pattern_type == "concentric":
            img = self._generate_concentric(W, H, config, rng)
        elif pattern_type == "fractal":
            img = self._generate_fractal(W, H, config, rng)
        elif pattern_type == "kaleidoscopic":
            img = self._generate_kaleidoscopic(W, H, config, rng)
        elif pattern_type == "rotating_grid":
            img = self._generate_rotating_grid(W, H, config, rng)
        elif pattern_type == "warped_grid":
            img = self._generate_warped_grid(W, H, config, rng)
        elif pattern_type == "tunnel":
            img = self._generate_tunnel(W, H, config, rng)
        elif pattern_type == "recursive_corridor":
            img = self._generate_recursive_corridor(W, H, config, rng)
        elif pattern_type == "polygons":
            img = self._generate_polygons(W, H, config, rng)
        elif pattern_type == "moire":
            img = self._generate_moire(W, H, config, rng)
        elif pattern_type == "high_frequency":
            img = self._generate_high_frequency(W, H, config, rng)
        elif pattern_type == "interference_field":
            img = self._generate_interference_field(W, H, config, rng)
        elif pattern_type == "noise_geometry":
            img = self._generate_noise_geometry(W, H, config, rng)
        elif pattern_type == "morphing":
            img = self._generate_morphing(W, H, config, rng)
        else:
            img = self._generate_lattice(W, H, config, rng)

        img = np.clip(img * config.contrast * config.brightness, 0, 255).astype(np.uint8)

        if config.noise > 0:
            noise = rng.uniform(-config.noise * 50, config.noise * 50, (H, W, 3))
            img = np.clip(img.astype(float) + noise, 0, 255).astype(np.uint8)

        metadata = {
            "seed": config.seed,
            "pattern_type": pattern_type,
            "parameters": {
                "frequency": config.frequency, "phase": config.phase,
                "rotation": config.rotation, "symmetry": config.symmetry,
                "radial_distortion": config.radial_distortion,
                "wave_interference": config.wave_interference,
                "contrast": config.contrast, "brightness": config.brightness,
                "scale": config.scale, "recursion_depth": config.recursion_depth,
                "noise": config.noise, "warp": config.warp,
                "color_channels": config.color_channels,
            },
            "size": [W, H],
            "pattern_type": pattern_type,
        }

        return img, metadata

    def save(self, img: np.ndarray, metadata: Dict, filepath: str):
        Image.fromarray(img).save(filepath)
        mpath = filepath.rsplit(".", 1)[0] + "_meta.json"
        with open(mpath, "w") as f:
            json.dump(metadata, f, indent=2, default=str)

    def _generate_lattice(self, W, H, cfg, rng):
        img = np.zeros((H, W, 3), dtype=float)
        freq = cfg.frequency * 20
        for y in range(H):
            for x in range(W):
                v = np.sin(x * freq + cfg.phase) * np.cos(y * freq + cfg.phase)
                angle = np.arctan2(y - H/2, x - W/2)
                dist = np.sqrt((x - W/2)**2 + (y - H/2)**2)
                if cfg.radial_distortion > 0:
                    r_warp = dist * (1.0 + cfg.radial_distortion * 0.1)
                    angle2 = angle * (1.0 + cfg.radial_distortion * 0.05)
                    x2 = W/2 + r_warp * np.cos(angle2)
                    y2 = H/2 + r_warp * np.sin(angle2)
                    v2 = np.sin(x2 * freq + cfg.phase) * np.cos(y2 * freq + cfg.phase)
                    v = v * (1 - cfg.radial_distortion) + v2 * cfg.radial_distortion
                img[y, x] = [v * 128 + 128, v * 80 + 100, v * 160 + 60]
        if cfg.wave_interference > 0:
            wy = np.sin(np.indices((H, W))[0] * freq * 3) * cfg.wave_interference * 30
            wx = np.cos(np.indices((H, W))[1] * freq * 3) * cfg.wave_interference * 30
            img = np.clip(img + wy[:,:,None] + wx[:,:,None], 0, 255)
        return img

    def _generate_radial_diffraction(self, W, H, cfg, rng):
        img = np.zeros((H, W, 3), dtype=float)
        cx, cy = W // 2, H // 2
        Y, X = np.indices((H, W))
        dist = np.sqrt((X - cx)**2 + (Y - cy)**2)
        for i in range(cfg.symmetry):
            angle = i * 2 * np.pi / cfg.symmetry
            dx = np.cos(angle) * dist
            dy = np.sin(angle) * dist
            v = np.sin(dx * cfg.frequency * 30 + cfg.phase) * np.cos(dy * cfg.frequency * 30 + cfg.phase)
            img[:, :, i % 3] += v * 80
        img += 128
        if cfg.noise > 0:
            img += rng.uniform(-15, 15, img.shape)
        return img

    def _generate_interference(self, W, H, cfg, rng):
        Y, X = np.indices((H, W))
        img = np.zeros((H, W, 3), dtype=float)
        for i in range(3):
            freq = cfg.frequency * (10 + i * 5)
            v = (np.sin(X * freq + cfg.phase + i) + np.sin(Y * freq * 1.3 + cfg.phase + i)) / 2.0
            img[:, :, i] = v * 60 + 128
        if cfg.wave_interference > 0:
            wi = np.sin(np.sqrt((X - W/2)**2 + (Y - H/2)**2) * cfg.frequency * 20 * cfg.wave_interference)
            img += wi[:,:,None] * 40
        return img

    def _generate_concentric(self, W, H, cfg, rng):
        img = np.zeros((H, W, 3), dtype=float)
        cx, cy = W // 2, H // 2
        Y, X = np.indices((H, W))
        dist = np.sqrt((X - cx)**2 + (Y - cy)**2)
        freq = cfg.frequency * 30
        v = np.sin(dist * freq + cfg.phase)
        img[:,:,0] = v * 100 + 128
        img[:,:,1] = v * 60 + 100
        img[:,:,2] = v * 80 + 140
        return img

    def _generate_fractal(self, W, H, cfg, rng):
        img = np.zeros((H, W), dtype=float)
        depth = min(cfg.recursion_depth + 2, 8)
        self._fractal_fill(img, W//2, H//2, W//2, depth, rng, cfg)
        for i in range(3):
            img3 = np.stack([img] * 3, axis=-1)
            img3[:,:,i] *= (0.6 + 0.4 * i / 2)
        return img3 * 1.5

    def _fractal_fill(self, img, cx, cy, size, depth, rng, cfg):
        if depth <= 0 or size < 2:
            return
        for i in range(cfg.symmetry):
            angle = i * 2 * np.pi / cfg.symmetry
            ox = int(cx + size * np.cos(angle))
            oy = int(cy + size * np.sin(angle))
            v = rng.uniform(0.3, 1.0)
            try:
                x1, x2 = max(0, ox - size//4), min(img.shape[1], ox + size//4)
                y1, y2 = max(0, oy - size//4), min(img.shape[0], oy + size//4)
                img[y1:y2, x1:x2] += v
            except Exception:
                pass
            self._fractal_fill(img, ox, oy, size * 0.6, depth - 1, rng, cfg)

    def _generate_kaleidoscopic(self, W, H, cfg, rng):
        img = np.zeros((H, W, 3), dtype=float)
        cx, cy = W // 2, H // 2
        Y, X = np.indices((H, W))
        for i in range(cfg.symmetry):
            angle = i * 2 * np.pi / cfg.symmetry
            cos_a, sin_a = np.cos(angle), np.sin(angle)
            rx = (X - cx) * cos_a + (Y - cy) * sin_a + cx
            ry = -(X - cx) * sin_a + (Y - cy) * cos_a + cy
            dist = np.sqrt((rx - cx)**2 + (ry - cy)**2)
            v = np.sin(dist * cfg.frequency * 20) * np.cos(rx * cfg.frequency * 10 + cfg.phase)
            img[:, :, i % 3] += v * 60
        img = np.clip(img + 128, 0, 255)
        return img

    def _generate_rotating_grid(self, W, H, cfg, rng):
        img = np.zeros((H, W, 3), dtype=float)
        angle = np.radians(cfg.rotation)
        cos_a, sin_a = np.cos(angle), np.sin(angle)
        Y, X = np.indices((H, W))
        rx = (X - W/2) * cos_a + (Y - H/2) * sin_a + W/2
        ry = -(X - W/2) * sin_a + (Y - H/2) * cos_a + H/2
        spacing = max(1, int(20 / cfg.scale))
        gx = np.sin(rx * np.pi / spacing) * 100
        gy = np.sin(ry * np.pi / spacing) * 100
        img[:,:,0] = (gx + gy) / 2 + 128
        img[:,:,1] = gx * 0.5 + 128
        img[:,:,2] = gy * 0.5 + 128
        return img

    def _generate_warped_grid(self, W, H, cfg, rng):
        img = np.zeros((H, W, 3), dtype=float)
        Y, X = np.indices((H, W))
        warp = cfg.warp * 10
        wx = X + warp * np.sin(Y * cfg.frequency * 10 + cfg.phase)
        wy = Y + warp * np.cos(X * cfg.frequency * 10 + cfg.phase)
        spacing = max(1, int(15 / cfg.scale))
        gx = np.sin(wx * np.pi / spacing) * 100
        gy = np.sin(wy * np.pi / spacing) * 100
        img[:,:,0] = (gx + gy) / 2 + 128
        img[:,:,1] = gx * 0.7 + 100
        img[:,:,2] = gy * 0.7 + 140
        return img

    def _generate_tunnel(self, W, H, cfg, rng):
        img = np.zeros((H, W, 3), dtype=float)
        cx, cy = W // 2, H // 2
        Y, X = np.indices((H, W))
        dist = np.sqrt((X - cx)**2 + (Y - cy)**2)
        rings = np.sin(dist * cfg.frequency * 15 + cfg.phase * np.sin(dist * 0.01))
        angle = np.arctan2(Y - cy, X - cx)
        radial_lines = np.sin(angle * cfg.symmetry + cfg.phase) * 0.5 + 0.5
        img[:,:,0] = rings * radial_lines * 120 + 100
        img[:,:,1] = rings * 60 + 100
        img[:,:,2] = rings * (1 - radial_lines) * 120 + 100
        return img

    def _generate_recursive_corridor(self, W, H, cfg, rng):
        img = np.zeros((H, W, 3), dtype=float)
        cx, cy = W // 2, H // 2
        for i in range(min(cfg.recursion_depth + 3, 10)):
            size = max(4, int(W * (0.15 + 0.08 * i)))
            offset = int((i % 2) * size * 0.3)
            v = 0.5 + 0.3 * np.sin(i + cfg.phase)
            try:
                img[cy-size//2+offset:cy+size//2+offset, cx-size//2:cx+size//2, i%3] += v * 80
                img[cy-size//4:cy+size//4, cx-size//4:cx+size//4, (i+1)%3] += v * 60
            except Exception:
                pass
        Y, X = np.indices((H, W))
        dist = np.sqrt((X-cx)**2 + (Y-cy)**2)
        ring = np.sin(dist * cfg.frequency * 10) * 30
        img += ring[:,:,None]
        return img

    def _generate_polygons(self, W, H, cfg, rng):
        img = np.zeros((H, W, 3), dtype=float) + 64
        cx, cy = W // 2, H // 2
        Y, X = np.indices((H, W))
        angle = np.arctan2(Y - cy, X - cx)
        dist = np.sqrt((X - cx)**2 + (Y - cy)**2)
        n_sides = max(3, cfg.symmetry)
        polygon_angles = np.round(angle * n_sides / (2 * np.pi)) * (2 * np.pi / n_sides)
        px = cx + dist * np.cos(polygon_angles)
        py = cy + dist * np.sin(polygon_angles)
        dist_p = np.sqrt((X - px)**2 + (Y - py)**2)
        v = np.sin(dist_p * cfg.frequency * 20 + cfg.phase) * 100
        img[:,:,0] = np.clip(v + 128, 0, 255)
        img[:,:,1] = np.clip(v * 0.5 + 100, 0, 255)
        img[:,:,2] = np.clip(v * 0.8 + 110, 0, 255)
        return img

    def _generate_moire(self, W, H, cfg, rng):
        img1 = np.zeros((H, W), dtype=float)
        img2 = np.zeros((H, W), dtype=float)
        spacing1 = max(1, int(8 / cfg.scale))
        spacing2 = max(1, int(8 / cfg.scale * 1.05))
        Y, X = np.indices((H, W))
        img1 = np.sin(X * np.pi / spacing1) * np.sin(Y * np.pi / spacing1)
        img2 = np.sin(X * np.pi / spacing2 + cfg.phase) * np.sin(Y * np.pi / spacing2)
        moire = (img1 + img2) / 2 * 100 + 128
        img = np.stack([moire] * 3, axis=-1)
        return img

    def _generate_high_frequency(self, W, H, cfg, rng):
        img = np.zeros((H, W, 3), dtype=float)
        Y, X = np.indices((H, W))
        freq = cfg.frequency * 100
        for i in range(3):
            v = np.sin(X * freq * (1 + i*0.3) + cfg.phase) * np.cos(Y * freq * (0.8 + i*0.2) + cfg.phase)
            img[:,:,i] = v * 80 + 128
        return img

    def _generate_interference_field(self, W, H, cfg, rng):
        Y, X = np.indices((H, W))
        img = np.zeros((H, W, 3), dtype=float)
        sources = [(W*0.3, H*0.3), (W*0.7, H*0.3), (W*0.3, H*0.7), (W*0.7, H*0.7)]
        for i, (sx, sy) in enumerate(sources):
            dist = np.sqrt((X - sx)**2 + (Y - sy)**2)
            v = np.sin(dist * cfg.frequency * 30 + i * np.pi / 2 + cfg.phase)
            img[:,:,i % 3] += v * 50
        img = img / len(sources) + 128
        return img

    def _generate_noise_geometry(self, W, H, cfg, rng):
        img = np.zeros((H, W, 3), dtype=float)
        noise = rng.uniform(0, 1, (H, W, 3)) * cfg.noise * 200
        img += noise
        for i in range(cfg.symmetry * 2):
            angle = i * np.pi / cfg.symmetry
            x0 = int(W * 0.5 + W * 0.3 * np.cos(angle))
            y0 = int(H * 0.5 + H * 0.3 * np.sin(angle))
            size = max(4, int(20 * cfg.scale))
            try:
                img[y0:y0+size, x0:x0+size, i%3] += 80
            except Exception:
                pass
        img += 64
        return np.clip(img, 0, 255)

    def _generate_morphing(self, W, H, cfg, rng):
        img = np.zeros((H, W, 3), dtype=float)
        t = cfg.temporal_modulation
        Y, X = np.indices((H, W))
        for c in range(3):
            v = np.sin(X * cfg.frequency * 15 * (1 + t * 0.3) + cfg.phase + c) * np.cos(Y * cfg.frequency * 12 * (1 - t * 0.2))
            img[:,:,c] = v * 70 + 128
        return img
