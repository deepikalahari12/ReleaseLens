
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

ReleaseLens is a working software release monitoring prototype.

### Implemented Features
- Interactive release monitoring dashboard using Streamlit.
- Live integration with GitHub Actions through the GitHub REST API.
- Retrieval of real CI workflow runs, commit IDs, branches, and execution results.
- SQLite storage of CI workflow evidence.
- Commit-based workflow traceability.
- Evidence-based CI health assessments.
- Automated testing using pytest and GitHub Actions.

### Current Limitations
- Sample release records are not yet fully linked to real CI workflow evidence.
- Deployment readiness is not independently verified.
- Other CI/CD platforms are not currently integrated.

The prototype is under active development

## Validation

Four readiness scenarios were checked successfully using Python assertions:

1. Passed build and tests → Ready
2. Failed tests → Blocked
3. Running build and pending tests → Pending
4. Failed build → Blocked

The pytest runner encountered an internal error in the local environment, so these checks were verified directly using Python.
The repository also contains automated pytest tests for release-readiness and CI health assessment logic, executed successfully through GitHub Actions.

## Author

Deepikalahari Devandla

M.S. Software Engineering  
Blekinge Institute of Technology, Sweden
