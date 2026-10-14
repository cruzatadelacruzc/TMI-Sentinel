from typing import Any

import httpx

from app.config import Settings
from app.core.exceptions import ProviderError
from app.core.rate_provider import RatePoint
from app.modules.bcc.html_parser import parse_bcc_widget


class BccClient:
    def __init__(
        self,
        settings: Settings,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.settings = settings
        self.transport = transport

    async def fetch_rates(self) -> list[RatePoint]:
        async with httpx.AsyncClient(
            timeout=self.settings.http_timeout_seconds,
            transport=self.transport,
            follow_redirects=True,
        ) as client:
            try:
                response = await client.get(
                    self.settings.bcc_widget_url,
                    headers={"Accept": "text/html"},
                )
                response.raise_for_status()
            except httpx.HTTPError as exc:
                raise ProviderError(f"BCC widget request failed: {exc}") from exc
        return parse_bcc_widget(response.text)