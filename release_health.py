
def assess_release_health(workflow_runs):
    """
    Assess CI health using GitHub Actions evidence.

    A successful CI run does not establish
    deployment readiness or deployment success.
    """

    if not workflow_runs:
        return {
            "status": "Insufficient Evidence",
            "reason": "No CI workflow evidence found.",
            "deployment": "Unknown"
        }

    # Use the most recent workflow record.
    latest = sorted(
        workflow_runs,
        key=lambda run: run.get("created_at") or "",
        reverse=True
    )[0]

    status = latest.get("status")
    conclusion = latest.get("conclusion")

    if status != "completed":
        health = "Pending"
        reason = "CI workflow execution is incomplete."

    elif conclusion == "success":
        health = "CI Passed"
        reason = (
            "The latest CI workflow completed "
            "successfully. Deployment readiness "
            "has not been verified."
        )

    elif conclusion == "failure":
        health = "CI Failed"
        reason = "The latest CI workflow failed."

    else:
        health = "Inconclusive"
        reason = (
            "The workflow completed without "
            "a confirmed success or failure."
        )

    return {
        "status": health,
        "reason": reason,
        "deployment": "Unknown"
    }
