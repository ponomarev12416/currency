import os.path
import logging
import crb_request

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from collections import namedtuple
from datetime import datetime
from decimal import Decimal

from crb_request import get_currency_value

# Numbers of columns in google sheet
NUMBER = 0
ORDER_NUMBER = 1
COST_USD = 2
SUPPLY_DATE = 3


class Service:

    def __init__(self, secret_file, scopes):
        try:
            self.credentials = self.make_credentials(secret_file, scopes) 
            self.service = build('sheets', 'v4', credentials=self.credentials,
                    cache_discovery=False)
            self.sheet = self.service.spreadsheets()
        except HttpError as err:
            logging.error(err)

    def make_credentials(self, secret_file, scopes):
        try:
            credendtials = (service_account.Credentials
                    .from_service_account_file(secret_file, scopes=scopes))
        except HttpError as err:
            logging.error(err)
        return credendtials
    
    def get_spreadsheets(self, sheet_id, range_name):
        '''
        Returns the data of the given google sheet.

        Return the list of rows from specified google sheet 
        and coresponding range.

        Parameters
        ----------
        shet_id: str
            Spreadsheet id.
        range_name: str
            Name of the range in spreadsheet.

        Returns
        -------
        list
            List of rows from spreadsheet, except for the headers.
        '''
        logging.info('Acquiring google sheet')
        try:
            result = self.sheet.values().get(spreadsheetId=sheet_id, 
                    range=range_name).execute()
            values = result.get('values', [])
            if not values:
                logging.info('No data found.')
                return
            # Remove headers
            values.pop(0)
            logging.info('Acquired google sheet')
            return values
        except HttpError as err:
                logging.info(err)

    @staticmethod
    def convert_currency(value, date, valute):
        '''
        Converts valute to RUB.

        Convert the provided vlue from given valute to RUB, according
        to the given date.

        Parameters
        ----------
        value: Decimal
            The value to convert.
        date: string
            Date in form dd.mm.yyyy.
        valute:
            iso_code of the valute to be converted.

        Returns
        -------
        Decimal
            The amount of RUB converted from the given value.
        '''
        coef = get_currency_value(date.replace('.', '/'), valute)
        return Decimal(value) * coef

    @staticmethod
    def prepare_data(raw_data):
        '''
        Process raw data from the spreadsheet.

        Constructs the generator, which elements is a dictionary,
        representing the processed row from the spreadsheet. 
        Adds new column "cost_rub" and converts date to the appropriate type.
        
        Parameters
        ----------
        raw_data: list
            List of rows from the spreadsheet, without headers.

        Returns
        -------
        list[dict]
            List of dictionary. Each dict represents extended row 
            with addition information from spreadsheet.
        '''
        return (dict(number=row[NUMBER],
                     order_number=row[ORDER_NUMBER],
                     cost_usd=row[COST_USD],
                     # Compute the price in RUB
                     cost_rub=Service.convert_currency(
                         row[COST_USD], row[SUPPLY_DATE], 'R01235'),
                     supply_date=datetime.strptime(
                         row[SUPPLY_DATE], '%d.%m.%Y'),
                     keep_it=True) for row in raw_data if len(row) == 4)


def main():
    service = Service('credentials.json', SCOPES)
    data = service.get_spreadsheets(SPREADSHEET_ID, 'Лист1')
    print(data)


if __name__ == '__main__':
    main()

