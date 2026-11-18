
# ReleaseLens — Software Release Visibility Platform

ReleaseLens is a Python-based prototype for monitoring software release status and presenting release evidence in a unified dashboard.

## Features

- Release overview dashboard
- Build and automated test status monitoring
- Deployment status visibility
- Source commit traceability
- Release readiness assessment
- SQLite-backed release records
- Interactive release selection

## Technologies

- Python
- Streamlit
- SQLite
- Pandas
- Python assertions for readiness validation

## How It Works

ReleaseLens stores sample release records containing:

- Release version
- Source commit SHA
- Build status
- Test status
- Deployment status
- Target environment
- Last updated date

The dashboard calculates release readiness:

- Ready: Both build and tests passed
- Blocked: Build or tests failed
- Pending: Builds or tests are incomplete

## Installation

Create a Python virtual environment and install dependencies:

```bash
python -m venv .venv
python -m pip install -r requirements.txt
```

## Run the Dashboard

```bash
python -m streamlit run app.py
```

Open http://localhost:8501.

## Project Status

Working demonstration prototype.

The dashboard currently uses sample release data stored in SQLite. Live integration with GitHub Actions or other CI/CD systems is not implemented.

## Validation

Four readiness scenarios were checked successfully using Python assertions:

1. Passed build and tests → Ready
2. Failed tests → Blocked
3. Running build and pending tests → Pending
4. Failed build → Blocked

The pytest runner encountered an internal error in the local environment, so these checks were verified directly using Python.

## Author

Deepikalahari Devandla

M.S. Software Engineering  
Blekinge Institute of Technology, Sweden
