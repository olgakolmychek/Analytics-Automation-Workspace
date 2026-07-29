from app.reports.btag_report.processor import process_files

from app.core.config_loader import load_config


def run():

    settings = load_config(
        "configs/settings.yaml"
    )

    sheets_config = load_config(
        "configs/sheets.yaml"
    )

    incoming_folder = settings["paths"]["incoming_btag"]

    process_files(
        incoming_folder,
        sheets_config
    )