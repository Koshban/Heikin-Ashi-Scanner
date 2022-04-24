from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config.config import Mode

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1L0zpYciVXrCv9wFtsyvx1IcDagEkwKYFHJyAfPRz2Pg'
INDIA_SPREADSHEET_ID="14SKoVrc3gBfTo4aHeqohuwkD5krTbc9HglnBnNzFoKs"
SAMPLE_RANGE_NAME = '{0}!A1:D500'

tab_names=["Main", "SA", "RB", "DDPortfolio", "Exclude"]
india_tab_names=["IndiaNames", "Exclude"]


def getNamesFromGoogleSheet(mode, dict_symbols):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    print("calling")
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('sheets', 'v4', credentials=creds)
    # Call the Sheets API
    sheet = service.spreadsheets()
    if mode == Mode.india:
        for tab in india_tab_names:
            getIndiaNames(dict_symbols, sheet, tab)
    else:
        for tab in tab_names:
            getTabValues(dict_symbols, sheet, tab)


def getIndiaNames(dict_symbols, sheet, tab_name):
    result = sheet.values().get(spreadsheetId=INDIA_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME.format(tab_name)).execute()
    values = result.get('values', [])
    if not values:
        print('No data found.')
    else:
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            if not row[0] or "Ticker" in row[0] or not isValidColumn(row[0]):
                continue
            name = row[0].strip()
            my_source = "Exclude"
            if "Exclude" not in tab_name:
                my_source = row[1].strip()
            sources = dict_symbols.get(name, None)
            if sources:
                if tab_name in sources:
                    continue  ## for dplicates in tab
                sources = "{0},{1}".format(sources, my_source)
            else:
                sources = my_source
            dict_symbols[name] = sources


def getTabValues(dict_symbols, sheet, tab_name):
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME.format(tab_name)).execute()
    values = result.get('values', [])
    if not values:
        print('No data found.')
    else:
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            if not row[0] or "Ticker" in row[0] or not isValidColumn(row[0]):
                continue
            name = row[0].strip()
            my_source = tab_name
            if "Main" in tab_name:
                my_source = row[2].strip()
            sources = dict_symbols.get(name, None)
            if sources:
                if tab_name in sources:
                    continue  ## for dplicates in tab
                sources = "{0},{1}".format(sources, my_source)
            else:
                sources = my_source
            dict_symbols[name] = sources


def isValidColumn(entry):
    if entry is None or entry == None or len(entry) < 1:
        return False
    return True