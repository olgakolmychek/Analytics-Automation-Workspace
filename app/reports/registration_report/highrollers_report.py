from app.connectors.excel_connector import load_excel


TOP_COUNT = 5


def build_highrollers_report(deposit_files):
    """
    Формирует Top-5 хайроллеров по каждому GEO.

    Для каждого игрока считаем:
    - дату первого депозита
    - дату последнего депозита
    - общую сумму депозитов в валюте отчета
    - количество депозитов

    Возвращает:
    {
        "period": "...",
        "countries": {
            "Bolivia": [
                {
                    "player_id": ...,
                    "first_deposit": ...,
                    "last_deposit": ...,
                    "sum": ...,
                    "count": ...
                }
            ]
        }
    }
    """

    players = {}
    report_dates = []

    for file in deposit_files:

        print(
            f"Обработка файла для Highrollers: {file.name}"
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

        for row in rows[1:]:

            player_id = row[player_col]
            country = row[country_col]
            transaction_date = row[date_col]
            deposit_sum = row[report_sum_col]

            # ------------------------------------------------
            # Проверяем обязательные данные
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
            # Создаем структуру GEO
            # ------------------------------------------------

            if country not in players:

                players[country] = {}

            # ------------------------------------------------
            # Создаем игрока
            # ------------------------------------------------

            if player_id not in players[country]:

                players[country][player_id] = {

                    "player_id": player_id,

                    "first_deposit": transaction_date,

                    "last_deposit": transaction_date,

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

            if transaction_date < player["first_deposit"]:

                player["first_deposit"] = (
                    transaction_date
                )

            # ------------------------------------------------
            # Последний депозит
            # ------------------------------------------------

            if transaction_date > player["last_deposit"]:

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
    # Top-5 по каждому GEO
    # ========================================================

    top_players = {}

    for country, country_players in players.items():

        sorted_players = sorted(
            country_players.values(),
            key=lambda player: player["sum"],
            reverse=True,
        )

        top_players[country] = (
            sorted_players[:TOP_COUNT]
        )

    return {

        "period": period,

        "countries": top_players,

    }