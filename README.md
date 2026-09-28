# PHANTOM VISION LAB

Computational research application that simulates altered-state AI perception when viewing structured-light visual stimuli. Compares baseline and altered computational modes to investigate whether controlled perturbations cause AI visual interpretations to become unusually geometric, symbolic, recursive, or code-like.

## Features

### Core Systems
- **Structured-Light Stimulus Generator**: 15 pattern types (lattice, radial diffraction, interference, concentric, fractal, kaleidoscopic, rotating grid, warped grid, tunnel, recursive corridor, polygons, moiré, high-frequency, interference field, noise geometry, morphing). All deterministic with seed-based generation.
- **Altered State Engine**: 11 computational parameters (Sensory Gain, Prior Weight, Prediction Error, Cross-Modal Association, Representation Drift, Temporal Instability, Recursive Attention, Pattern Amplification, Novelty Gain, Semantic Loose Association) with 6 presets.
- **Vision Analysis Pipeline**: Classical CV-based analysis including object detection, pattern analysis, geometry scoring, symmetry detection, color extraction, spatial relationship analysis, text-like structure detection, symbol detection, and code-like structure detection.
- **Experiment Engine**: Full baseline vs. altered comparison with experiment tracking, data persistence, and replay capability.
- **Statistics Engine**: Group statistics, t-tests, effect sizes (Cohen's d), confidence intervals, and aggregate reporting.

### UI & Interaction
- **PySide6 Dark UI**: Laboratory theme with cyan/magenta accents
- **Live Stimulus Animation**: Continuous morphing display with temporal modulation
- **Baseline/Altered Comparison**: Side-by-side viewer panels
- **Perception Divergence Display**: Real-time score with progress bar
- **Control Panel**: 11 parameter sliders, presets (BASELINE, LOW PERTURBATION, HIGH SENSORY GAIN, HIGH PREDICTION ERROR, PATTERN AMPLIFICATION, MAXIMUM EXPLORATION), reset/randomize, save/load custom presets
- **Experiment History Table**: Browse past experiments with divergence scores, metrics, and timestamps
- **Statistics Dashboard Tab**: Aggregated analysis with t-test results and effect sizes

### Data & Export
- **Auto-Export**: JSON, CSV, HTML report, and Markdown report generated automatically after every experiment
- **Blind Experiment Mode**: Anonymous condition IDs supported
- **Experiment Replay**: Full reproducibility from metadata and seeds
- **Data Persistence**: All experiments saved in `data/experiments/` with registry

## Installation

### Prerequisites
- Windows 10/11
- Python 3.13+
- pip

### Setup

```bash
cd phantom_vision_lab
pip install -r requirements.txt
```

Or manually:

```bash
pip install PySide6 numpy Pillow matplotlib scipy scikit-learn pytest
```

### Running

```bash
python main.py
```

Or use the batch file:

```cmd
RUN.bat
```

For executable build:

```cmd
BUILD.bat
```

## Quick Start

1. Launch the application
2. A generated structured-light pattern will be displayed in the LIVE STIMULUS panel (animated)
3. Adjust parameters in the Control Panel using sliders (0-100 for each)
4. Apply a preset: BASELINE, LOW PERTURBATION, HIGH SENSORY GAIN, HIGH PREDICTION ERROR, PATTERN AMPLIFICATION, MAXIMUM EXPLORATION
5. Click **RUN EXPERIMENT** to execute baseline + altered comparison
6. View results: perception divergence score, metrics, and scientific interpretation report
7. Browse past experiments in the **History** tab and statistics in the **Statistics** tab

## Running Tests

```bash
python -m pytest tests/ -v
```

## Technology Stack

- **Python 3.13+** — Core runtime
- **PySide6** — Desktop UI
- **NumPy/SciPy** — Numerical computation
- **Pillow** — Image processing
- **scikit-learn** — Color clustering
- **matplotlib** — Visualization (available)
- **pytest** — Testing framework

## Project Structure

```
phantom_vision_lab/
├── app/                  Application entry point and state management
│   └── app_state.py      AppState, experiment orchestration
├── ui/                   PySide6 interface
│   ├── main_window.py    Main window, viewers, animation, history, stats
│   ├── control_panel.py  Parameter controls, presets, experiment trigger
│   └── components.py     Shared UI components (ImageViewer, threads)
├── vision/               Vision analysis pipeline
│   └── __init__.py       VisionModelProvider, analyze_image_cv, VisionResult
├── altered_state/        Computational perturbation engine
│   └── engine.py         AlteredStateEngine, parameters, presets, metric transforms
├── stimuli/              Visual stimulus generator
│   └── generator.py      15 pattern types, seed-based determinism
├── experiments/          Experiment orchestration
│   └── engine.py         Run experiments, replay, results management
├── analysis/             Metrics and divergence calculations
│   └── metrics.py        PerceptionMetrics, compute_perception_divergence
├── statistics/           Statistical analysis engine
│   └── stats.py          Group stats, t-tests, effect sizes, confidence intervals
├── storage/              Data persistence and export
│   ├── experiment_store.py    Experiment registry and data storage
│   └── exporter.py            JSON, CSV, HTML, Markdown export
├── reports/              Report generation
│   └── reporter.py        PerceptionReport, scientific interpretation
├── config/               Application settings
│   └── settings.py       AppSettings, paths, hardware mode
├── models/               Hardware detection
│   └── hardware.py       CPU, RAM, CUDA detection
├── tests/                Automated tests
│   └── test_all.py       25 tests across all modules
├── docs/                 Documentation
│   ├── RESEARCH.md       Research documentation and bibliography
│   └── FINAL_AUDIT.md    Feature audit and interpretation guide
├── data/experiments/     Runtime experiment data
├── main.py               Entry point
└── requirements.txt      Dependencies
```

## Experiment Data

All experiments are saved in `data/experiments/EXP-XXXXXX/` with:

- `metadata.json` — Experiment configuration, model info, parameters
- `baseline.json` / `altered.json` — AI interpretation results
- `measurements.json` — Divergence scores, seeds, timestamps
- `stimulus.png` — Generated visual stimulus
- `report.md` / `report.html` — Structured experience reports
- `export.json` / `export.csv` — Flat data exports

## Interpretation Guide

### Perception Divergence Score
| Range | Meaning |
|-------|---------|
| 0.0 | No difference between baseline and altered interpretation |
| 0.1-0.3 | Minor differences in interpretation |
| 0.3-0.5 | Moderate differences |
| 0.5+ | Significant differences in interpretation |

### Metrics
- **Geometry Score**: How geometric/structured the model's interpretation is
- **Symmetry Score**: Degree of bilateral symmetry detected
- **Confidence**: How confident the model is in its interpretation (may decrease under perturbation)
- **Novelty**: How novel/unusual the model's interpretation is (may increase under perturbation)
- **Uncertainty**: Model uncertainty (may increase under perturbation)
- **Code-like Structures**: Count of detected code-like patterns (grid structures, sequential arrangements)

## Scientific Limitations

- This is a computational simulation only
- Does not reproduce biological psychedelic states
- Does not establish subjective consciousness
- All metrics are derived from computer vision algorithms, not neural network internals
- Statistical significance requires sufficient independent observations
- The vision model uses classical CV techniques (edge detection, symmetry analysis) rather than deep learning
- Cross-modal associations are simulated computationally, not computed from actual multimodal models

## Hardware Requirements

| Mode | Requirements |
|------|-------------|
| Light Mode | 4GB+ RAM, CPU only |
| Balanced Mode | 8GB+ RAM, recommended default |
| High Quality Mode | 16GB+ RAM, CUDA GPU with 4GB+ VRAM recommended |

All processing works in CPU-only mode.

## License

Virtual simulation only. No physical hardware is controlled.

---

_Disclaimer: This software simulates computational changes in AI perception. It does not reproduce a biological psychedelic state and does not establish subjective consciousness. All measurements are derived from mathematical image analysis algorithms, not from neural network internal states._
