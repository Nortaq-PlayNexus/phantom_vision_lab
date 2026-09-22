import os
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class AppSettings:
    app_name: str = "PHANTOM VISION LAB"
    app_subtitle: str = "AI Altered-State & Structured-Light Perception Simulator"
    experiments_dir: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "experiments")
    log_level: str = "INFO"
    hardware_mode: str = "BALANCED"
    random_seed: int = 42
    model_name: str = "phantom-vision-local"
    model_version: str = "0.1.0"
    image_size: tuple = (512, 512)
    display_size: tuple = (400, 400)
    cuda_available: bool = False
    vram_mb: int = 0
    total_ram_mb: int = 0
    cpu_count: int = os.cpu_count() or 1

    def ensure_dirs(self):
        os.makedirs(self.experiments_dir, exist_ok=True)

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items()}


settings = AppSettings()
settings.ensure_dirs()
