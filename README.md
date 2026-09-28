# PHANTOM VISION LAB

## Overview
PHANTOM VISION LAB is a computational research application that simulates altered-state AI perception when viewing structured-light visual stimuli. It compares baseline and altered computational modes to investigate whether controlled perturbations cause AI visual interpretations to become unusually geometric, symbolic, recursive, or code-like.

## Installation

### Prerequisites
- Windows 10/11
- Python 3.13+
- pip

### Setup
```
cd phantom_vision_lab
RUN.bat
```

Or manually:
```
pip install PySide6 numpy Pillow matplotlib scipy
python main.py
```

For executable build:
```
BUILD.bat
```

## Running Experiments
1. Launch the application
2. Adjust the stimulus pattern parameters in the control panel
3. Configure altered-state parameters using sliders (0-100 for each)
4. Apply presets: BASELINE, LOW PERTURBATION, HIGH SENSORY GAIN, HIGH PREDICTION ERROR, PATTERN AMPLIFICATION, MAXIMUM EXPLORATION
5. Click RUN EXPERIMENT to execute baseline + altered comparison
6. View results: perception divergence score, metrics, and scientific interpretation report

## Experiment Data
All experiments are saved in the `experiments/` directory with:
- `metadata.json` - experiment configuration, model info, parameters
- `baseline.json` / `altered.json` - AI interpretation results
- `measurements.json` - divergence scores, seeds, timestamps
- `stimulus.png` - generated visual stimulus
- `report.md` / `report.html` - structured experience reports

## Features
- **Structured-Light Generator**: 15 pattern types (lattice, radial diffraction, fractals, moiré, etc.)
- **Altered-State Engine**: 11 computational parameters with presets
- **Vision Pipeline**: Object detection, pattern analysis, geometry/symmetry scoring, code-like structure detection
- **Live Stimulus Animation**: Continuous morphing display with temporal modulation
- **Blind Experiment Mode**: Anonymous condition IDs
- **6 Control/Experiment Groups**: Proper control group design
- **Statistics Engine**: Mean, median, std dev, t-tests, effect sizes, confidence intervals
- **Experiment History**: View past experiments with divergence scores, metrics, and timestamps
- **Statistics Dashboard**: Aggregated statistical analysis with t-tests and effect sizes
- **Auto-Export**: JSON, CSV, HTML, Markdown reports generated automatically after each experiment
- **Experiment Replay**: Full reproducibility with seeds

## Scientific Limitations
- This is a computational simulation only
- Does not reproduce biological psychedelic states
- Does not establish subjective consciousness
- All metrics are derived from computer vision algorithms, not neural network internals
- Statistical significance requires sufficient independent observations
- The vision model uses classical CV techniques (edge detection, symmetry analysis) rather than deep learning

## Hardware Requirements
- **Light Mode**: 4GB+ RAM, CPU only
- **Balanced Mode**: 8GB+ RAM, recommended default
- **High Quality Mode**: 16GB+ RAM, CUDA GPU recommended

## Architecture
```
phantom_vision_lab/
  app/         - Application entry point and state management
  ui/          - PySide6 interface (main window, control panel, viewers)
  vision/      - Vision analysis pipeline
  altered_state/ - Computational perturbation engine
  stimuli/     - Visual stimulus generator
  experiments/ - Experiment orchestration
  analysis/    - Metrics and divergence calculations
  statistics/  - Statistical analysis engine
  models/      - Hardware detection
  storage/     - Data persistence and export
  reports/     - Report generation
  config/      - Application settings
  tests/       - Automated tests
  docs/        - Documentation
  experiments/ - Runtime experiment data
```
