import gspread
from gspread.utils import rowcol_to_a1


AGENTS_SHEET = "Агенты"


def write_agents_report(
    report_data,
    sheets_config,
    credentials,
):
    """
    Записывает данные агентов
    в отдельный лист Агенты.
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

    Каждая новая неделя
    добавляется ниже.
    """

    rows = []


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


    if len(rows) <= 1:
        return


    next_row = len(
        sheet.get_all_values()
    ) + 1


    sheet.update(
        f"A{next_row}",
        rows
    )