import gspread
from gspread.utils import rowcol_to_a1

from app.reports.registration_report.geo_mapper import (
    get_sheet_name,
)


TEMPLATE_SHEET = "Шаблон"

TEMPLATE_WIDTH = 5
TEMPLATE_HEIGHT = 14

MAX_WEEKS = 15

METHODS_START_ROW = 15


# ============================================================
# Highrollers
# ============================================================

HIGHROLLERS_SHEET = "Хайроллеры"

HIGHROLLERS_SUM_START_COLUMN = 1
HIGHROLLERS_AVERAGE_START_COLUMN = 9

HIGHROLLERS_TABLE_WIDTH = 6

HIGHROLLERS_HEADERS_SUM = [
    "Неделя",
    "Дата первого пополнения",
    "Дата последнего пополнения",
    "Страна",
    "ID",
    "Сумма, USD",
    "Кол-во депозитов",
]

HIGHROLLERS_HEADERS_AVERAGE = [
    "Неделя",
    "Дата первого пополнения",
    "Дата последнего пополнения",
    "Страна",
    "ID",
    "Средний деп, USD",
]


def write_report(
    report_data,
    sheets_config,
    credentials,
):
    """
    Записывает Registration Report.

    Каждый GEO = отдельный лист.

    В каждый новый недельный блок записываются:
    - дата;
    - регистрации;
    - FTD;
    - депозиты;
    - методы оплаты начиная с 15-й строки.
    """

    client = gspread.service_account(
        filename=credentials
    )

    config = (
        sheets_config["google_sheets"]
        ["projects"]
        ["1xBet"]
        ["reports"]
        ["registration"]
    )

    spreadsheet = client.open_by_key(
        config["id"]
    )

    for country, data in report_data.items():

        sheet_name = get_sheet_name(
            country
        )

        sheet = get_or_create_sheet(
            spreadsheet,
            sheet_name,
        )

        add_week_block(
            spreadsheet,
            sheet,
        )

        write_values(
            sheet,
            data,
        )

        write_methods(
            sheet,
            data,
        )


def write_highrollers_report(
    highrollers_data,
    sheets_config,
    credentials,
):
    """
    Записывает Highrollers Report.

    Левая таблица:
    A:G

    Top-5 по общей сумме депозитов.

    H:
    пустой разделитель.

    Правая таблица:
    I:N

    Top-5 по Average Deposit.

    Каждый новый запуск добавляет строки вниз.
    """

    if not highrollers_data:
        return

    countries = highrollers_data.get(
        "countries",
        {}
    )

    if not countries:
        return

    period = highrollers_data.get(
        "period"
    )

    if not period:
        return

    # ========================================================
    # Подключение к Google Sheets
    # ========================================================

    client = gspread.service_account(
        filename=credentials
    )

    config = (
        sheets_config["google_sheets"]
        ["projects"]
        ["1xBet"]
        ["reports"]
        ["registration"]
    )

    spreadsheet = client.open_by_key(
        config["id"]
    )

    # ========================================================
    # Получаем / создаём лист
    # ========================================================

    sheet = get_or_create_highrollers_sheet(
        spreadsheet
    )

    # ========================================================
    # Формируем две таблицы
    # ========================================================

    sum_rows = []

    average_rows = []

    for country, country_data in countries.items():

        # ====================================================
        # Top-5 по сумме
        # ====================================================

        for player in country_data.get(
            "by_sum",
            []
        ):

            sum_rows.append(
                [
                    period,

                    format_date(
                        player.get(
                            "first_deposit"
                        )
                    ),

                    format_date(
                        player.get(
                            "last_deposit"
                        )
                    ),

                    country,

                    player.get(
                        "player_id",
                        ""
                    ),

                    round(
                        player.get(
                            "sum",
                            0
                        ),
                        2,
                    ),

                    player.get(
                        "count",
                        0
                    ),
                ]
            )

        # ====================================================
        # Top-5 по Average Deposit
        # ====================================================

        for player in country_data.get(
            "by_average",
            []
        ):

            average_rows.append(
                [
                    period,

                    format_date(
                        player.get(
                            "first_deposit"
                        )
                    ),

                    format_date(
                        player.get(
                            "last_deposit"
                        )
                    ),

                    country,

                    player.get(
                        "player_id",
                        ""
                    ),

                    round(
                        player.get(
                            "average_deposit",
                            0
                        ),
                        2,
                    ),
                ]
            )

    if not sum_rows:
        return

    if not average_rows:
        return

    # ========================================================
    # Находим первую свободную строку
    # ========================================================

    start_row = (
        get_highrollers_next_row(
            sheet
        )
    )

    # ========================================================
    # Записываем левую таблицу A:G
    # ========================================================

    sum_end_row = (
        start_row
        + len(sum_rows)
        - 1
    )

    sum_range = (
        f"{rowcol_to_a1(
            start_row,
            HIGHROLLERS_SUM_START_COLUMN
        )}:"
        f"{rowcol_to_a1(
            sum_end_row,
            HIGHROLLERS_SUM_START_COLUMN
            + len(HIGHROLLERS_HEADERS_SUM)
            - 1
        )}"
    )

    sheet.update(
        values=sum_rows,
        range_name=sum_range,
    )

    # ========================================================
    # Записываем правую таблицу I:N
    # ========================================================

    average_end_row = (
        start_row
        + len(average_rows)
        - 1
    )

    average_range = (
        f"{rowcol_to_a1(
            start_row,
            HIGHROLLERS_AVERAGE_START_COLUMN
        )}:"
        f"{rowcol_to_a1(
            average_end_row,
            HIGHROLLERS_AVERAGE_START_COLUMN
            + len(HIGHROLLERS_HEADERS_AVERAGE)
            - 1
        )}"
    )

    sheet.update(
        values=average_rows,
        range_name=average_range,
    )

    # ========================================================
    # Вывод в консоль
    # ========================================================

    print(
        "\nHighrollers Report записан "
        "в Google Sheets:"
    )

    print(
        f"  • Лист: {HIGHROLLERS_SHEET}"
    )

    print(
        f"  • Период: {period}"
    )

    print(
        f"  • Top-5 по сумме: "
        f"{len(sum_rows)} строк"
    )

    print(
        f"  • Top-5 Average Deposit: "
        f"{len(average_rows)} строк"
    )


