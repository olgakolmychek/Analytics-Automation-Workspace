from datetime import datetime

from gspread.exceptions import WorksheetNotFound


def create_archive_sheet(
    spreadsheet,
    source_sheet_name,
):
    """
    Создает архивный лист
    дублированием рабочего листа.

    После дублирования
    все формулы заменяются
    значениями.

    Полностью сохраняются:
    - оформление
    - цвета
    - размеры
    - объединения
    - условное форматирование
    """

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    archive_name = (
        f"{source_sheet_name}_{today}"
    )

    counter = 2

    while True:

        try:

            spreadsheet.worksheet(
                archive_name
            )

            archive_name = (
                f"{source_sheet_name}_{today} ({counter})"
            )

            counter += 1

        except WorksheetNotFound:

            break

    source_sheet = spreadsheet.worksheet(
        source_sheet_name
    )

    archive_sheet = spreadsheet.duplicate_sheet(
        source_sheet.id,
        new_sheet_name=archive_name,
    )

    spreadsheet.batch_update(
        {
            "requests": [
                {
                    "copyPaste": {
                        "source": {
                            "sheetId": archive_sheet.id,
                            "startRowIndex": 0,
                            "startColumnIndex": 0,
                        },
                        "destination": {
                            "sheetId": archive_sheet.id,
                            "startRowIndex": 0,
                            "startColumnIndex": 0,
                        },
                        "pasteType": "PASTE_VALUES",
                        "pasteOrientation": "NORMAL",
                    }
                }
            ]
        }
    )

    return archive_name


def cleanup_old_archives(
    spreadsheet,
    keep_last=30,
):
    """
    Удаляет старые архивы,
    оставляя только keep_last.
    """

    for prefix in [
        "Отчет_",
        "Методы_",
    ]:

        archives = sorted(
            [
                sheet
                for sheet in spreadsheet.worksheets()
                if sheet.title.startswith(
                    prefix
                )
            ],
            key=lambda sheet: sheet.id,
        )

        while len(archives) > keep_last:

            spreadsheet.del_worksheet(
                archives.pop(0)
            )