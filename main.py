from app.core.config_loader import load_config, get_btag_sheet_config
from app.connectors.file_connector import get_files
from app.connectors.excel_connector import load_excel, find_country
from app.connectors.google_sheets_connector import connect_google_sheet, upload_to_sheet
from app.services.geo_detector import detect_geo
from app.services.google_sheet_archive import create_archive_sheet

import time


CREDENTIALS = "credentials/focal-pager-503718-p2-82fd68b1b8f7.json"


def process_file(file_path, sheets_config):

    print("\n==============================")
    print(f"Обработка файла: {file_path}")

    rows = load_excel(file_path)

    country = find_country(rows)

    print(f"Страна из файла: {country}")

    geo = detect_geo(country)

    print(f"Определенный GEO: {geo}")

    if not geo:
        print("GEO не определен, файл пропущен")
        return

    sheet_config = get_btag_sheet_config(
        sheets_config,
        geo
    )

    spreadsheet = connect_google_sheet(
        CREDENTIALS,
        sheet_config["id"]
    )

    upload_to_sheet(
        spreadsheet,
        sheet_config["sheets"]["input"],
        rows
    )

    print("Sheet1 обновлен")

    print("Ожидание пересчета формул...")
    time.sleep(10)

    report_archive = create_archive_sheet(
        spreadsheet,
        sheet_config["sheets"]["report"]
    )

    methods_archive = create_archive_sheet(
        spreadsheet,
        sheet_config["sheets"]["methods"]
    )

    print(f"Создан архив: {report_archive}")
    print(f"Создан архив: {methods_archive}")


def main():

    settings = load_config("configs/settings.yaml")

    incoming_folder = settings["paths"]["incoming_btag"]

    sheets_config = load_config("configs/sheets.yaml")

    files = get_files(incoming_folder)

    print(f"Найдено файлов: {len(files)}")

    for file_path in files:
        process_file(
            file_path,
            sheets_config
        )


if __name__ == "__main__":
    main()