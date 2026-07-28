from app.core.config_loader import load_config, get_btag_sheet_config
from app.connectors.file_connector import get_latest_file
from app.connectors.excel_connector import load_excel, find_country
from app.connectors.google_sheets_connector import (
    connect_google_sheet,
    upload_to_sheet,
)
from app.services.geo_detector import detect_geo
from app.services.google_sheet_archive import create_archive_sheet

import time

CREDENTIALS_FILE = "credentials/focal-pager-503718-p2-82fd68b1b8f7.json"


def main():

    settings = load_config("configs/settings.yaml")

    incoming_folder = settings["paths"]["incoming_btag"]

    file_path = get_latest_file(incoming_folder)

    print(f"Найден файл: {file_path}")

    rows = load_excel(file_path)

    country = find_country(rows)

    print(f"Страна из файла: {country}")

    geo = detect_geo(country)

    print(f"Определенный GEO: {geo}")

    if geo is None:
        raise ValueError("Не удалось определить GEO.")

    sheets_config = load_config("configs/sheets.yaml")

    sheet_config = get_btag_sheet_config(
        sheets_config,
        geo
    )

    spreadsheet = connect_google_sheet(
        CREDENTIALS_FILE,
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

    print(f"Создан лист: {report_archive}")

    methods_archive = create_archive_sheet(
        spreadsheet,
        sheet_config["sheets"]["methods"]
    )

    print(f"Создан лист: {methods_archive}")

    print("Готово!")


if __name__ == "__main__":
    main()