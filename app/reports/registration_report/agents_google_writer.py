import gspread


AGENTS_SHEET = "Агенты"


HEADERS = [
    "Дата",
    "GEO",
    "Агент",
    "Количество депозитов",
    "Сумма в валюте отчета",
    "Сумма платежей",
    "Валюта",
    "Количество субагентов",
]


def write_agents_report(
    report_data,
    sheets_config,
    credentials,
):
    """
    Записывает данные агентов
    в отдельный лист Агенты.

    Заголовок создается только один раз.
    Каждая новая генерация добавляется ниже.
    """

    client = gspread.service_account(
        filename=credentials
    )


    config = (
        sheets_config["google_sheets"]
        ["projects"]
        ["1xBet"]
        ["reports"]
        ["registration"]
    )


    spreadsheet = client.open_by_key(
        config["id"]
    )


    sheet = get_or_create_agents_sheet(
        spreadsheet
    )


    write_agents_data(
        sheet,
        report_data
    )



def get_or_create_agents_sheet(
    spreadsheet,
):
    """
    Создает лист Агенты,
    если его нет.
    """

    try:

        return spreadsheet.worksheet(
            AGENTS_SHEET
        )


    except gspread.exceptions.WorksheetNotFound:


        return spreadsheet.add_worksheet(
            title=AGENTS_SHEET,
            rows=1000,
            cols=100,
        )



def write_agents_data(
    sheet,
    report_data,
):
    """
    Записывает агентские данные.

    Заголовок создается только если лист пустой.
    Каждая новая неделя добавляется ниже.
    """

    existing_values = sheet.get_all_values()


    # Проверяем, реально ли лист пустой
    is_empty = (
        len(existing_values) == 0
        or (
            len(existing_values) == 1
            and not any(existing_values[0])
        )
    )


    rows = []


    if is_empty:

        rows.append(
            [
                "Дата",
                "GEO",
                "Агент",
                "Количество депозитов",
                "Сумма в валюте отчета",
                "Сумма платежей",
                "Валюта",
                "Количество субагентов",
            ]
        )


    for country, data in report_data.items():

        agents = data.get(
            "agents",
            {}
        )


        for agent_id, agent_data in agents.items():

            rows.append(
                [
                    data.get(
                        "date",
                        ""
                    ),

                    country,

                    agent_id,

                    agent_data.get(
                        "count",
                        0
                    ),

                    agent_data.get(
                        "sum_report",
                        0
                    ),

                    agent_data.get(
                        "sum_payment",
                        0
                    ),

                    agent_data.get(
                        "currency",
                        ""
                    ),

                    agent_data.get(
                        "subagents",
                        0
                    ),
                ]
            )


    if not rows:
        return


    # если лист был пустой — начинаем с A1
    # если нет — добавляем после последней строки

    if is_empty:

        start_row = 1

    else:

        start_row = len(existing_values) + 1


    sheet.update(
        f"A{start_row}",
        rows,
    )