def get_or_create_highrollers_sheet(
    spreadsheet,
):
    """
    Возвращает лист Хайроллеры.

    Если листа нет — создаёт его
    и добавляет заголовки двух таблиц.
    """

    try:

        sheet = spreadsheet.worksheet(
            HIGHROLLERS_SHEET
        )

        return sheet

    except gspread.exceptions.WorksheetNotFound:

        sheet = spreadsheet.add_worksheet(
            title=HIGHROLLERS_SHEET,
            rows=1000,
            cols=14,
        )

        # ====================================================
        # Заголовок левой таблицы A:G
        # ====================================================

        left_range = (
            f"A1:G1"
        )

        sheet.update(
            values=[
                HIGHROLLERS_HEADERS_SUM
            ],
            range_name=left_range,
        )

        # ====================================================
        # Заголовок правой таблицы I:N
        # ====================================================

        right_range = (
            f"I1:N1"
        )

        sheet.update(
            values=[
                HIGHROLLERS_HEADERS_AVERAGE
            ],
            range_name=right_range,
        )

        return sheet


def get_highrollers_next_row(
    sheet,
):
    """
    Находит первую свободную строку
    для нового недельного блока.

    Используется колонка A как основная.
    """

    values = sheet.col_values(
        1
    )

    if not values:

        return 2

    # Если есть только заголовок

    if len(values) == 1:

        return 2

    # Следующая строка после последней
    # заполненной строки

    return len(values) + 1


def format_date(
    value,
):
    """
    Преобразует дату в:

    DD.MM.YYYY

    Время отбрасывается.
    """

    if not value:
        return ""

    # ========================================================
    # Если это datetime / date
    # ========================================================

    if hasattr(
        value,
        "strftime",
    ):

        return value.strftime(
            "%d.%m.%Y"
        )

    value = str(value)

    # ========================================================
    # Если строка содержит время
    # ========================================================

    if " " in value:

        value = value.split(
            " ",
            1
        )[0]

    # ========================================================
    # ISO дата
    # ========================================================

    try:

        from datetime import datetime

        date_value = datetime.fromisoformat(
            value
        )

        return date_value.strftime(
            "%d.%m.%Y"
        )

    except ValueError:

        return value


def get_or_create_sheet(
    spreadsheet,
    sheet_name,
):
    """
    Возвращает GEO-лист.
    Если листа нет — создаёт.
    """

    try:

        return spreadsheet.worksheet(
            sheet_name
        )

    except gspread.exceptions.WorksheetNotFound:

        return spreadsheet.add_worksheet(
            title=sheet_name,
            rows=100,
            cols=200,
        )


def add_week_block(
    spreadsheet,
    sheet,
):
    """
    Добавляет новый недельный блок.
    """

    weeks = get_weeks_count(
        sheet
    )

    if weeks >= MAX_WEEKS:

        # Сначала добавляем новый блок слева.

        insert_columns_left(
            spreadsheet,
            sheet,
        )

        copy_template(
            spreadsheet,
            sheet,
            1,
        )

        # Затем удаляем самый старый блок справа.

        remove_oldest_week(
            sheet,
        )

    else:

        start_column = (
            weeks
            * TEMPLATE_WIDTH
            + 1
        )

        copy_template(
            spreadsheet,
            sheet,
            start_column,
        )


