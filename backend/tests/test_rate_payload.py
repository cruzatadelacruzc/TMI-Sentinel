from app.modules.rate_payload import parse_rate_payload


def test_parses_nested_json_with_buy_and_sell_values() -> None:
    rates = parse_rate_payload(
        {
            "data": {
                "rates": [
                    {
                        "currency": {"code": "usd"},
                        "buy": "120.00",
                        "sell": "125.00",
                        "date": "2026-10-14T10:00:00Z",
                    }
                ]
            }
        },
        "fixture",
    )

    assert rates[0].currency == "USD"
    assert rates[0].rate == 122.5
    assert rates[0].buy_rate == 120
    assert rates[0].sell_rate == 125
    assert rates[0].source == "fixture"