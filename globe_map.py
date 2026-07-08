"""
Globe map for Viably — shows country origins of evidence.
Extracts country data from trial facility countries, patent jurisdictions,
and regulatory agencies. Renders flag emojis and a country grid.
"""
from typing import Any


# ISO country code → flag emoji
COUNTRY_FLAGS = {
    "US": "🇺🇸", "GB": "🇬🇧", "DE": "🇩🇪", "FR": "🇫🇷", "JP": "🇯🇵",
    "CN": "🇨🇳", "CA": "🇨🇦", "AU": "🇦🇺", "IT": "🇮🇹", "ES": "🇪🇸",
    "NL": "🇳🇱", "SE": "🇸🇪", "CH": "🇨🇭", "KR": "🇰🇷", "IN": "🇮🇳",
    "BR": "🇧🇷", "DK": "🇩🇰", "BE": "🇧🇪", "AT": "🇦🇹", "NO": "🇳🇴",
    "FI": "🇫🇮", "IE": "🇮🇪", "PT": "🇵🇹", "PL": "🇵🇱", "RU": "🇷🇺",
    "IL": "🇮🇱", "SG": "🇸🇬", "TW": "🇹🇼", "HK": "🇭🇰", "NZ": "🇳🇿",
    "ZA": "🇿🇦", "MX": "🇲🇽", "AR": "🇦🇷", "CL": "🇨🇱", "CO": "🇨🇴",
    "TR": "🇹🇷", "SA": "🇸🇦", "AE": "🇦🇪", "EG": "🇪🇬", "TH": "🇹🇭",
    "MY": "🇲🇾", "ID": "🇮🇩", "PH": "🇵🇭", "VN": "🇻🇳",
    # Patent office codes
    "WO": "🌐", "EP": "🇪🇺",
    # Regulatory
    "FDA": "🇺🇸", "EMA": "🇪🇺",
}


def _country_name(code: str) -> str:
    """Convert ISO code to country name."""
    names = {
        "US": "United States", "GB": "UK", "DE": "Germany", "FR": "France",
        "JP": "Japan", "CN": "China", "CA": "Canada", "AU": "Australia",
        "IT": "Italy", "ES": "Spain", "NL": "Netherlands", "SE": "Sweden",
        "CH": "Switzerland", "KR": "South Korea", "IN": "India", "BR": "Brazil",
        "DK": "Denmark", "BE": "Belgium", "AT": "Austria", "NO": "Norway",
        "FI": "Finland", "IE": "Ireland", "PT": "Portugal", "PL": "Poland",
        "IL": "Israel", "SG": "Singapore", "TW": "Taiwan", "NZ": "New Zealand",
        "WO": "International", "EP": "Europe",
        "FDA": "US (FDA)", "EMA": "EU (EMA)",
    }
    return names.get(code, code)


def extract_countries(
    papers: list[dict],
    trials: list[dict],
    drugs: list[dict],
    regulatory: list[dict] | None = None,
    patents: list[dict] | None = None,
) -> dict[str, int]:
    """
    Extract country codes and their record counts from evidence.

    Sources:
    - Trials: facilityCountries field
    - Patents: countryCode field
    - Regulatory: agency field (FDA→US, EMA→EU)
    - Papers: no country data available without authorsMetadata include
    """
    if regulatory is None:
        regulatory = []
    if patents is None:
        patents = []

    counts: dict[str, int] = {}

    for t in trials:
        for cc in t.get("facilityCountries", []) or []:
            cc = cc.upper()
            counts[cc] = counts.get(cc, 0) + 1

    for p in patents:
        cc = (p.get("countryCode") or "").upper()
        if cc:
            counts[cc] = counts.get(cc, 0) + 1

    for r in regulatory:
        agency = (r.get("agency") or "").upper()
        if agency:
            counts[agency] = counts.get(agency, 0) + 1

    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))


def build_globe_html(countries: dict[str, int]) -> str:
    """
    Build an HTML globe visualization showing country flags and counts.
    If no country data, returns a message.
    """
    if not countries:
        return "<p style='text-align:center;color:#888;padding:20px'>No country data available from the results.</p>"

    rows = []
    for code, count in countries.items():
        flag = COUNTRY_FLAGS.get(code, "🏳️")
        name = _country_name(code)
        rows.append(
            f"<div style='display:inline-flex;align-items:center;gap:6px;"
            f"background:#f1f5f9;padding:6px 12px;border-radius:8px;margin:4px;"
            f"font-size:13px'>"
            f"<span style='font-size:18px'>{flag}</span>"
            f"<span style='font-weight:600;color:#334155'>{name}</span>"
            f"<span style='background:#6366f1;color:white;padding:1px 7px;"
            f"border-radius:10px;font-size:11px;font-weight:600'>{count}</span>"
            f"</div>"
        )

    total_countries = len(countries)
    total_records = sum(countries.values())

    html = [
        "<div style='font-family:system-ui,sans-serif;max-width:700px;margin:0 auto;text-align:center'>",
        # Mini globe icon
        "<div style='font-size:40px;margin-bottom:8px'>🌍</div>",
        f"<p style='color:#64748b;font-size:12px;margin-bottom:12px'>"
        f"Evidence originates from <strong>{total_countries} countries/regions</strong> "
        f"({total_records} location-tagged records)</p>",
        "<div style='line-height:1.8'>",
        *rows,
        "</div>",
        "</div>",
    ]
    return "\n".join(html)


def has_country_data(
    trials: list[dict],
    patents: list[dict] | None = None,
    regulatory: list[dict] | None = None,
) -> bool:
    """Check if any records have extractable country data."""
    if patents is None:
        patents = []
    if regulatory is None:
        regulatory = []
    for t in trials:
        if t.get("facilityCountries"):
            return True
    for p in patents:
        if p.get("countryCode"):
            return True
    for r in regulatory:
        if r.get("agency"):
            return True
    return False
