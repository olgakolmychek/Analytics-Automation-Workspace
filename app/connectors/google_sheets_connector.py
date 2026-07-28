import gspread
from google.oauth2.service_account import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


def connect_google_sheet(credentials_file, spreadsheet_id):

    creds = Credentials.from_service_account_file(
        credentials_file,
        scopes=SCOPES
    )

    client = gspread.authorize(creds)

    return client.open_by_key(spreadsheet_id)



def upload_to_sheet(spreadsheet, sheet_name, data):

    worksheet = spreadsheet.worksheet(sheet_name)

    worksheet.clear()

    worksheet.update(
        values=data,
        range_name="A1"
    )