from typing import Any

import httpx

from app.config import Settings
from app.core.exceptions import ProviderError
from app.core.rate_provider import RatePoint
from app.modules.rate_payload import parse_rate_payload


class ElToqueClient:
    def __init__(
        self,
        settings: Settings,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.settings = settings
        self.transport = transport

    async def fetch_rates(self) -> list[RatePoint]:
        headers = {"Accept": "application/json"}
        token = self.settings.el_toque_api_token
        if not token:
            raise ProviderError("EL_TOQUE_API_TOKEN is required to fetch rates")
        value = f"{self.settings.el_toque_auth_scheme} {token}".strip()
        headers[self.settings.el_toque_auth_header] = value
        async with httpx.AsyncClient(
            timeout=self.settings.http_timeout_seconds,
            transport=self.transport,
        ) as client:
            try:
                response = await client.get(
                    self.settings.el_toque_api_url, headers=headers
                )
                response.raise_for_status()
                payload: Any = response.json()
            except (httpx.HTTPError, ValueError) as exc:
                raise ProviderError(f"El Toque request failed: {exc}") from exc
        return parse_rate_payload(payload, "eltoque")