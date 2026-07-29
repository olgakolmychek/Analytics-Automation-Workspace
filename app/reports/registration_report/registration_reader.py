from app.connectors.excel_connector import load_excel


def normalize_traffic_source(source):
    """
    Приводит источник трафика к формату aff/org.
    """

    if not source:
        return None

    source = str(source).lower()

    if "aff" in source:
        return "aff"

    if "org" in source:
        return "org"

    return None


def read_registration_files(registration_files):
    """
    Читает все файлы регистраций и объединяет статистику по странам.
    """

    countries = {}

    for file in registration_files:

        print(f"Обработка файла регистраций: {file.name}")

        rows = load_excel(file)

        headers = rows[0]

        country_col = headers.index("Страна")
        traffic_col = headers.index("Источник трафика")
        registrations_col = headers.index("Всего регистраций")
        ftd_col = headers.index(
            "Количество регистраций за период, из них с первым депозитом"
        )

        for row in rows[1:]:

            country = row[country_col]

            traffic = normalize_traffic_source(
                row[traffic_col]
            )

            registrations = row[registrations_col] or 0
            ftd = row[ftd_col] or 0

            # Если источник не aff/org — пропускаем
            if not traffic:
                continue

            if country not in countries:

                countries[country] = {
                    "registrations": {
                        "aff": 0,
                        "org": 0
                    },
                    "ftd": {
                        "aff": 0,
                        "org": 0
                    }
                }

            countries[country]["registrations"][traffic] += registrations

            countries[country]["ftd"][traffic] += ftd

    return countries