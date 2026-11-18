
from release_health import assess_release_health


def make_run(status, conclusion):
    return [{
        "status": status,
        "conclusion": conclusion,
        "created_at": "2026-11-18T09:22:20Z"
    }]


def test_ci_success():
    result = assess_release_health(
        make_run("completed", "success")
    )
    assert result["status"] == "CI Passed"
    assert result["deployment"] == "Unknown"


def test_ci_failure():
    result = assess_release_health(
        make_run("completed", "failure")
    )
    assert result["status"] == "CI Failed"


def test_ci_pending():
    result = assess_release_health(
        make_run("in_progress", None)
    )
    assert result["status"] == "Pending"


def test_missing_evidence():
    result = assess_release_health([])
    assert result["status"] == "Insufficient Evidence"


def test_inconclusive_result():
    result = assess_release_health(
        make_run("completed", "cancelled")
    )
    assert result["status"] == "Inconclusive"


def test_most_recent_workflow():
    runs = [
        {
            "status": "completed",
            "conclusion": "failure",
            "created_at": "2026-11-17T09:00:00Z"
        },
        {
            "status": "completed",
            "conclusion": "success",
            "created_at": "2026-11-18T09:00:00Z"
        }
    ]

    result = assess_release_health(runs)
    assert result["status"] == "CI Passed"
