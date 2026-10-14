import re
import unicodedata
from datetime import UTC, datetime

from bs4 import BeautifulSoup

from app.core.exceptions import ProviderError
from app.core.rate_provider import RatePoint

_CURRENCY_NAMES = {
    "dolar estadounidense": "USD",
    "dolar americano": "USD",
    "euro": "EUR",
    "dolar canadiense": "CAD",
    "libra esterlina": "GBP",
    "franco suizo": "CHF",
    "yen japones": "JPY",
    "peso mexicano": "MXN",
    "yuan chino": "CNY",
}
_NON_CURRENCY_CODES = {"BAN", "CAM", "COD", "DIV", "MON", "TAS"}


def _plain(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    return " ".join(
        "".join(char for char in decomposed if not unicodedata.combining(char))
        .lower()
        .split()
    )


def _currency(cells: list[str]) -> tuple[int, str] | None:
    for index, cell in enumerate(cells):
        codes = re.findall(r"\b[A-Z]{3}\b", cell.upper())
        code = next(
            (item for item in codes if item not in _NON_CURRENCY_CODES), None
        )
        if code:
            return index, code
        normalized = _plain(cell)
        for name, mapped_code in _CURRENCY_NAMES.items():
            if name in normalized:
                return index, mapped_code
    return None


def _number(value: str) -> float | None:
    text = value.strip().replace("\u00a0", "")
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        text = text.replace(",", ".")
    try:
        result = float(text)
    except ValueError:
        return None
    return result if result > 0 else None


def _date(text: str) -> datetime:
    match = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", text)
    if match:
        return datetime.strptime(match.group(1), "%d/%m/%Y").replace(tzinfo=UTC)
    return datetime.now(UTC)


def _variant(label: str, index: int) -> str:
    normalized = _plain(label)
    slug = re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")
    return slug or f"column_{index + 1}"


def parse_bcc_widget(html: str) -> list[RatePoint]:
    soup = BeautifulSoup(html, "html.parser")
    observed_at = _date(soup.get_text(" ", strip=True))
    rates: list[RatePoint] = []

    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        header_cells: list[str] = []
        header = table.find("thead")
        if header is not None:
            header_row = header.find("tr")
            if header_row is not None:
                header_cells = [
                    cell.get_text(" ", strip=True)
                    for cell in header_row.find_all(["th", "td"])
                ]
        if not header_cells and rows:
            first_cells = [
                cell.get_text(" ", strip=True)
                for cell in rows[0].find_all(["th", "td"])
            ]
            if first_cells and _currency(first_cells) is None:
                header_cells = first_cells

        for row in rows:
            cells = [
                cell.get_text(" ", strip=True)
                for cell in row.find_all(["th", "td"])
            ]
            if not cells:
                continue
            currency_info = _currency(cells)
            if currency_info is None:
                continue
            currency_index, currency = currency_info
            value_cells = cells[currency_index + 1 :]
            if not value_cells:
                value_cells = cells
            values = [_number(cell) for cell in value_cells]
            values = [value for value in values if value is not None]
            if not values:
                continue

            for index, value in enumerate(values):
                label_index = currency_index + index + 1
                label = (
                    header_cells[label_index]
                    if label_index < len(header_cells)
                    else ""
                )
                rates.append(
                    RatePoint(
                        currency=currency,
                        rate=value,
                        observed_at=observed_at,
                        source="bcc",
                        variant=_variant(label, index),
                        buy_rate=value if "compra" in _plain(label) else None,
                        sell_rate=value if "venta" in _plain(label) else None,
                    )
                )

    if not rates:
        raise ProviderError("BCC widget contains no recognizable exchange-rate rows")
    return rates