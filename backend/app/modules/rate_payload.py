from datetime import UTC, datetime
from typing import Any

from app.core.exceptions import ProviderError
from app.core.rate_provider import RatePoint

_COLLECTION_KEYS = ("data", "rates", "tasas", "results", "items")
_CURRENCY_KEYS = ("currency", "moneda", "code", "codigo", "symbol", "ticker")
_RATE_KEYS = ("rate", "tasa", "valor", "exchange_rate", "cambio")
_BUY_KEYS = ("buy", "compra", "bid")
_SELL_KEYS = ("sell", "venta", "ask")
_DATE_KEYS = ("observed_at", "timestamp", "date", "fecha", "updated_at", "as_of")


def _first(row: dict[str, Any], keys: tuple[str, ...]) -> Any:
    return next((row[key] for key in keys if row.get(key) is not None), None)


def _number(value: Any) -> float | None:
    if value is None:
        return None
    try:
        number = float(str(value).strip().replace(",", "."))
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _observed_at(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value.replace(tzinfo=UTC) if value.tzinfo is None else value
    if value:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            return parsed.replace(tzinfo=UTC) if parsed.tzinfo is None else parsed
        except ValueError:
            for date_format in ("%d/%m/%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(str(value), date_format).replace(
                        tzinfo=UTC
                    )
                except ValueError:
                    continue
    return datetime.now(UTC)


def _rows(payload: Any) -> list[dict[str, Any]]:
    for _ in range(5):
        if isinstance(payload, list):
            return [row for row in payload if isinstance(row, dict)]
        if not isinstance(payload, dict):
            break
        nested = next(
            (payload[key] for key in _COLLECTION_KEYS if key in payload),
            None,
        )
        if nested is not None:
            payload = nested
            continue
        if any(key in payload for key in (*_CURRENCY_KEYS, *_RATE_KEYS)):
            return [payload]
        return [
            {"currency": currency, **value}
            for currency, value in payload.items()
            if isinstance(value, dict)
        ]
    raise ProviderError("Provider response does not contain a rates collection")


def parse_rate_payload(payload: Any, source: str) -> list[RatePoint]:
    rates = []
    for row in _rows(payload):
        currency_value = _first(row, _CURRENCY_KEYS)
        if isinstance(currency_value, dict):
            currency_value = _first(currency_value, ("code", "codigo", "name"))
        if currency_value is None:
            continue
        currency = str(currency_value).strip().upper()
        if not currency:
            continue
        buy_rate = _number(_first(row, _BUY_KEYS))
        sell_rate = _number(_first(row, _SELL_KEYS))
        explicit_rate = _number(_first(row, _RATE_KEYS))
        values = [value for value in (buy_rate, sell_rate) if value is not None]
        rate = explicit_rate or (sum(values) / len(values) if values else None)
        if rate is None:
            continue
        rates.append(
            RatePoint(
                currency=currency,
                rate=rate,
                observed_at=_observed_at(_first(row, _DATE_KEYS)),
                source=source,
                variant="default",
                buy_rate=buy_rate,
                sell_rate=sell_rate,
            )
        )
    if not rates:
        raise ProviderError("Provider response contains no usable rate records")
    return rates