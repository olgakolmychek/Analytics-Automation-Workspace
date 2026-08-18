from app.reports.registration_report.file_detector import (
    get_report_files,
)

from app.reports.registration_report.highrollers_report import (
    build_highrollers_report,
)

from app.reports.registration_report.google_writer import (
    write_highrollers_report,
)

from app.core.config_loader import load_config


def run_highrollers_test():
    """
    Тестовый запуск только Highrollers Report.

    НЕ выполняет:
    - Registration Report
    - Methods Report
    - Agents Report

    Выполняет только:
    - чтение файлов депозитов;
    - Top-5 по сумме депозитов;
    - Top-5 по Average Deposit;
    - запись на лист "Хайроллеры".
    """

    print("\n")
    print("=" * 60)
    print("TEST: TOP 5 HIGHROLLERS")
    print("=" * 60)

    # ========================================================
    # Settings
    # ========================================================

    settings = load_config(
        "configs/settings.yaml"
    )

    folder_path = (
        settings["paths"]
        ["incoming_registration"]
    )

    # ========================================================
    # Ищем файлы
    # ========================================================

    (
        registration_files,
        deposit_files,
        conversion_files,
    ) = get_report_files(
        folder_path
    )

    print(
        f"\nНайдено файлов депозитов: "
        f"{len(deposit_files)}"
    )

    for file in deposit_files:

        print(
            f"  • {file.name}"
        )

    if not deposit_files:

        print(
            "\nФайлы депозитов не найдены."
        )

        return

    # ========================================================
    # Только Highrollers
    # ========================================================

    highrollers_data = (
        build_highrollers_report(
            deposit_files
        )
    )

    # ========================================================
    # Выводим результат в консоль
    # ========================================================

    print("\n")
    print("=" * 60)
    print("TOP 5 ПО СУММЕ")
    print("=" * 60)

    print(
        f"\nПериод: "
        f"{highrollers_data.get('period')}"
    )

    for country, country_data in (
        highrollers_data
        .get("countries", {})
        .items()
    ):

        print(f"\n{country}")

        for index, player in enumerate(
            country_data.get(
                "by_sum",
                []
            ),
            start=1,
        ):

            print(
                f"{index}. "
                f"ID: {player['player_id']} | "
                f"Сумма: "
                f"{player['sum']:.2f} | "
                f"Депозитов: "
                f"{player['count']} | "
                f"Средний: "
                f"{player['average_deposit']:.2f} | "
                f"Первый: "
                f"{player['first_deposit']} | "
                f"Последний: "
                f"{player['last_deposit']}"
            )

    print("\n")
    print("=" * 60)
    print("TOP 5 ПО AVERAGE DEPOSIT")
    print("=" * 60)

    for country, country_data in (
        highrollers_data
        .get("countries", {})
        .items()
    ):

        print(f"\n{country}")

        for index, player in enumerate(
            country_data.get(
                "by_average",
                []
            ),
            start=1,
        ):

            print(
                f"{index}. "
                f"ID: {player['player_id']} | "
                f"Средний деп: "
                f"{player['average_deposit']:.2f} | "
                f"Сумма: "
                f"{player['sum']:.2f} | "
                f"Депозитов: "
                f"{player['count']} | "
                f"Первый: "
                f"{player['first_deposit']} | "
                f"Последний: "
                f"{player['last_deposit']}"
            )

    # ========================================================
    # Google Sheets
    # ========================================================

    sheets_config = load_config(
        "configs/sheets.yaml"
    )

    credentials = (
        sheets_config["google_sheets"]
        ["credentials_file"]
    )

    print("\n")
    print("=" * 60)
    print("ЗАПИСЬ В GOOGLE SHEETS")
    print("=" * 60)

    write_highrollers_report(
        highrollers_data,
        sheets_config,
        credentials,
    )

    print("\n")
    print("=" * 60)
    print("HIGHROLLERS TEST FINISHED")
    print("=" * 60)


if __name__ == "__main__":

    run_highrollers_test()