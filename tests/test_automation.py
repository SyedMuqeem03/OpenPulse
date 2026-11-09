from openpulse.automation import build_commit_message, should_commit


def test_should_commit_true_for_meaningful_updates() -> None:
    summary = {
        "new_total": 5,
        "updated_total": 2,
        "failed_collectors": 0,
    }
    assert should_commit(summary) is True


def test_should_commit_false_for_no_changes() -> None:
    summary = {
        "new_total": 0,
        "updated_total": 0,
        "failed_collectors": 0,
    }
    assert should_commit(summary) is False


def test_build_commit_message_uses_conventional_style() -> None:
    summary = {"new_security": 3, "new_devops": 2, "updated_total": 1, "failed_collectors": 0}
    message = build_commit_message(summary)
    assert message.startswith("feat:")
    assert "3" in message
    assert "daily intelligence" in message.lower()
