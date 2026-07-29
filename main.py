from app.core.config_loader import load_config
from app.reports.registration_report.report import run as run_registration_report


def main():

    settings = load_config("configs/settings.yaml")

    incoming_folder = settings["paths"]["incoming_registration"]

    run_registration_report(incoming_folder)


if __name__ == "__main__":
    main()