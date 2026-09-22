import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from config.settings import settings


class ExperimentStore:
    def __init__(self, experiments_dir: str = None):
        self.experiments_dir = experiments_dir or settings.experiments_dir
        os.makedirs(self.experiments_dir, exist_ok=True)
        self._registry_path = os.path.join(self.experiments_dir, "registry.json")
        self._registry: Dict[str, Dict] = self._load_registry()

    def _load_registry(self) -> Dict[str, Dict]:
        if os.path.exists(self._registry_path):
            try:
                with open(self._registry_path, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_registry(self):
        with open(self._registry_path, "w") as f:
            json.dump(self._registry, f, indent=2, default=str)

    def create_experiment(self, stimulus_id: str = None, params: Dict[str, Any] = None) -> str:
        exp_id = f"EXP-{uuid.uuid4().hex[:6].upper()}"
        experiment_dir = os.path.join(self.experiments_dir, exp_id)
        os.makedirs(experiment_dir, exist_ok=True)
        self._registry[exp_id] = {
            "directory": exp_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "stimulus_id": stimulus_id or "",
            "status": "running",
        }
        self._save_registry()
        return exp_id

    def save_experiment_data(self, exp_id: str, data: Dict[str, Any], category: str):
        exp_dir = os.path.join(self.experiments_dir, exp_id)
        os.makedirs(exp_dir, exist_ok=True)
        filepath = os.path.join(exp_dir, f"{category}.json")
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)
        if exp_id in self._registry:
            self._registry[exp_id]["status"] = "complete"
            self._save_registry()

    def get_experiment(self, exp_id: str) -> Optional[Dict[str, Any]]:
        exp_dir = os.path.join(self.experiments_dir, exp_id)
        if not os.path.exists(exp_dir):
            return None
        data = {}
        for fname in ["metadata", "baseline", "altered", "measurements"]:
            fpath = os.path.join(exp_dir, f"{fname}.json")
            if os.path.exists(fpath):
                with open(fpath, "r") as f:
                    data[fname] = json.load(f)
        return data

    def list_experiments(self) -> List[Dict[str, Any]]:
        return sorted(
            [{"exp_id": k, **v} for k, v in self._registry.items()],
            key=lambda x: x.get("timestamp", ""),
            reverse=True,
        )

    def get_experiment_files(self, exp_id: str) -> List[str]:
        exp_dir = os.path.join(self.experiments_dir, exp_id)
        if not os.path.exists(exp_dir):
            return []
        return os.listdir(exp_dir)
