# Changelog

All notable changes to PHANTOM VISION LAB will be documented in this file.

## v2.0 (Current)

### Added
- **Live Stimulus Animation**: Continuous morphing display integrated into main window
- **Experiment History Table**: Browse past experiments with divergence scores, metrics, timestamps
- **History Replay**: Double-click or use REPLAY button to replay any experiment
- **Details View**: View detailed measurements for any past experiment
- **Statistics Dashboard Tab**: Aggregated analysis with t-tests, effect sizes, confidence intervals
- **Auto-Statistics Refresh**: Dashboard automatically updates after each experiment
- **CLI Headless Mode**: `run_experiment.py` with `experiment` and `batch` commands
- **Batch Mode**: Run multiple experiments across presets and patterns
- **Stimulus Configuration**: Pattern type selector and seed input in Control Panel
- **Cross-Modal Effects**: Cross-Modal parameter now influences semantic concepts, object tags, spatial relations
- **Auto-Export**: JSON, CSV, HTML, Markdown reports auto-generated after every experiment
- **Shared UI Components**: `ui/components.py` eliminates code duplication
- **GitHub Repository**: Public repo with topics, description, 8 tags

### Fixed
- **AppState Export Bug**: Fixed `store.get_experiment_data()` → `store.get_experiment()` method mismatch
- **AppState Logging**: Replaced bare `except Exception` with logged warning in `get_stimulus_preview`
- **Import Names**: Fixed `Signals` → `Signal` in PySide6 imports across UI modules
- **Lattice Generator Performance**: Vectorized from Python loops to NumPy meshgrid (25x speedup: 1.69s → 0.067s)

### Changed
- README expanded with quick start, tech stack, project structure, interpretation guide
- `requirements.txt` added with version constraints
- `docs/FINAL_AUDIT.md` updated with all new features

## v1.0 (Initial)
- Core application architecture established
- 15 pattern stimulus generator
- 11-parameter altered state engine
- Vision analysis pipeline
- Experiment engine with replay
- Statistics engine
- PySide6 UI with dark theme
- 25 automated tests
