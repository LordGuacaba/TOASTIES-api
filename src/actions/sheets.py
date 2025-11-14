import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]

def get_creds():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def create_spreadsheet(title: str):
  """
  Creates a google sheet with the given title
  """
  creds = get_creds()
  try:
    service = build("sheets", "v4", credentials=creds)
    spreadsheet = {"sheets": [], "properties": {"title": title}}
    newsheet = (
        service.spreadsheets()
        .create(body=spreadsheet, fields="spreadsheetId")
        .execute()
    )
    return newsheet.get("spreadsheetId")


  except HttpError as error:
    print(f"An error occurred: {error}")
    return error
  
def get_sheet_names(id: str) -> list[str]:
    """
    Gets the name of each sheet in the spreadsheet with the given id. Deletes a sheet named "Sheet 1" if it exists
    """
    sheet_names = []
    creds = get_creds()
    service = build("sheets", "v4", credentials=creds)
    spreadsheet = service.spreadsheets().get(spreadsheetId=id).execute()
    sheets = spreadsheet.get("sheets")
    for sheet in sheets:
        if sheet['properties']['title'] == "Sheet1":
            if len(sheets) == 1:
                return []
            spreadsheet_batch_update(id, [{"deleteSheet": {"sheetId": sheet['properties']['sheetId']}}])
            continue
        sheet_names.append(sheet['properties']['title'])
    return sheet_names

def batch_get_values(id: str, ranges: list):
    """
    Retrieves and returns a list of value sets for each of the given ranges.
    """
    major_dimension = "ROWS"
    creds = get_creds()
    service = build("sheets", "v4", credentials=creds)
    get_object = service.spreadsheets().values().batchGet(spreadsheetId=id, ranges=ranges, majorDimension=major_dimension).execute()
    value_sets = [value_range["values"] for value_range in get_object["valueRanges"]]
    return value_sets
  
def spreadsheet_batch_update(id: str, requests: list):
    """
    Performs a batch update to a spreadsheet with the given requests.
    """
    body = {
        "requests": requests
    }
    creds = get_creds()
    service = build("sheets", "v4", credentials=creds)
    service.spreadsheets().batchUpdate(spreadsheetId=id, body=body).execute()

def values_batch_update(id: str, data: list, clear=False):
    """
    Performs a batch update on the given spreadsheet with the given data. If clear is 
    set, this will perform a batch clear first.
    """
    body = {
       "valueInputOption": "RAW",
       "data": data
    }
    creds = get_creds()
    service = build("sheets", "v4", credentials=creds)
    service.spreadsheets().values().batchUpdate(spreadsheetId=id, body=body).execute()