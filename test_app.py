
from app import calculate_readiness


# Test 1: Release is ready
def test_ready_release():
    release = {
        "build_status": "Passed",
        "test_status": "Passed"
    }

    assert calculate_readiness(release) == "Ready"


# Test 2: Release is blocked due to failed tests
def test_blocked_release():
    release = {
        "build_status": "Passed",
        "test_status": "Failed"
    }

    assert calculate_readiness(release) == "Blocked"


# Test 3: Release is pending
def test_pending_release():
    release = {
        "build_status": "Running",
        "test_status": "Pending"
    }

    assert calculate_readiness(release) == "Pending"


# Test 4: Release is blocked due to failed build
def test_failed_build():
    release = {
        "build_status": "Failed",
        "test_status": "Pending"
    }

    assert calculate_readiness(release) == "Blocked"
