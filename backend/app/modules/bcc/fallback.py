from typing import Any

import httpx

from app.config import Settings
from app.core.exceptions import ProviderError
from app.core.rate_provider import RatePoint
from app.modules.rate_payload import parse_rate_payload


class BccFallbackClient:
    """Optional JSON adapter for a third-party rate service."""

    def __init__(
        self,
        settings: Settings,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.settings = settings
        self.transport = transport

    async def fetch_rates(self) -> list[RatePoint]:
        url = self.settings.bcc_fallback_api_url
        if not url:
            raise ProviderError("No BCC fallback provider URL is configured")
        headers = {"Accept": "application/json"}
        if self.settings.bcc_fallback_api_token:
            headers[self.settings.bcc_fallback_auth_header] = (
                f"{self.settings.bcc_fallback_auth_scheme} "
                f"{self.settings.bcc_fallback_api_token}"
            ).strip()
        async with httpx.AsyncClient(
            timeout=self.settings.http_timeout_seconds,
            transport=self.transport,
        ) as client:
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                payload: Any = response.json()
            except (httpx.HTTPError, ValueError) as exc:
                raise ProviderError(f"BCC fallback request failed: {exc}") from exc
        points = parse_rate_payload(payload, "bcc_fallback")
        return [
            RatePoint(
                currency=point.currency,
                rate=point.rate,
                observed_at=point.observed_at,
                source="bcc_fallback",
                variant=point.variant,
                buy_rate=point.buy_rate,
                sell_rate=point.sell_rate,
            )
            for point in points
        ]