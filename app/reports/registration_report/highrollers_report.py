from app.connectors.excel_connector import load_excel


TOP_COUNT = 5


def build_highrollers_report(deposit_files):
    """
    Формирует два Top-5 отчета по каждому GEO:

    1. Top-5 игроков по общей сумме депозитов за неделю.
    2. Top-5 игроков по Average Deposit.

    Average Deposit =
        сумма всех депозитов игрока за неделю
        /
        количество его депозитов за неделю

    Для каждого игрока сохраняется:
    - ID игрока
    - дата первого депозита
    - дата последнего депозита
    - сумма депозитов
    - количество депозитов
    - средний депозит

    Возвращает:

    {
        "period": "...",

        "countries": {

            "Мексика": {
                "by_sum": [...],
                "by_average": [...]
            },

            "Боливия": {
                "by_sum": [...],
                "by_average": [...]
            }

        }
    }
    """

    players = {}

    report_dates = []

    # ========================================================
    # Чтение файлов депозитов
    # ========================================================

    for file in deposit_files:

        print(
            f"Обработка файла для Highrollers: "
            f"{file.name}"
        )

        rows = load_excel(file)

        if not rows:
            continue

        headers = rows[0]

        player_col = headers.index(
            "ID Игрока"
        )

        country_col = headers.index(
            "Страна аккаунта"
        )

        date_col = headers.index(
            "Дата проведения"
        )

        report_sum_col = headers.index(
            "Сумма в валюте отчета"
        )

        # ====================================================
        # Обрабатываем строки
        # ====================================================

        for row in rows[1:]:

            player_id = row[player_col]

            country = row[country_col]

            transaction_date = row[date_col]

            deposit_sum = row[report_sum_col]

            # ------------------------------------------------
            # Проверяем обязательные поля
            # ------------------------------------------------

            if not player_id:
                continue

            if not country:
                continue

            if not transaction_date:
                continue

            if deposit_sum is None:
                continue

            # ------------------------------------------------
            # Период отчета
            # ------------------------------------------------

            report_dates.append(
                transaction_date
            )

            # ------------------------------------------------
            # GEO
            # ------------------------------------------------

            if country not in players:

                players[country] = {}

            # ------------------------------------------------
            # Игрок
            # ------------------------------------------------

            if player_id not in players[country]:

                players[country][player_id] = {

                    "player_id": player_id,

                    "first_deposit": (
                        transaction_date
                    ),

                    "last_deposit": (
                        transaction_date
                    ),

                    "sum": 0,

                    "count": 0,

                }

            player = players[country][player_id]

            # ------------------------------------------------
            # Количество депозитов
            # ------------------------------------------------

            player["count"] += 1

            # ------------------------------------------------
            # Сумма депозитов
            # ------------------------------------------------

            player["sum"] += deposit_sum

            # ------------------------------------------------
            # Первый депозит
            # ------------------------------------------------

            if (
                transaction_date
                < player["first_deposit"]
            ):

                player["first_deposit"] = (
                    transaction_date
                )

            # ------------------------------------------------
            # Последний депозит
            # ------------------------------------------------

            if (
                transaction_date
                > player["last_deposit"]
            ):

                player["last_deposit"] = (
                    transaction_date
                )

    # ========================================================
    # Период отчета
    # ========================================================

    period = None

    if report_dates:

        period = (
            f"{min(report_dates)}"
            f" - "
            f"{max(report_dates)}"
        )

    # ========================================================
    # Подготавливаем Average Deposit
    # ========================================================

    for country_players in players.values():

        for player in country_players.values():

            if player["count"] > 0:

                player["average_deposit"] = (
                    player["sum"]
                    / player["count"]
                )

            else:

                player["average_deposit"] = 0

    # ========================================================
    # Формируем Top-5 по каждому GEO
    # ========================================================

    countries = {}

    for country, country_players in players.items():

        # ----------------------------------------------------
        # Top-5 по общей сумме депозитов
        # ----------------------------------------------------

        by_sum = sorted(
            country_players.values(),
            key=lambda player: (
                player["sum"],
                player["count"],
            ),
            reverse=True,
        )

        # ----------------------------------------------------
        # Top-5 по Average Deposit
        # ----------------------------------------------------

        by_average = sorted(
            country_players.values(),
            key=lambda player: (
                player["average_deposit"],
                player["sum"],
            ),
            reverse=True,
        )

        countries[country] = {

            "by_sum": by_sum[:TOP_COUNT],

            "by_average": by_average[:TOP_COUNT],

        }

    return {

        "period": period,

        "countries": countries,

    }