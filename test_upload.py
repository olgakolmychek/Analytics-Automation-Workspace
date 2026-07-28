from app.core.config_loader import load_config, get_btag_sheet_config
from app.connectors.google_sheets_connector import connect_google_sheet, upload_to_sheet
from app.connectors.excel_connector import load_excel


# настройки Google
sheets_config = load_config("configs/sheets.yaml")

geo = "Bolivia"

sheet_config = get_btag_sheet_config(
    sheets_config,
    geo
)


# подключение к таблице
spreadsheet = connect_google_sheet(
    "credentials/focal-pager-503718-p2-82fd68b1b8f7.json",
    sheet_config["id"]
)


# читаем Excel
data = load_excel(
    "data/incoming/btag/report_by_params_btag (5).xlsx"
)


# загружаем в Sheet1
upload_to_sheet(
    spreadsheet,
    sheet_config["sheets"]["input"],
    data
)


print("Данные загружены")