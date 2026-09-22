import platform
import os
import subprocess
import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class HardwareInfo:
    cpu: str = "Unknown"
    ram_mb: int = 0
    gpu: str = "None"
    vram_mb: int = 0
    cuda_available: bool = False
    cpu_count: int = 1
    cuda_devices: List[str] = field(default_factory=list)

    @property
    def hardware_mode(self) -> str:
        if self.cuda_available and self.vram_mb >= 4096:
            return "HIGH QUALITY"
        if self.ram_mb >= 8192:
            return "BALANCED"
        return "LIGHT"

    @property
    def recommended_model_size(self) -> str:
        mode = self.hardware_mode
        if mode == "HIGH QUALITY":
            return "large"
        if mode == "BALANCED":
            return "medium"
        return "small"


def detect_hardware() -> HardwareInfo:
    info = HardwareInfo()
    info.cpu_count = os.cpu_count() or 1

    try:
        result = subprocess.run(["wmic", "cpu", "get", "Name"],
                                capture_output=True, text=True, timeout=5)
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("Name"):
                info.cpu = line
                break
    except Exception:
        pass

    try:
        result = subprocess.run(["wmic", "OS", "get", "TotalVisibleMemorySize"],
                                capture_output=True, text=True, timeout=5)
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if line.isdigit():
                info.ram_mb = int(line) // 1024
                break
    except Exception:
        pass

    info.cuda_available = _check_cuda()
    if info.cuda_available:
        info.gpu = _get_cuda_gpu_name()
        info.vram_mb = _get_cuda_vram()

    return info


def _check_cuda() -> bool:
    try:
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except Exception:
        return False


def _get_cuda_gpu_name() -> str:
    try:
        result = subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                                capture_output=True, text=True, timeout=5)
        return result.stdout.strip().split("\n")[0].strip()
    except Exception:
        return "Unknown CUDA GPU"


def _get_cuda_vram() -> int:
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5)
        return int(result.stdout.strip().split("\n")[0].strip())
    except Exception:
        return 0
