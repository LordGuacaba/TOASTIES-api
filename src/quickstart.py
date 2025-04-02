import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from actions.sheets import *
from utils.sheet_updates import *
from utils.anal import scoresheet_anal

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "156vpN7iWzVjzkDRwoGiwnwagdMzId61GFGtujJlOnEY"
SAMPLE_RANGE_NAME = "Will!A2:C"
SAMPLE_STATS_ID = "16h5C1FTQkOIiSsfDAqqo0taPDCzCDv-0BGZhf42RG2Y"


def main():
  """Shows basic usage of the Sheets API.
  Prints values from a sample spreadsheet.
  """
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

  try:
    service = build("sheets", "v4", credentials=creds)

    # Call the Sheets API
    
    # names = get_sheet_names(SAMPLE_SPREADSHEET_ID)
    # ranges = [get_scoresheet_values(name) for name in names]
    # value_list = batch_get_values(SAMPLE_SPREADSHEET_ID, ranges)
    # print(value_list)

    writers = get_sheet_names(SAMPLE_SPREADSHEET_ID)
    ranges = [get_scoresheet_values(name) for name in writers]
    scoresheet_list = batch_get_values(SAMPLE_SPREADSHEET_ID, ranges)
    all_stats = scoresheet_anal(writers, scoresheet_list)
    values_batch_update(SAMPLE_STATS_ID, write_stats_json(writers, all_stats))

#     data = {
#         "range": "Clete!A:C",
#         "values": [
#           ["Question", "Answerer", "Points"],
#           [1, "Cade", -5],
#           ["", "Chris", 10],
#           [2, "Will", 15],
#           [3, "Tom", -5],
#           ["", "Chris", -5],
#           ["", "Will", -5],
#           [],
#           ["Roster", "Will"],
#           ["", "Tom"],
#           ["", "Cade"],
#           ["", "Chris"],
#           ["", "Adam"],
#           ["", "Danny"]
#         ]
#     }
#     values_batch_update(SAMPLE_SPREADSHEET_ID, [data])

#     if not values:
#       print("No data found.")
#       return

#     print("Answerer, Points:")
#     print(values)
#     for row in values:
#       # Print columns A and E, which correspond to indices 0 and 4.
#       print(f"{row[1]}, {row[2]}")
  except HttpError as err:
    print(err)


if __name__ == "__main__":
  main()