import yaml
from pathlib import Path


def load_config(file_path):
    """
    Загружает YAML конфигурацию.
    """

    path = Path(file_path)

    with open(path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    return config

def get_btag_sheet_config(config, geo):
    return (
        config["google_sheets"]
        ["projects"]
        ["1xBet"]
        ["reports"]
        ["btag"]
        [geo]
    )