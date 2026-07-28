from app.connectors.google_sheets_connector import connect_google_sheet
from app.services.google_sheet_archive import create_archive_sheet


spreadsheet = connect_google_sheet(
    "credentials/focal-pager-503718-p2-82fd68b1b8f7.json",
    "1QB8FSxf9cKxetu1nfLaGBIMCeWiLE8qXbCWtrG2SHhA"
)


name = create_archive_sheet(
    spreadsheet,
    "Отчет"
)


print(name)