import sys
import os
import json
import argparse
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from stimuli.generator import StimulusGenerator, StimulusConfig
from altered_state.engine import AlteredStateEngine
from experiments.engine import ExperimentEngine
from app.app_state import AppState


def setup_logging(level: str = "INFO"):
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def run_headless_experiment(args) -> Dict[str, Any]:
    setup_logging(args.log_level)
    logger = logging.getLogger("phantom_vision_lab.cli")

    logger.info("PHANTOM VISION LAB - Headless Experiment Mode")
    logger.info(f"Pattern: {args.pattern}")
    logger.info(f"Seed: {args.seed}")
    logger.info(f"Preset: {args.preset}")

    state = AppState()

    cfg = StimulusConfig(
        seed=args.seed,
        pattern_type=args.pattern,
    )
    if args.size and args.size != 512:
        cfg.size = (args.size, args.size)

    if args.preset and args.preset != "CUSTOM":
        logger.info(f"Applying preset: {args.preset}")
        state.altered_engine.apply_preset(args.preset)
    elif args.params:
        for param_val in args.params:
            if "=" in param_val:
                name, value = param_val.split("=", 1)
                try:
                    state.altered_engine.set_param(name.strip(), float(value.strip()))
                    logger.info(f"Set {name.strip()} = {value.strip()}")
                except (ValueError, KeyError) as e:
                    logger.warning(f"Skipping invalid param '{param_val}': {e}")

    params = state.altered_engine.to_dict()
    logger.info(f"Altered params: {json.dumps(params, indent=2)}")

    logger.info("Running experiment...")
    result = state.run_experiment(cfg, params=params)

    exp_id = result["experiment_id"]
    logger.info(f"Experiment complete: {exp_id}")
    logger.info(f"Divergence: {result['divergence'].get('perception_divergence_score', 0):.6f}")
    logger.info(f"Stimulus: {result['stimulus_path']}")

    print(json.dumps({
        "experiment_id": exp_id,
        "divergence": result["divergence"],
        "summary": result["summary"],
        "stimulus_path": result["stimulus_path"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, indent=2, default=str))

    return result


def run_batch_experiments(args) -> list:
    setup_logging(args.log_level)
    logger = logging.getLogger("phantom_vision_lab.cli")

    logger.info(f"Batch mode: {args.iterations} experiments")

    state = AppState()
    results = []

    presets = args.presets.split(",") if args.presets else ["BASELINE"]
    patterns = args.patterns.split(",") if args.patterns else StimulusGenerator.PATTERN_TYPES

    count = 0
    for preset in presets:
        for pattern in patterns:
            if count >= args.iterations:
                break

            cfg = StimulusConfig(
                seed=args.seed + count,
                pattern_type=pattern,
            )

            state.altered_engine.reset()
            if preset != "BASELINE":
                state.altered_engine.apply_preset(preset)

            params = state.altered_engine.to_dict()
            logger.info(f"[{count+1}/{args.iterations}] {preset}/{pattern}")

            result = state.run_experiment(cfg, params=params)
            results.append({
                "experiment_id": result["experiment_id"],
                "preset": preset,
                "pattern": pattern,
                "divergence": result["divergence"],
            })
            count += 1

    summary = {
        "total": len(results),
        "presets_tested": presets,
        "patterns_tested": list(set(p["pattern"] for p in results)),
    }
    logger.info(f"Batch complete: {len(results)} experiments")
    print(json.dumps(summary, indent=2))

    return results


def main():
    parser = argparse.ArgumentParser(
        description="PHANTOM VISION LAB - Run experiments headlessly",
    )
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        help="Logging level")

    subparsers = parser.add_subparsers(dest="command")

    # Single experiment
    single = subparsers.add_parser("experiment", help="Run a single experiment")
    single.add_argument("--pattern", default="lattice",
                        choices=StimulusGenerator.PATTERN_TYPES,
                        help="Pattern type")
    single.add_argument("--seed", type=int, default=42, help="Random seed")
    single.add_argument("--preset", default="CUSTOM",
                        help="Preset name (BASELINE, LOW PERTURBATION, etc.) or CUSTOM")
    single.add_argument("--size", type=int, default=512, help="Image size (NxN)")
    single.add_argument("--params", nargs="*", default=[],
                        help="Parameter overrides (e.g., SENSORY_GAIN=90 PREDICTION_ERROR=80)")

    # Batch mode
    batch = subparsers.add_parser("batch", help="Run multiple experiments")
    batch.add_argument("--iterations", type=int, default=10, help="Number of experiments")
    batch.add_argument("--seed", type=int, default=42, help="Base random seed")
    batch.add_argument("--presets", default="BASELINE,LOW PERTURBATION,HIGH SENSORY GAIN",
                        help="Comma-separated presets")
    batch.add_argument("--patterns", default=None,
                        help="Comma-separated pattern types (default: all)")

    args = parser.parse_args()

    if args.command == "experiment":
        run_headless_experiment(args)
    elif args.command == "batch":
        run_batch_experiments(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
