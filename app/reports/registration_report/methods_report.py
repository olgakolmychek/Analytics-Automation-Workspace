from collections import defaultdict

import gspread

from app.connectors.excel_connector import load_excel


# ============================================================
# НАСТРОЙКИ
# ============================================================

MIN_SHARE = 0.5

DETAIL_GROUPS = {
    "Боливия": {
        "QR code payment",
        "Pago Facil",
        "QR Rapido",
    },
    "Мексика": {
        "Spei",
    },
}


# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def normalize(value):
    """
    Нормализует значение для сравнений.
    """

    if value is None:
        return ""

    return str(value).strip().lower()


def to_number(value):
    """
    Безопасно приводит значение к float.
    """

    if value is None or value == "":
        return 0.0

    if isinstance(value, (int, float)):
        return float(value)

    value = str(value).strip()

    # Убираем пробелы-разделители тысяч
    value = value.replace(" ", "")
    value = value.replace("\u00a0", "")

    # Если число записано как 1,234.56
    if "," in value and "." in value:

        if value.rfind(",") < value.rfind("."):
            value = value.replace(",", "")
        else:
            value = value.replace(".", "")
            value = value.replace(",", ".")

    elif "," in value:
        value = value.replace(",", ".")

    try:
        return float(value)

    except (ValueError, TypeError):
        return 0.0


def round_one(value):
    """
    Округление до одного знака.
    """

    return round(float(value), 1)


def format_percent(value):
    """
    Форматирует процент для Google Sheets/отчета.
    """

    if value is None:
        return "N/A"

    return f"{round_one(value):.1f}%"


def clean_number(value):
    """
    Убирает ненужные десятичные знаки.

    1234.0 -> 1234
    1234.5 -> 1234.5
    """

    value = round_one(value)

    if value.is_integer():
        return int(value)

    return value


# ============================================================
# ЧТЕНИЕ CONVERTION REPORT
# ============================================================

def read_conversion_file(file_path):
    """
    Читает ConvertionReport.xlsx.

    Возвращает список словарей.
    """

    rows = load_excel(file_path)

    if not rows:
        return []

    headers = list(rows[0])

    required_headers = [
        "Агент",
        "Агент (ID)",
        "Субагент",
        "Субагент (ID)",
        "Страна",
        "Количество 'OK'",
        "Доля 'OK', %",
        "Общее количество заявок",
    ]

    missing = [
        header
        for header in required_headers
        if header not in headers
    ]

    if missing:
        raise ValueError(
            "В ConvertionReport.xlsx отсутствуют колонки: "
            + ", ".join(missing)
        )

    index = {
        header: headers.index(header)
        for header in required_headers
    }

    result = []

    for row in rows[1:]:

        country = row[index["Страна"]]

        if not country:
            continue

        item = {
            "agent": row[index["Агент"]],
            "agent_id": row[index["Агент (ID)"]],
            "subagent": row[index["Субагент"]],
            "subagent_id": row[index["Субагент (ID)"]],
            "country": str(country).strip(),

            "ok": to_number(
                row[index["Количество 'OK'"]]
            ),

            "conversion": to_number(
                row[index["Доля 'OK', %"]]
            ),

            "total_requests": to_number(
                row[index["Общее количество заявок"]]
            ),
        }

        result.append(item)

    return result


# ============================================================
# MAPPING GOOGLE SHEETS
# ============================================================

def read_mapping(
    credentials_file,
    spreadsheet_id,
    worksheet_name,
):
    """
    Читает Mapping напрямую из Google Sheets.

    Ожидаемые колонки:

    Subagent ID
    Субагент
    Строка в отчете

    Допускаются также русские варианты:

    Субагент (ID)
    Название
    """

    client = gspread.service_account(
        filename=credentials_file
    )

    spreadsheet = client.open_by_key(
        spreadsheet_id
    )

    worksheet = spreadsheet.worksheet(
        worksheet_name
    )

    values = worksheet.get_all_values()

    if not values:
        return {
            "by_id": {},
            "by_name": {},
        }

    headers = [
        str(value).strip()
        for value in values[0]
    ]

    def find_column(*names):

        normalized_headers = {
            normalize(header): index
            for index, header in enumerate(headers)
        }

        for name in names:

            index = normalized_headers.get(
                normalize(name)
            )

            if index is not None:
                return index

        return None

    id_col = find_column(
        "Subagent ID",
        "Субагент ID",
        "Субагент (ID)",
        "ID",
    )

    name_col = find_column(
        "Субагент",
        "Название",
        "Subagent",
    )

    group_col = find_column(
        "Строка в отчете",
        "Строка в отчёте",
        "Группа",
        "Group",
    )

    if group_col is None:
        raise ValueError(
            "В Mapping не найдена колонка "
            "'Строка в отчете'."
        )

    by_id = {}
    by_name = {}

    for row in values[1:]:

        if len(row) <= group_col:
            continue

        group = str(
            row[group_col]
        ).strip()

        if not group:
            continue

        # --------------------------------------------------------
        # Mapping по ID
        # --------------------------------------------------------

        if id_col is not None and len(row) > id_col:

            subagent_id = str(
                row[id_col]
            ).strip()

            if subagent_id:
                by_id[subagent_id] = group

        # --------------------------------------------------------
        # Mapping по названию
        # --------------------------------------------------------

        if name_col is not None and len(row) > name_col:

            name = str(
                row[name_col]
            ).strip()

            if name:
                by_name[
                    normalize(name)
                ] = group

    return {
        "by_id": by_id,
        "by_name": by_name,
    }


