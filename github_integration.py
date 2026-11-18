
import requests


def fetch_workflow_runs(
    owner="deepikalahari12",
    repo="ReleaseLens"
):
    """Fetch recent workflow runs from a public GitHub repository."""

    url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repo}/actions/runs"
    )

    response = requests.get(
        url,
        params={"per_page": 20},
        headers={
            "Accept": "application/vnd.github+json"
        },
        timeout=15
    )

    response.raise_for_status()

    runs = response.json().get("workflow_runs", [])

    return [
        {
            "workflow": run.get("name"),
            "commit_sha": run.get("head_sha", "")[:7],
            "branch": run.get("head_branch"),
            "status": run.get("status"),
            "conclusion": run.get("conclusion"),
            "created_at": run.get("created_at"),
            "url": run.get("html_url"),
        }
        for run in runs
    ]
