from app.reports.btag_report.report import (
    run as run_btag,
)

from app.reports.registration_report.report import (
    run as run_registration,
)


REPORT = "registration"
# REPORT = "btag"
# REPORT = "all"


if __name__ == "__main__":

    if REPORT == "registration":

        run_registration()

    elif REPORT == "btag":

        run_btag()

    elif REPORT == "all":

        run_registration()

        run_btag()

    else:

        raise ValueError(
            f"Неизвестный отчет: {REPORT}"
        )