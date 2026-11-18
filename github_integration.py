
import requests


def fetch_workflow_runs(
    owner="deepikalahari12",
    repo="ReleaseLens"
):
    """Fetch recent GitHub Actions workflow runs."""

    url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repo}/actions/runs"
    )

    response = requests.get(
        url,
        params={"per_page": 100},
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
            "full_commit_sha": run.get("head_sha", ""),
            "branch": run.get("head_branch"),
            "status": run.get("status"),
            "conclusion": run.get("conclusion"),
            "created_at": run.get("created_at"),
            "url": run.get("html_url"),
        }
        for run in runs
    ]


def fetch_github_releases(
    owner="deepikalahari12",
    repo="ReleaseLens"
):
    """Fetch actual published GitHub releases and resolve their commits."""

    base_url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(
        f"{base_url}/releases",
        params={"per_page": 30},
        headers=headers,
        timeout=15
    )
    response.raise_for_status()

    releases = []

    for release in response.json():
        tag = release.get("tag_name")
        commit_sha = None

        if tag:
            commit_response = requests.get(
                f"{base_url}/commits/{tag}",
                headers=headers,
                timeout=15
            )
            commit_response.raise_for_status()
            commit_sha = commit_response.json().get("sha")

        releases.append({
            "version": tag,
            "name": release.get("name"),
            "commit_sha": commit_sha,
            "published_at": release.get("published_at"),
            "url": release.get("html_url"),
        })

    return releases