def copy_template(
    spreadsheet,
    sheet,
    start_column,
):
    """
    Копирует Шаблон A1:E14
    в нужный недельный блок.
    """

    template = spreadsheet.worksheet(
        TEMPLATE_SHEET
    )

    spreadsheet.batch_update(
        {
            "requests": [
                {
                    "copyPaste": {
                        "source": {
                            "sheetId": template.id,
                            "startRowIndex": 0,
                            "endRowIndex": TEMPLATE_HEIGHT,
                            "startColumnIndex": 0,
                            "endColumnIndex": TEMPLATE_WIDTH,
                        },
                        "destination": {
                            "sheetId": sheet.id,
                            "startRowIndex": 0,
                            "endRowIndex": TEMPLATE_HEIGHT,
                            "startColumnIndex": (
                                start_column - 1
                            ),
                            "endColumnIndex": (
                                start_column - 1
                                + TEMPLATE_WIDTH
                            ),
                        },
                        "pasteType": "PASTE_NORMAL",
                    }
                }
            ]
        }
    )


def get_weeks_count(
    sheet,
):
    """
    Считает количество недельных блоков.
    """

    values = sheet.row_values(
        1
    )

    weeks = 0

    for col in range(
        0,
        MAX_WEEKS * TEMPLATE_WIDTH,
        TEMPLATE_WIDTH,
    ):

        block = values[
            col:col + TEMPLATE_WIDTH
        ]

        if not any(block):
            break

        weeks += 1

    return weeks


def remove_oldest_week(
    sheet,
):
    """
    Удаляет крайний правый старый блок.
    """

    weeks = get_weeks_count(
        sheet
    )

    start_column = (
        weeks
        * TEMPLATE_WIDTH
        - TEMPLATE_WIDTH
        + 1
    )

    sheet.delete_columns(
        start_column,
        TEMPLATE_WIDTH,
    )


def insert_columns_left(
    spreadsheet,
    sheet,
):
    """
    Добавляет 5 колонок слева.
    """

    spreadsheet.batch_update(
        {
            "requests": [
                {
                    "insertDimension": {
                        "range": {
                            "sheetId": sheet.id,
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": TEMPLATE_WIDTH,
                        },
                        "inheritFromBefore": False,
                    }
                }
            ]
        }
    )


def write_values(
    sheet,
    data,
):
    """
    Записывает основные значения
    Registration Report.
    """

    weeks = get_weeks_count(
        sheet
    )

    # Колонка значений:
    # B, G, L, Q ...

    value_column = (
        (weeks - 1)
        * TEMPLATE_WIDTH
        + 2
    )

    updates = {

        # Дата
        1: data.get(
            "date",
            ""
        ),

        # Регистрации
        3: data["registrations"]["aff"],
        4: data["registrations"]["org"],

        # FTD
        6: data["ftd"]["aff"],
        7: data["ftd"]["org"],

        # Депозиты
        11: data["deposits"]["sum"],
        12: data["deposits"]["count"],
    }

    for row, value in updates.items():

        sheet.update(
            values=[
                [value]
            ],
            range_name=rowcol_to_a1(
                row,
                value_column,
            ),
        )


def write_methods(
    sheet,
    data,
):
    """
    Записывает методы оплаты начиная с 15-й строки.

    Структура:

    Агент / Группа | Доля | Кол-во депозитов | Конверсии

    Все строки записываются обычным шрифтом.

    Доля и конверсия записываются
    сразу с символом %.

    unresolved_message пока не записывается.
    """

    methods_data = data.get(
        "methods"
    )

    if not methods_data:
        return

    weeks = get_weeks_count(
        sheet
    )

    # Первый столбец текущего недельного блока.

    start_column = (
        (weeks - 1)
        * TEMPLATE_WIDTH
        + 1
    )

    rows = []

    for group in methods_data.get(
        "rows",
        []
    ):

        share = group.get(
            "share"
        )

        conversion = group.get(
            "conversion"
        )

        rows.append(
            [
                group.get(
                    "name",
                    ""
                ),
                (
                    f"{share:.1f}%"
                    if share is not None
                    else ""
                ),
                group.get(
                    "deposits",
                    ""
                ),
                (
                    f"{conversion:.1f}%"
                    if conversion is not None
                    else ""
                ),
            ]
        )

        for detail in group.get(
            "detail",
            []
        ):

            detail_share = detail.get(
                "share"
            )

            detail_conversion = detail.get(
                "conversion"
            )

            rows.append(
                [
                    detail.get(
                        "name",
                        ""
                    ),
                    (
                        f"{detail_share:.1f}%"
                        if detail_share is not None
                        else ""
                    ),
                    detail.get(
                        "deposits",
                        ""
                    ),
                    (
                        f"{detail_conversion:.1f}%"
                        if detail_conversion is not None
                        else ""
                    ),
                ]
            )

    if not rows:
        return

    # ========================================================
    # Записываем всю таблицу одним update
    # ========================================================

    end_row = (
        METHODS_START_ROW
        + len(rows)
        - 1
    )

    end_column = (
        start_column + 3
    )

    range_name = (
        f"{rowcol_to_a1(
            METHODS_START_ROW,
            start_column
        )}:"
        f"{rowcol_to_a1(
            end_row,
            end_column
        )}"
    )

    sheet.update(
        values=rows,
        range_name=range_name,
    )