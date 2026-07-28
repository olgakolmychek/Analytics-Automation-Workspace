GEO_MAPPING = {
    "bolivia": "Bolivia",
    "боливия": "Bolivia",

    "mexico": "Mexico",
    "мексика": "Mexico",

    "guatemala": "Guatemala",
    "гватемала": "Guatemala",

    "jamaica": "Jamaica",
    "ямайка": "Jamaica",
}


def detect_geo(country_name):
    """
    Определяет стандартное название GEO.
    """

    if not country_name:
        return None

    country = country_name.strip().lower()

    return GEO_MAPPING.get(country)