from app.connectors.file_connector import get_files
from app.connectors.excel_connector import load_excel, find_country
from app.connectors.google_sheets_connector import (
    connect_google_sheet,
    upload_to_sheet,
)

from app.core.config_loader import get_btag_sheet_config
from app.services.geo_detector import detect_geo
from app.services.google_sheet_archive import (
    create_archive_sheet,
    cleanup_old_archives,
)

import time


def process_file(file_path, sheets_config):

    print(
        f"\nОбработка файла: {file_path}"
    )

    rows = load_excel(file_path)

    country = find_country(rows)

    print(
        f"Страна из файла: {country}"
    )

    geo = detect_geo(country)

    print(
        f"Определенный GEO: {geo}"
    )

    if not geo:
        print(
            "GEO не определен"
        )
        return


    sheet_config = get_btag_sheet_config(
        sheets_config,
        geo
    )


    credentials = sheets_config["google_sheets"]["credentials_file"]


    spreadsheet = connect_google_sheet(
        credentials,
        sheet_config["id"]
    )


    upload_to_sheet(
        spreadsheet,
        sheet_config["sheets"]["input"],
        rows
    )


    print(
        "Sheet1 обновлен"
    )


    print(
        "Ожидание пересчета формул..."
    )

    time.sleep(10)


    report_archive = create_archive_sheet(
        spreadsheet,
        sheet_config["sheets"]["report"]
    )


    methods_archive = create_archive_sheet(
        spreadsheet,
        sheet_config["sheets"]["methods"]
    )


    print(
        f"Создан архив: {report_archive}"
    )

    print(
        f"Создан архив: {methods_archive}"
    )

    cleanup_old_archives(
        spreadsheet,
        keep_last=30
    )



def process_files(folder, sheets_config):

    files = get_files(folder)


    print(
        f"Найдено файлов: {len(files)}"
    )


    for file in files:

        process_file(
            file,
            sheets_config
        )