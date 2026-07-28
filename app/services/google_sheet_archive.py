from datetime import datetime
from gspread.exceptions import WorksheetNotFound


def create_archive_sheet(spreadsheet, source_sheet_name):

    today = datetime.now().strftime("%Y-%m-%d")

    archive_name = f"{source_sheet_name}_{today}"

    counter = 2

    while True:
        try:
            spreadsheet.worksheet(archive_name)
            archive_name = f"{source_sheet_name}_{today} ({counter})"
            counter += 1

        except WorksheetNotFound:
            break

    source = spreadsheet.worksheet(source_sheet_name)

    data = source.get_all_values()

    # Убираем столбец AD из архива
    ad_index = 29

    data = [
        row[:ad_index] + row[ad_index + 1:]
        for row in data
    ]

    new_sheet = spreadsheet.add_worksheet(
        title=archive_name,
        rows=max(len(data), 100),
        cols=max(len(data[0]), 20)
    )

    new_sheet.update(
        values=data,
        range_name="A1"
    )

    return archive_name