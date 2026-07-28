from openpyxl import load_workbook
from pathlib import Path


def load_excel(file_path):
    """
    Загружает Excel-файл и возвращает данные.
    """

    workbook = load_workbook(file_path)

    sheet = workbook.active

    rows = list(sheet.iter_rows(values_only=True))

    return rows


def find_country(rows):
    """
    Ищет колонку Страна/Country и берет значение из второй строки.
    """

    headers = rows[0]

    country_column = None

    for index, header in enumerate(headers):
        if header in ["Страна", "Country"]:
            country_column = index
            break

    if country_column is None:
        raise Exception("Не найдена колонка Страна/Country")

    country = rows[1][country_column]

    return country