# ============================================================
# FALLBACK-КЛАССИФИКАЦИЯ
# ============================================================

def classify_by_rules(item):
    """
    Fallback-классификация новых субагентов,
    которых нет в Google Sheets Mapping.

    Возвращает название группы или None.
    """

    agent_id = normalize(
        item.get("agent_id")
    )

    subagent = normalize(
        item.get("subagent")
    )

    country = normalize(
        item.get("country")
    )

    # ========================================================
    # BT (ручные)
    # ========================================================

    if agent_id == "279":
        return "BT (ручные)"

    # ========================================================
    # CRYPTO
    # ========================================================

    crypto_words = [
        "crypto",
        "binance",
        "binancepay",
        "bitcoin",
        "btc",
        "ethereum",
        "eth",
        "usdt",
        "usdc",
        "tron",
        "trc20",
        "erc20",
        "tether",
        "shib",
        "kshib",
        "polygon",
        "pol",
    ]

    if any(
        word in subagent
        for word in crypto_words
    ):
        return "Crypto"

    # ========================================================
    # AIRTM
    # ========================================================

    if "airtm" in subagent:
        return "Airtm"

    # ========================================================
    # SKRILL
    # ========================================================

    if "skrill" in subagent:
        return "Skrill"

    # ========================================================
    # NETELLER
    # ========================================================

    if "neteller" in subagent:
        return "Neteller"

    # ========================================================
    # CARDS
    # ========================================================

    card_words = [
        "card",
        "cards",
        "visa",
        "mastercard",
        "master card",
    ]

    if any(
        word in subagent
        for word in card_words
    ):
        return "Карты"

    # ========================================================
    # BOLIVIA
    # ========================================================

    if country == "боливия":

        # Сначала проверяем QR Rapido,
        # потому что в названии тоже есть QR.
        if "qr rapido" in subagent:
            return "QR Rapido"

        # Pago Facil
        if "pago facil" in subagent:
            return "Pago Facil"

        if "pago fácil" in subagent:
            return "Pago Facil"

        # Любой другой QR
        if "qr" in subagent:
            return "QR code payment"

    # ========================================================
    # MEXICO
    # ========================================================

    if country == "мексика":

        mexico_methods = {
            "bbva": "BBVA",
            "mercadopago": "MercadoPago",
            "mercado pago": "MercadoPago",
            "oxxopay": "Oxxopay",
            "oxxo pay": "Oxxopay",
            "codi": "CoDi",
            "banorte": "Banorte",
            "banamex": "Banamex",
            "spei": "Spei",
        }

        for keyword, group in mexico_methods.items():

            if keyword in subagent:
                return group

    # ========================================================
    # BT — ОСТАЛЬНЫЕ БАНКОВСКИЕ
    # ========================================================

    bank_words = [
        "bank",
        "banco",
        "banking",
        "transfer",
        "transferencia",
    ]

    if any(
        word in subagent
        for word in bank_words
    ):
        return "BT – остальные банковские"

    # ========================================================
    # НЕ УДАЛОСЬ ОПРЕДЕЛИТЬ
    # ========================================================

    return None


# ============================================================
# ОПРЕДЕЛЕНИЕ ГРУППЫ
# ============================================================

