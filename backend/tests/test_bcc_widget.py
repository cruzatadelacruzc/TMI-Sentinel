from app.modules.bcc.html_parser import parse_bcc_widget


def test_parses_widget_currencies_variants_and_effective_date() -> None:
    html = """
    <table>
      <thead><tr><th>Currency</th><th>Official</th><th>Cards</th><th>Cash</th></tr></thead>
      <tbody>
        <tr><td>Bandera CAD CAD</td><td>16.89</td><td>84.47</td><td>497.68</td></tr>
        <tr><td>Bandera EUR EUR</td><td>26.87</td><td>134.33</td><td>791.42</td></tr>
        <tr><td>Bandera USD USD</td><td>24.00</td><td>120.00</td><td>707.00</td></tr>
      </tbody>
    </table>
    <p>Vigente para operaciones del día: 14/10/2026</p>
    """

    rates = parse_bcc_widget(html)

    assert len(rates) == 9
    assert rates[0].currency == "CAD"
    assert rates[0].rate == 16.89
    assert rates[0].variant == "official"
    assert rates[0].observed_at.isoformat() == "2026-10-14T00:00:00+00:00"
    assert rates[2].variant == "cash"
    assert rates[2].rate == 497.68