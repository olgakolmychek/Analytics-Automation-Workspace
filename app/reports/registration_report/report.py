from app.reports.registration_report.file_detector import (
    get_report_files,
)

from app.reports.registration_report.registration_reader import (
    read_registration_files,
)

from app.reports.registration_report.deposit_reader import (
    read_deposit_files,
)

from app.reports.registration_report.aggregator import (
    aggregate_report_data,
)

from app.reports.registration_report.google_writer import (
    write_report,
)

from app.reports.registration_report.agents_google_writer import (
    write_agents_report,
)

from app.reports.registration_report.methods_report import (
    build_methods_report,
)

from app.core.config_loader import load_config


def run():
    """
    Точка входа для Registration Report.
    """

    settings = load_config(
        "configs/settings.yaml"
    )

    folder_path = (
        settings["paths"]
        ["incoming_registration"]
    )

    (
        registration_files,
        deposit_files,
        conversion_files,
    ) = get_report_files(
        folder_path
    )

    print("\n==============================")
    print("Registration Report")
    print("==============================")

    print(
        f"\nФайлов регистраций: "
        f"{len(registration_files)}"
    )

    for file in registration_files:
        print(f"  • {file.name}")

    print(
        f"\nФайлов депозитов: "
        f"{len(deposit_files)}"
    )

    for file in deposit_files:
        print(f"  • {file.name}")

    print(
        f"\nФайлов конверсий: "
        f"{len(conversion_files)}"
    )

    for file in conversion_files:
        print(f"  • {file.name}")

    # ========================================================
    # Старый Registration Report
    # ========================================================

    registration_data = read_registration_files(
        registration_files
    )

    deposit_data = read_deposit_files(
        deposit_files
    )

    report_data = aggregate_report_data(
        registration_data,
        deposit_data
    )

    # ========================================================
    # Google Sheets config
    # ========================================================

    sheets_config = load_config(
        "configs/sheets.yaml"
    )

    credentials = (
        sheets_config["google_sheets"]
        ["credentials_file"]
    )

    # ========================================================
    # Новый отчет по методам
    # ========================================================

    methods_data = {}

    if conversion_files:

        if len(conversion_files) > 1:

            raise ValueError(
                "Найдено несколько файлов "
                "ConvertionReport. "
                "Ожидается только один."
            )

        conversion_file = (
            conversion_files[0]
        )

        mapping_config = (
            sheets_config["google_sheets"]
            ["projects"]
            ["1xBet"]
            ["reports"]
            ["registration"]
            ["mapping"]
        )

        methods_data = build_methods_report(
            conversion_file=conversion_file,
            credentials_file=credentials,
            mapping_spreadsheet_id=(
                mapping_config["id"]
            ),
            mapping_worksheet=(
                mapping_config["sheet"]
            ),
        )

    # ========================================================
    # Добавляем методы к report_data
    # ========================================================

    for country, methods in methods_data.items():

        if country not in report_data:

            report_data[country] = {
                "date": "",
                "registrations": {
                    "aff": 0,
                    "org": 0,
                },
                "ftd": {
                    "aff": 0,
                    "org": 0,
                },
                "deposits": {
                    "count": 0,
                    "sum": 0,
                },
                "agents": {},
            }

        report_data[country][
            "methods"
        ] = methods

    # ========================================================
    # Вывод в консоль
    # ========================================================

    print("\nОбщий отчет:")

    for country, data in report_data.items():

        print(
            f"\n{country}"
        )

        print(data)

    # ========================================================
    # Google Sheets
    # ========================================================

    write_report(
        report_data,
        sheets_config,
        credentials,
    )

    write_agents_report(
        report_data,
        sheets_config,
        credentials,
    )