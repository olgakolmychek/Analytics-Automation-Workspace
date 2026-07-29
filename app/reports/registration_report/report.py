from app.connectors.file_connector import get_files
from app.connectors.excel_connector import detect_excel_type

from app.reports.registration_report.registration_reader import read_registration_files
from app.reports.registration_report.deposit_reader import read_deposit_files
from app.reports.registration_report.aggregator import aggregate_report_data


def get_report_files(folder_path):
    """
    Разделяет входные Excel-файлы на файлы регистраций и депозитов.
    """

    files = get_files(folder_path)

    registration_files = []
    deposit_files = []

    for file in files:

        file_type = detect_excel_type(file)

        if file_type == "registrations":
            registration_files.append(file)

        elif file_type == "deposits":
            deposit_files.append(file)

        else:
            print(f"Не удалось определить тип файла: {file.name}")

    return registration_files, deposit_files


def run(folder_path):
    """
    Точка входа для отчета Registration Report.
    """

    registration_files, deposit_files = get_report_files(folder_path)

    print("\n==============================")
    print("Registration Report")
    print("==============================")

    print(f"\nФайлов регистраций: {len(registration_files)}")

    for file in registration_files:
        print(f"  • {file.name}")

    print(f"\nФайлов депозитов: {len(deposit_files)}")

    for file in deposit_files:
        print(f"  • {file.name}")


    # Читаем регистрации
    registration_data = read_registration_files(
        registration_files
    )


    print("\nСтатистика регистраций:")

    for country, data in registration_data.items():
        print(country)
        print(data)


    # Читаем депозиты
    deposit_data = read_deposit_files(
        deposit_files
    )


    # Объединяем данные регистраций и депозитов
    report_data = aggregate_report_data(
        registration_data,
        deposit_data
    )


    print("\nОбщий отчет:")

    for country, data in report_data.items():
        print(country)
        print(data)