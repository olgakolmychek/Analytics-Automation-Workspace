from app.connectors.file_connector import get_files
from app.connectors.excel_connector import detect_excel_type


def get_report_files(folder_path):
    """
    Разделяет входные Excel-файлы
    на файлы регистраций и депозитов.
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
            print(
                f"Не удалось определить тип файла: {file.name}"
            )

    return registration_files, deposit_files