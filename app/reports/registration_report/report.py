from app.reports.registration_report.file_detector import get_report_files

from app.reports.registration_report.registration_reader import read_registration_files
from app.reports.registration_report.deposit_reader import read_deposit_files
from app.reports.registration_report.aggregator import aggregate_report_data
from app.reports.registration_report.google_writer import write_report

from app.core.config_loader import load_config
from app.reports.registration_report.agents_google_writer import (
    write_agents_report,
)


def run(folder_path):
    """
    Точка входа для отчета Registration Report.
    """

    registration_files, deposit_files = get_report_files(
        folder_path
    )

    print("\n==============================")
    print("Registration Report")
    print("==============================")


    print(
        f"\nФайлов регистраций: {len(registration_files)}"
    )

    for file in registration_files:
        print(f"  • {file.name}")


    print(
        f"\nФайлов депозитов: {len(deposit_files)}"
    )

    for file in deposit_files:
        print(f"  • {file.name}")


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


    print("\nОбщий отчет:")

    for country, data in report_data.items():
        print(country)
        print(data)


    sheets_config = load_config(
        "configs/sheets.yaml"
    )

    credentials = (
        sheets_config["google_sheets"]
        ["credentials_file"]
    )


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