def classify_item(
    item,
    mapping,
):
    """
    Каскадное определение группы.

    Приоритет:

    1. Mapping по ID
    2. Mapping по названию
    3. Fallback-правила
    4. Остальные методы
    """

    subagent_id = str(
        item.get("subagent_id", "")
    ).strip()

    subagent_name = normalize(
        item.get("subagent")
    )

    by_id = mapping.get(
        "by_id",
        {}
    )

    by_name = mapping.get(
        "by_name",
        {}
    )

    # ========================================================
    # 1. MAPPING ПО ID
    # ========================================================

    if subagent_id:

        group = by_id.get(
            subagent_id
        )

        if group:
            return group, False

    # ========================================================
    # 2. MAPPING ПО НАЗВАНИЮ
    # ========================================================

    if subagent_name:

        group = by_name.get(
            subagent_name
        )

        if group:
            return group, False

    # ========================================================
    # 3. FALLBACK
    # ========================================================

    group = classify_by_rules(
        item
    )

    if group:
        return group, True

    # ========================================================
    # 4. ОСТАЛЬНЫЕ
    # ========================================================

    return "Остальные методы", True


# ============================================================
# РАСЧЕТ КОНВЕРСИИ
# ============================================================

def calculate_conversion(items):
    """
    Считает конверсию группы.

    Если есть total_requests:

        SUM(OK) / SUM(requests) * 100

    Иначе:

        средняя готовая конверсия,
        взвешенная по количеству OK.
    """

    if not items:
        return None

    total_ok = sum(
        item["ok"]
        for item in items
    )

    total_requests = sum(
        item["total_requests"]
        for item in items
    )

    # --------------------------------------------------------
    # Основной расчет
    # --------------------------------------------------------

    if total_requests > 0:

        return (
            total_ok
            / total_requests
            * 100
        )

    # --------------------------------------------------------
    # Fallback расчет
    # --------------------------------------------------------

    weighted_sum = sum(
        item["conversion"] * item["ok"]
        for item in items
        if item["ok"] > 0
    )

    weight = sum(
        item["ok"]
        for item in items
        if item["ok"] > 0
    )

    if weight > 0:

        return (
            weighted_sum
            / weight
        )

    return None


# ============================================================
# СОРТИРОВКА
# ============================================================

def sort_rows(rows):
    """
    Сортировка:

    1. По убыванию доли
    2. При равенстве — по убыванию количества
    """

    return sorted(
        rows,
        key=lambda row: (
            row["share"],
            row["deposits"],
        ),
        reverse=True,
    )


# ============================================================
# ФОРМИРОВАНИЕ ОТЧЕТА ПО GEO
# ============================================================

