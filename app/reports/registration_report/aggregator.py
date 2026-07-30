def aggregate_report_data(
    registration_data,
    deposit_data
):
    """
    Объединяет данные регистраций и депозитов
    в единый отчет по странам.
    """


    countries = set()


    countries.update(
        registration_data.keys()
    )

    countries.update(
        deposit_data["countries"].keys()
    )


    result = {}


    for country in countries:


        result[country] = {

            "date": deposit_data.get(
                "period",
                ""
            ),


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


            "agents": {}

        }



        #
        # Регистрации
        #

        if country in registration_data:


            result[country]["registrations"] = (
                registration_data[country]["registrations"]
            )


            result[country]["ftd"] = (
                registration_data[country]["ftd"]
            )



        #
        # Депозиты и агенты
        #

        if country in deposit_data["countries"]:


            result[country]["deposits"] = (
                deposit_data["countries"][country]["deposits"]
            )


            result[country]["agents"] = (
                deposit_data["countries"][country]["agents"]
            )


    return result