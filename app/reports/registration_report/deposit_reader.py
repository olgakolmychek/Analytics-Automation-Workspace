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
    Читает файлы депозитов.

    Возвращает:
    - статистику депозитов по GEO
    - данные агентов
    - период отчета
    """

    countries = {}

    report_dates = []


    for file in deposit_files:

        print(
            f"Обработка файла депозитов: {file.name}"
        )


        rows = load_excel(file)

        headers = rows[0]


        country_col = headers.index(
            "Страна аккаунта"
        )

        report_sum_col = headers.index(
            "Сумма в валюте отчета"
        )


        date_col = headers.index(
            "Дата создания"
        )


        agent_col = headers.index(
            "Id Агента"
        )

        payment_sum_col = headers.index(
            "Сумма в валюте платежа"
        )

        payment_currency_col = headers.index(
            "Валюта платежа"
        )

        subagent_col = headers.index(
            "Субагент"
        )


        for row in rows[1:]:


            transaction_date = row[date_col]

            if transaction_date:

                report_dates.append(
                    transaction_date
                )


            country = row[country_col]


            if not country:
                continue


            if country not in countries:

                countries[country] = {

                    "deposits": {
                        "count": 0,
                        "sum": 0
                    },


                    "agents": {}

                }


            #
            # Общие депозиты GEO
            #

            countries[country]["deposits"]["count"] += 1


            countries[country]["deposits"]["sum"] += (
                row[report_sum_col] or 0
            )



            #
            # Агенты
            #

            agent_id = row[agent_col]

            if agent_id != 279:
                continue

            if agent_id not in countries[country]["agents"]:

                countries[country]["agents"][agent_id] = {

                    "count": 0,

                    "sum_report": 0,

                    "sum_payment": 0,

                    "currency": None,

                    "subagents": set()

                }

            agent_data = (
                countries[country]
                ["agents"]
                [agent_id]
            )

            agent_data["count"] += 1

            agent_data["sum_report"] += (
                row[report_sum_col] or 0
            )

            agent_data["sum_payment"] += (
                row[payment_sum_col] or 0
            )

            if not agent_data["currency"]:

                agent_data["currency"] = (
                    row[payment_currency_col]
                )

            subagent = get_first_word(
                row[subagent_col]
            )

            if subagent:

                agent_data["subagents"].add(
                    subagent
                )

    #
    # Подготовка данных
    #

    for country_data in countries.values():


        for agent_data in country_data["agents"].values():

            agent_data["subagents"] = len(
                agent_data["subagents"]
            )



    #
    # Период отчета
    #

    period = None


    if report_dates:

        period = (
        f"{min(report_dates)}"
        f" - "
        f"{max(report_dates)}"
        )


    return {

        "countries": countries,

        "period": period

    }