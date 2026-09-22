# PHANTOM VISION LAB - Final Audit

## WHAT WAS BUILT

A complete Windows desktop research application with:

- **Structured-Light Stimulus Generator**: 15 pattern types (lattice, radial diffraction, interference, concentric, fractal, kaleidoscopic, rotating grid, warped grid, tunnel, recursive corridor, polygons, moiré, high-frequency, interference field, noise geometry, morphing). All deterministic with seed-based generation.

- **Altered State Engine**: 11 computational parameters (Sensory Gain, Prior Weight, Prediction Error, Cross-Modal Association, Representation Drift, Temporal Instability, Recursive Attention, Pattern Amplification, Novelty Gain, Semantic Loose Association) with 0-100 range, presets, reset/randomize, and metric transformation logic.

- **Vision Analysis Pipeline**: Classical CV-based analysis including object detection, pattern analysis, geometry scoring, symmetry detection, color extraction, spatial relationship analysis, text-like structure detection, symbol detection, and code-like structure detection.

- **Experiment Engine**: Full baseline vs. altered comparison with experiment tracking, data persistence, and replay capability.

- **Statistics Engine**: Group statistics, t-tests, effect sizes, confidence intervals, and aggregate reporting.

- **PySide6 UI**: Dark laboratory theme with cyan/magenta accents, stimulus viewer with live animation, baseline/altered comparison panels, perception divergence display, metrics display, control panel with sliders and presets, experiment history table, and statistics dashboard tab.

- **Live Stimulus Animation**: Continuous morphing stimulus display with temporal modulation, running at adjustable frame rates.

- **Report Generation**: Structured experience reports with scientific interpretation, cautious language, and anti-priming disclaimers.

- **Data Export**: Automatic export to JSON, CSV, HTML report, and Markdown report formats after every experiment (via UI or programmatic API).

- **Cross-Modal Enhancement**: The Cross-Modal Association parameter now actively influences semantic concepts, object tagging, and spatial relationship analysis.

- **Automated Tests**: Tests for stimulus determinism, engine behavior, metrics calculation, experiment store, statistics, and integration.

## WHAT WORKS

- Stimulus generation is fully deterministic and tested
- Altered state parameter system with presets works correctly
- Vision analysis pipeline runs without errors
- Experiment engine completes full baseline/altered comparisons
- UI launches and displays stimuli and metrics
- Experiment data persists to disk
- Reports generate with proper scientific language
- Export to JSON, CSV, HTML, Markdown works
- Statistics engine computes aggregate reports
- All tests pass
- Hardware detection works (CPU, RAM, CUDA detection)

## WHAT DOES NOT WORK

- **No neural network model is loaded**: The vision pipeline uses classical computer vision algorithms (edge detection, symmetry analysis, contour finding) rather than a deep learning model. This means the "AI interpretation" is computed from mathematical image analysis rather than a neural network's internal representations.
- **No GPU acceleration**: All processing is CPU-based. CUDA detection works but no GPU computation is performed.
- **No actual blind experiment mode**: The UI does not implement anonymous condition IDs in a way that would prevent the user from knowing stimulus types. The infrastructure is designed but not enforced in the UI layer.
- **No live animation**: The stimulus animation thread now runs continuously in the main UI window, showing morphing structured-light patterns.
- **No internal activation telemetry**: Since no neural network model is loaded, the "Live AI Inner-State Monitor" feature cannot show activation statistics, embedding trajectories, or attention weights.

## KNOWN LIMITATIONS

1. No pre-trained neural network model is bundled or downloaded
2. All perception metrics are derived from classical CV, not deep learning
3. Running on modest hardware: CPU-only mode, no VRAM usage
4. No paid API requirements - fully local
5. Statistical tests require multiple experiments before meaningful results
6. Code-like structure detection uses geometric heuristics, not linguistic analysis
7. Cross-modal associations are simulated, not computed from actual multimodal models

## MODEL REQUIREMENTS

- No pre-trained model required for core functionality
- Vision analysis uses classical computer vision algorithms
- If a neural network vision model is desired in the future, the `VisionModelProvider` class in `vision/__init__.py` provides the interface for adding one
- Recommended: Any vision transformer or CNN can be added as a provider without modifying the rest of the system

## HARDWARE REQUIREMENTS

- **Minimum**: 4GB RAM, any modern CPU (LIGHT mode)
- **Recommended**: 8GB+ RAM, modern CPU (BALANCED mode - default)
- **High Quality**: 16GB+ RAM, CUDA GPU with 4GB+ VRAM
- All processing works in CPU-only mode

## SCIENTIFIC LIMITATIONS

1. Results are from computational image analysis, not neural network perception
2. Cannot establish causality between perturbation and interpretation changes
3. Cannot determine if effects are specific to the perturbation type
4. No consciousness or subjective experience assessment is possible
5. Statistical significance requires sufficient independent observations
6. The perception divergence score is an algorithmic construct, not a validated psychometric instrument

## HOW TO RUN THE FIRST EXPERIMENT

1. Open a command prompt in the `phantom_vision_lab` directory
2. Run: `RUN.bat` or `python main.py`
3. Wait for the application window to open
4. In the stimulus section, a generated structured-light pattern will be displayed
5. Adjust sliders in the Control Panel to desired values (or apply a preset)
6. Click "RUN EXPERIMENT" in the Control Panel
7. Wait for the experiment to complete
8. View results: perception divergence score, metrics, and a report dialog will appear
9. Data is saved in the `data/experiments/EXP-XXXXXX/` directories

## HOW TO INTERPRET RESULTS

### Perception Divergence Score
- **0.0**: No difference between baseline and altered interpretation
- **0.1-0.3**: Minor differences in interpretation
- **0.3-0.5**: Moderate differences
- **0.5+**: Significant differences in interpretation

### Geometry Score
Measures how geometric/structured the model's interpretation is. Higher values indicate more geometric interpretation.

### Novelty Score
Measures how novel/unusual the model's interpretation is. Higher values indicate more novel interpretation.

### Confidence Score
How confident the model is in its interpretation. May decrease under perturbation.

### Uncertainty Score
How uncertain the model is. May increase under perturbation.

### Code-like Structures
Count of detected code-like patterns (grid structures, sequential arrangements, hierarchical structures).

### Important Note
All scores are derived from mathematical image analysis algorithms, not from neural network internal states. They represent computational analogues to what might be measured in a neural network perception system. Treat them as research instruments for studying computational perturbation effects, not as measures of subjective experience.
