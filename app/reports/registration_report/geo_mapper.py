GEO_NAMES = {
    "Mexico": "Мексика",
    "Guatemala": "Гватемала",
    "Bolivia": "Боливия",
    "Jamaica": "Ямайка",
}


def get_sheet_name(country):
    return GEO_NAMES.get(
        country,
        country,
    )