def build_country_report(
    country,
    items,
    mapping,
):
    """
    Формирует отчет одного GEO.

    Для детализированных групп:

    Bolivia:
        QR code payment
        Pago Facil
        QR Rapido

    Mexico:
        Spei
    """

    total_deposits = sum(
        item["ok"]
        for item in items
    )

    groups = defaultdict(list)

    unresolved = []

    # ========================================================
    # КЛАССИФИКАЦИЯ ВСЕХ СУБАГЕНТОВ
    # ========================================================

    for item in items:

        group, used_fallback = classify_item(
            item,
            mapping,
        )

        groups[group].append(
            item
        )

        if used_fallback:

            unresolved.append(
                {
                    "id": item["subagent_id"],
                    "name": item["subagent"],
                    "group": group,
                }
            )

    rows = []

    # ========================================================
    # ФОРМИРОВАНИЕ ГРУПП
    # ========================================================

    for group_name, group_items in groups.items():

        deposits = sum(
            item["ok"]
            for item in group_items
        )

        share = (
            deposits
            / total_deposits
            * 100
            if total_deposits
            else 0
        )

        conversion = calculate_conversion(
            group_items
        )

        is_detail_group = (
            country in DETAIL_GROUPS
            and group_name in DETAIL_GROUPS[country]
        )

        group_row = {
            "name": group_name,
            "share": round_one(share),
            "deposits": clean_number(deposits),
            "conversion": (
                round_one(conversion)
                if conversion is not None
                else None
            ),
            "bold": True,
            "detail": [],
        }

        # ====================================================
        # ДЕТАЛИЗАЦИЯ
        # ====================================================

        if is_detail_group:

            detail_rows = []

            for item in group_items:

                item_deposits = item["ok"]

                item_share = (
                    item_deposits
                    / total_deposits
                    * 100
                    if total_deposits
                    else 0
                )

                item_conversion = item["conversion"]

                subagent_name = str(
                    item["subagent"] or ""
                ).strip()

                # ------------------------------------------------
                # Определяем префикс
                # ------------------------------------------------

                if (
                    country == "Мексика"
                    and group_name == "Spei"
                ):

                    prefix = "Spei"

                elif (
                    country == "Боливия"
                    and group_name == "Pago Facil"
                ):

                    prefix = "Pago Facil"

                elif (
                    country == "Боливия"
                    and group_name == "QR code payment"
                ):

                    prefix = ""

                elif (
                    country == "Боливия"
                    and group_name == "QR Rapido"
                ):

                    prefix = "QR Rapido"

                else:

                    prefix = ""

                # ------------------------------------------------
                # Формируем название
                # ------------------------------------------------

                if prefix:

                    detail_name = (
                        f"{prefix} {subagent_name}"
                    )

                else:

                    detail_name = subagent_name

                detail_rows.append(
                    {
                        "name": detail_name,
                        "share": round_one(
                            item_share
                        ),
                        "deposits": clean_number(
                            item_deposits
                        ),
                        "conversion": (
                            round_one(
                                item_conversion
                            )
                            if item_conversion is not None
                            else None
                        ),
                        "bold": False,
                    }
                )

            group_row["detail"] = sort_rows(
                detail_rows
            )

        rows.append(
            group_row
        )

    # ========================================================
    # ПОРОГ 0.5%
    # ========================================================

    visible_rows = []

    other_items = []

    for row in rows:

        if row["share"] >= MIN_SHARE:

            visible_rows.append(
                row
            )

        else:

            other_items.append(
                row
            )

    # ========================================================
    # ОБЪЕДИНЯЕМ МАЛЕНЬКИЕ ГРУППЫ
    # ========================================================

    if other_items:

        small_items = []

        for row in other_items:

            for item in groups[row["name"]]:

                small_items.append(
                    item
                )

        other_deposits = sum(
            item["ok"]
            for item in small_items
        )

        other_share = (
            other_deposits
            / total_deposits
            * 100
            if total_deposits
            else 0
        )

        other_conversion = calculate_conversion(
            small_items
        )

        visible_rows.append(
            {
                "name": "Остальные методы",
                "share": round_one(
                    other_share
                ),
                "deposits": clean_number(
                    other_deposits
                ),
                "conversion": (
                    round_one(
                        other_conversion
                    )
                    if other_conversion is not None
                    else None
                ),
                "bold": True,
                "detail": [],
            }
        )

    # ========================================================
    # ФИНАЛЬНАЯ СОРТИРОВКА
    # ========================================================

    visible_rows = sort_rows(
        visible_rows
    )

    # ========================================================
    # СООБЩЕНИЕ О НОВЫХ СУБАГЕНТАХ
    # ========================================================

    if unresolved:

        unresolved_unique = []

        seen = set()

        for item in unresolved:

            key = (
                str(item["id"]),
                str(item["name"]),
                str(item["group"]),
            )

            if key in seen:
                continue

            seen.add(key)

            unresolved_unique.append(
                item
            )

        unresolved_message = (
            "Новые/неопределённые субагенты: "
            + "; ".join(
                f"{item['id']} ({item['name']}) "
                f"→ отнесён в {item['group']}"
                for item in unresolved_unique
            )
        )

    else:

        unresolved_message = (
            "Все субагенты распределены "
            "по логическим группам в соответствии "
            "с порогом 0.5% и правилами маппинга"
        )

    # ========================================================
    # РЕЗУЛЬТАТ
    # ========================================================

    return {
        "country": country,
        "total_deposits": clean_number(
            total_deposits
        ),
        "rows": visible_rows,
        "unresolved_message": unresolved_message,
    }


# ============================================================
# ФОРМИРОВАНИЕ ОТЧЕТА ПО GEO
# ============================================================

def build_methods_report(
    conversion_file,
    credentials_file,
    mapping_spreadsheet_id,
    mapping_worksheet,
):
    """
    Главная функция построения отчета по методам.

    Возвращает:

    {
        "Боливия": {...},
        "Мексика": {...},
        ...
    }
    """

    items = read_conversion_file(
        conversion_file
    )

    mapping = read_mapping(
        credentials_file=credentials_file,
        spreadsheet_id=mapping_spreadsheet_id,
        worksheet_name=mapping_worksheet,
    )

    countries = defaultdict(list)

    for item in items:

        countries[
            item["country"]
        ].append(item)

    result = {}

    for country, country_items in countries.items():

        result[country] = build_country_report(
            country=country,
            items=country_items,
            mapping=mapping,
        )

    return result