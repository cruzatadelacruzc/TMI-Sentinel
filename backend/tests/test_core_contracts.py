import json
import logging

from app.core.exceptions import (
    CalculationError,
    ConfigurationError,
    DataSourceError,
    MissingRateHistory,
    ProviderError,
)
from app.core.logging import JsonFormatter


def test_json_formatter_emits_required_fields() -> None:
    record = logging.LogRecord(
        name="app.modules.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="structured event",
        args=(),
        exc_info=None,
    )

    event = json.loads(JsonFormatter().format(record))

    assert event["timestamp"]
    assert event["level"] == "INFO"
    assert event["module"] == "app.modules.test"
    assert event["message"] == "structured event"


def test_domain_exception_inheritance() -> None:
    assert issubclass(ProviderError, DataSourceError)
    assert issubclass(MissingRateHistory, CalculationError)
    assert issubclass(ConfigurationError, Exception)