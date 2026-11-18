
from data_sources import (
    normalize_github_runs,
    normalize_sample_records,
)


def test_github_normalization():
    runs = [{
        "commit_sha": "abc1234",
        "status": "completed",
        "conclusion": "success",
        "created_at": "2026-11-18T10:00:00Z",
    }]

    result = normalize_github_runs(runs)

    assert len(result) == 1
    assert result[0]["source"] == "GitHub Actions"
    assert result[0]["identifier"] == "abc1234"
    assert result[0]["result"] == "success"


def test_sample_normalization():
    records = [{
        "reference": "VER-001",
        "status": "completed",
        "result": "failure",
        "timestamp": "2026-11-18T11:00:00Z",
    }]

    result = normalize_sample_records(records)

    assert len(result) == 1
    assert result[0]["source"] == "Sample Verification System"
    assert result[0]["identifier"] == "VER-001"
    assert result[0]["result"] == "failure"


def test_empty_sources():
    assert normalize_github_runs([]) == []
    assert normalize_sample_records([]) == []
