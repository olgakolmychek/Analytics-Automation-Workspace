import gspread
from gspread.utils import rowcol_to_a1

from app.reports.registration_report.geo_mapper import get_sheet_name


TEMPLATE_SHEET = "Шаблон"

TEMPLATE_WIDTH = 5
TEMPLATE_HEIGHT = 14

MAX_WEEKS = 15


def write_report(
    report_data,
    sheets_config,
    credentials,
):
    """
    Записывает Registration Report.
    Каждый GEO = отдельный лист.
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

    for country, data in report_data.items():

        sheet_name = get_sheet_name(
            country
        )

        sheet = get_or_create_sheet(
            spreadsheet,
            sheet_name,
        )

        add_week_block(
            spreadsheet,
            sheet,
        )

        write_values(
            sheet,
            data,
        )


def get_or_create_sheet(
    spreadsheet,
    sheet_name,
):
    """
    Возвращает GEO-лист.
    Если листа нет — создаёт.
    """

    try:
        return spreadsheet.worksheet(
            sheet_name
        )

    except gspread.exceptions.WorksheetNotFound:

        return spreadsheet.add_worksheet(
            title=sheet_name,
            rows=100,
            cols=200,
        )


def add_week_block(
    spreadsheet,
    sheet,
):
    """
    Добавляет новый недельный блок.
    """

    weeks = get_weeks_count(
        sheet
    )

    if weeks >= MAX_WEEKS:

        # сначала добавляем новый блок слева

        insert_columns_left(
            spreadsheet,
            sheet,
        )

        copy_template(
            spreadsheet,
            sheet,
            1,
        )

        # потом удаляем самый старый справа

        remove_oldest_week(
            sheet,
        )

    else:

        start_column = (
            weeks
            * TEMPLATE_WIDTH
            + 1
        )

        copy_template(
            spreadsheet,
            sheet,
            start_column,
        )


def copy_template(
    spreadsheet,
    sheet,
    start_column,
):
    """
    Копирует Шаблон A1:E14
    в нужный недельный блок.
    """

    template = spreadsheet.worksheet(
        TEMPLATE_SHEET
    )

    spreadsheet.batch_update(
        {
            "requests": [
                {
                    "copyPaste": {
                        "source": {
                            "sheetId": template.id,
                            "startRowIndex": 0,
                            "endRowIndex": TEMPLATE_HEIGHT,
                            "startColumnIndex": 0,
                            "endColumnIndex": TEMPLATE_WIDTH,
                        },
                        "destination": {
                            "sheetId": sheet.id,
                            "startRowIndex": 0,
                            "endRowIndex": TEMPLATE_HEIGHT,
                            "startColumnIndex": start_column - 1,
                            "endColumnIndex": (
                                start_column - 1
                                + TEMPLATE_WIDTH
                            ),
                        },
                        "pasteType": "PASTE_NORMAL",
                    }
                }
            ]
        }
    )


def get_weeks_count(sheet):
    """
    Считает количество недельных блоков.
    """

    values = sheet.row_values(1)

    weeks = 0

    for col in range(
        0,
        MAX_WEEKS * TEMPLATE_WIDTH,
        TEMPLATE_WIDTH,
    ):

        block = values[
            col:col + TEMPLATE_WIDTH
        ]

        if not any(block):
            break

        weeks += 1

    return weeks


def remove_oldest_week(sheet):
    """
    Удаляет крайний правый старый блок.
    """

    weeks = get_weeks_count(
        sheet
    )

    start_column = (
        weeks
        * TEMPLATE_WIDTH
        - TEMPLATE_WIDTH
        + 1
    )

    sheet.delete_columns(
        start_column,
        TEMPLATE_WIDTH,
    )


def insert_columns_left(
    spreadsheet,
    sheet,
):
    """
    Добавляет 5 колонок слева.
    """

    spreadsheet.batch_update(
        {
            "requests": [
                {
                    "insertDimension": {
                        "range": {
                            "sheetId": sheet.id,
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": TEMPLATE_WIDTH,
                        },
                        "inheritFromBefore": False,
                    }
                }
            ]
        }
    )


def write_values(
    sheet,
    data,
):
    """
    Записывает только значения.
    Формулы из шаблона сохраняются.
    """

    weeks = get_weeks_count(
        sheet
    )

    # колонка значений (B, G, L...)

    value_column = (
        (weeks - 1)
        * TEMPLATE_WIDTH
        + 2
    )


    updates = {

        # Дата
        1: data.get(
            "date",
            ""
        ),


        # Регистрации
        3: data["registrations"]["aff"],

        4: data["registrations"]["org"],


        # FTD

        6: data["ftd"]["aff"],

        7: data["ftd"]["org"],


        # Депозиты

        11: data["deposits"]["sum"],

        12: data["deposits"]["count"],
    }


    for row, value in updates.items():

        sheet.update(
        values=[
            [value]
        ],
        range_name=rowcol_to_a1(
            row,
            value_column,
        ),
    )