import json
import csv
import os
from typing import Dict, Any, List
from PIL import Image, ImageDraw, ImageFont


class Exporter:
    def __init__(self, experiments_dir: str):
        self.experiments_dir = experiments_dir

    def export_json(self, exp_id: str, data: Dict[str, Any]) -> str:
        exp_dir = os.path.join(self.experiments_dir, exp_id)
        path = os.path.join(exp_dir, "export.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        return path

    def export_csv(self, exp_id: str, data: Dict[str, Any]) -> str:
        exp_dir = os.path.join(self.experiments_dir, exp_id)
        path = os.path.join(exp_dir, "export.csv")
        flat = self._flatten(data)
        if not flat:
            return path
        all_fields = list(dict.fromkeys(k for row in flat for k in row.keys()))
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=all_fields, restval="")
            writer.writeheader()
            for row in flat:
                writer.writerow(row)
        return path

    def export_html_report(self, exp_id: str, report: Dict[str, Any]) -> str:
        exp_dir = os.path.join(self.experiments_dir, exp_id)
        path = os.path.join(exp_dir, "report.html")
        html = self._generate_html(report)
        with open(path, "w") as f:
            f.write(html)
        return path

    def export_markdown_report(self, exp_id: str, report: Dict[str, Any]) -> str:
        exp_dir = os.path.join(self.experiments_dir, exp_id)
        path = os.path.join(exp_dir, "report.md")
        md = self._generate_markdown(report)
        with open(path, "w") as f:
            f.write(md)
        return path

    def export_stimulus_image(self, exp_id: str, img_array, filename: str = "stimulus.png") -> str:
        exp_dir = os.path.join(self.experiments_dir, exp_id)
        os.makedirs(exp_dir, exist_ok=True)
        path = os.path.join(exp_dir, filename)
        Image.fromarray(img_array).save(path)
        return path

    def _flatten(self, data, prefix="") -> List[Dict[str, Any]]:
        results = []
        if isinstance(data, dict):
            for k, v in data.items():
                key = f"{prefix}_{k}" if prefix else k
                if isinstance(v, (dict, list)):
                    results.extend(self._flatten(v, key))
                else:
                    results.append({key: v})
        elif isinstance(data, list):
            for i, item in enumerate(data[:5]):
                results.extend(self._flatten(item, f"{prefix}_{i}"))
        return results

    def _generate_html(self, report: Dict[str, Any]) -> str:
        return f"""<!DOCTYPE html>
<html><head><title>PHANTOM VISION LAB Report</title>
<style>
body {{ background: #0a0a12; color: #e0e0e0; font-family: 'Segoe UI', monospace; padding: 20px; }}
h1 {{ color: #00ffff; }} h2 {{ color: #ff00ff; border-bottom: 1px solid #333; }}
.panel {{ background: #14141f; border: 1px solid #00ffff33; border-radius: 8px; padding: 15px; margin: 10px 0; }}
.score {{ color: #00ff88; font-size: 1.3em; font-weight: bold; }}
</style></head><body>
<h1>PHANTOM VISION LAB - Experiment Report</h1>
<div class="panel">
<h2>Experiment ID</h2><p>{report.get('experiment_id', 'N/A')}</p>
<h2>Perception Divergence Score</h2><p class="score">{report.get('perception_divergence_score', 0):.4f}</p>
<h2>What Model Saw</h2><p>{report.get('what_model_saw', 'N/A')}</p>
<h2>What Model Described</h2><p>{report.get('what_model_described', 'N/A')}</p>
<h2>Changes from Baseline</h2><ul>{''.join(f'<li>{c}</li>' for c in report.get('changes_from_baseline', []))}</ul>
<h2>Scientific Interpretation</h2><p>{report.get('scientific_interpretation', 'N/A')}</p>
</div></body></html>"""

    def _generate_markdown(self, report: Dict[str, Any]) -> str:
        lines = [
            "# PHANTOM VISION LAB - Experiment Report",
            f"**Experiment ID**: {report.get('experiment_id', 'N/A')}",
            f"**Perception Divergence Score**: {report.get('perception_divergence_score', 0):.4f}",
            "",
            "## What Model Saw",
            report.get("what_model_saw", "N/A"),
            "",
            "## What Model Described",
            report.get("what_model_described", "N/A"),
            "",
            "## Changes from Baseline",
        ]
        for c in report.get("changes_from_baseline", []):
            lines.append(f"- {c}")
        lines.append("")
        lines.append("## Scientific Interpretation")
        lines.append(report.get("scientific_interpretation", "N/A"))
        return "\n".join(lines)
