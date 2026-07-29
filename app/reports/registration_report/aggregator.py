def aggregate_report_data(registration_data, deposit_data):
    """
    Объединяет данные регистраций и депозитов
    в единый отчет по странам.
    """

    countries = set()

    countries.update(registration_data.keys())
    countries.update(deposit_data.keys())

    result = {}

    for country in countries:

        result[country] = {

            "registrations": {
                "aff": 0,
                "org": 0
            },

            "ftd": {
                "aff": 0,
                "org": 0
            },

            "deposits": {
                "count": 0,
                "sum": 0
            },

            "agent_279": {
                "count": 0,
                "sum_report": 0,
                "sum_payment": 0,
                "currency": None,
                "subagents": 0
            }
        }


        # Добавляем регистрации

        if country in registration_data:

            result[country]["registrations"] = (
                registration_data[country]["registrations"]
            )

            result[country]["ftd"] = (
                registration_data[country]["ftd"]
            )


        # Добавляем депозиты

        if country in deposit_data:

            result[country]["deposits"] = (
                deposit_data[country]["deposits"]
            )

            result[country]["agent_279"] = (
                deposit_data[country]["agent_279"]
            )


    return result