DEFAULT_INTERVAL_MINUTES = 60


def resolve_interval(
    environment_interval: int | None, stored_interval: int | None
) -> int:
    if environment_interval is not None:
        return environment_interval
    if stored_interval is not None:
        return stored_interval
    return DEFAULT_INTERVAL_MINUTES