from gspread.utils import rowcol_to_a1


TEMPLATE_SHEET = "Шаблон"

TEMPLATE_WIDTH = 5
TEMPLATE_HEIGHT = 14


def copy_template(
    spreadsheet,
    destination_sheet,
    start_column,
):
    """
    Копирует диапазон A1:E14
    с листа 'Шаблон'
    на нужный лист.
    """

    template = spreadsheet.worksheet(
        TEMPLATE_SHEET
    )

    sheet = spreadsheet.worksheet(
        destination_sheet
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
                            "endColumnIndex": start_column - 1 + TEMPLATE_WIDTH,
                        },
                        "pasteType": "PASTE_NORMAL",
                    }
                }
            ]
        }
    )


def find_next_column(sheet):
    """
    Возвращает номер первой свободной колонки
    для нового недельного отчета.
    """

    values = sheet.row_values(1)

    if not values:
        return 1

    return len(values) + 1