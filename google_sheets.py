import socket
orig_getaddrinfo = socket.getaddrinfo

def ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

socket.getaddrinfo = ipv4_only
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import numpy as np
import traceback

class GoogleSheetSaver():

    sheets = None

    def connect(self):
        """ Connect to google spread sheet """
        print("Started google spread sheet connecting")
        try:
            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
            creds = service_account.Credentials.from_service_account_file(
                'service_account.json', scopes=SCOPES
            )
            service = build('sheets', 'v4', credentials=creds)
            self.sheets = service.spreadsheets()
            return True
        except Exception as e:
            trace = traceback.format_exc()
            print("Error while trying go connect to google spreadsheet: ")
            print(trace)
            return False

    def save_data(self, data, spreadsheet_id):
        """ Prepare data and save """
        print("Saving data to google spread sheet")
        try:
            # Prepare data 
            keys = list(data[0].keys())
            values = []
            for item in data:
                data_list_item = list(item.values())
                values.append(data_list_item)
            
            body = {
                "valueInputOption": "USER_ENTERED",
                "data": [
                    {"range": "Sheet1!A1", "values": [keys]},
                    {"range": "Sheet1!A2", "values": values},
                ],
            }
            # Save to sheet
            self.sheets.values().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
            return True
        except Exception as e:
            trace = traceback.format_exc()
            print("Error while trying go save data to google spreadsheet: ")
            print(trace)
            return False


    def save(self, data, spreadsheet_id):
        """ Save data to google spreadsheet """
        connect_result = self.connect()
        if connect_result:
            result = self.save_data(data, spreadsheet_id)
            if result:
                print("Done!")