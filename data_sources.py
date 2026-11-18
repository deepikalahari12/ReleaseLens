
def normalize_github_runs(runs):
    """Convert GitHub Actions runs into a common format."""
    return [
        {
            "source": "GitHub Actions",
            "identifier": run.get("commit_sha"),
            "status": run.get("status"),
            "result": run.get("conclusion"),
            "timestamp": run.get("created_at"),
        }
        for run in runs
    ]


def normalize_sample_records(records):
    """Convert sample verification records into the same format."""
    return [
        {
            "source": "Sample Verification System",
            "identifier": record.get("reference"),
            "status": record.get("status"),
            "result": record.get("result"),
            "timestamp": record.get("timestamp"),
        }
        for record in records
    ]
