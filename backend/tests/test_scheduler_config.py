from app.scheduler.config import resolve_interval


def test_environment_interval_has_precedence() -> None:
    assert resolve_interval(15, 30) == 15


def test_stored_interval_is_used_without_environment_override() -> None:
    assert resolve_interval(None, 30) == 30


def test_default_interval_is_sixty_minutes() -> None:
    assert resolve_interval(None, None) == 60