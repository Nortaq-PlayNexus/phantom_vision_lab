# Security Policy

## Scope

A local desktop research application: deterministic image generation, classical
computer-vision analysis, statistical computation, and a PySide6 GUI. No web
server, no network service, no authentication, no user accounts.

**Known vulnerabilities: none identified.**

## Dependencies

`requirements.txt`, all standard PyPI:

```
PySide6  numpy  scipy  Pillow  matplotlib  scikit-learn  pytest
PyInstaller (Windows only)
```

## What is deliberately not supported

- **Running as a service or binding any port.** There is no server component.
- **Processing untrusted images.** Image loading uses Pillow and NumPy on files
  the user supplies locally. The software does not promise safety on hostile
  input, and no image-parsing sandbox is claimed.
- **Network access.** None is required. `scikit-learn` and `matplotlib` may probe
  caches on first use; nothing in this project transmits data.
- **Automated blinding.** There is no blinding implementation. A previous version
  of the README claimed otherwise; see `docs/RELEASE_AUDIT.md`.

## Data handling

Experiment output goes to `data/experiments/` and is **git-ignored**. It contains
generated stimuli and computed metrics only — no personal data, no credentials, no
network-derived input.

The application writes only inside that directory. `config/settings.py` resolves
paths relative to the project root.

## Integrity as the real risk

This project's main risk is not network-facing. It is **documentation claiming
capabilities the code lacks** — a failure mode that inflates the apparent
rigour of any downstream use. Three such claims were found and corrected before
first release; see `docs/RELEASE_AUDIT.md`.

Two are now enforced by tests:

- `test_no_blind_mode_implementation` — greps the source for blinding keywords
- `test_pattern_type_count_matches_documentation` — fails if the pattern count
  changes without the documentation being updated

## Reporting

Open a private security advisory, or contact the maintainers directly. Please do
not open a public issue for an unfixed vulnerability.

Given the scope, reports about **misleading documentation or overstated claims**
are just as welcome here, and are arguably the more likely finding.
