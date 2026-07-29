from app.connectors.excel_connector import load_excel


def get_first_word(value):
    """
    Берет первое слово из названия субагента.

    Например:
    John Smith -> John
    """

    if not value:
        return None

    return str(value).split()[0]


def read_deposit_files(deposit_files):
    """
    Читает файлы депозитов и считает статистику по странам.
    """

    countries = {}

    for file in deposit_files:

        print(f"Обработка файла депозитов: {file.name}")

        rows = load_excel(file)

        headers = rows[0]

        country_col = headers.index("Страна аккаунта")
        report_sum_col = headers.index("Сумма в валюте отчета")

        agent_col = headers.index("Id Агента")
        payment_sum_col = headers.index("Сумма в валюте платежа")
        payment_currency_col = headers.index("Валюта платежа")
        subagent_col = headers.index("Субагент")

        for row in rows[1:]:

            country = row[country_col]

            if not country:
                continue

            if country not in countries:

                countries[country] = {
                    "deposits": {
                        "count": 0,
                        "sum": 0
                    },
                    "agent_279": {
                        "count": 0,
                        "sum_report": 0,
                        "sum_payment": 0,
                        "currency": None,
                        "subagents": set()
                    }
                }

            # Общая статистика депозитов

            countries[country]["deposits"]["count"] += 1

            countries[country]["deposits"]["sum"] += (
                row[report_sum_col] or 0
            )


            # Агент 279

            if row[agent_col] == 279:

                agent_data = countries[country]["agent_279"]

                agent_data["count"] += 1

                agent_data["sum_report"] += (
                    row[report_sum_col] or 0
                )

                agent_data["sum_payment"] += (
                    row[payment_sum_col] or 0
                )

                if not agent_data["currency"]:
                    agent_data["currency"] = row[payment_currency_col]

                subagent = get_first_word(
                    row[subagent_col]
                )

                if subagent:
                    agent_data["subagents"].add(subagent)


    # set нельзя отдавать дальше,
    # превращаем в количество

    for country_data in countries.values():

        country_data["agent_279"]["subagents"] = len(
            country_data["agent_279"]["subagents"]
        )

    return countries