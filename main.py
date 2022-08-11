import retrieve_changes
import config
import logging

from time import sleep
from service import Service
from db_service import DataBase
from retrieve_changes import fetch_start_page_token, fetch_changes
def main():
    logging.getLogger('googleapicliet.discovery_cache').setLevel(logging.CRITICAL)
    FORMAT = '%(asctime)s %(message)s'
    logging.basicConfig(filename='info.log', encoding='utf-8', level=logging.INFO, format=FORMAT)
    logging.info('Started')
    # Instantiate service to work with google sheet and 
    # google driver
    service_obj = Service(config.SECRET_FILE, config.SCOPES)
    sheet = service_obj.get_spreadsheets(config.SPREADSHEET_ID,
            config.RANGE_NAME)
    records = Service.prepare_data(sheet)
    # Instantiate object for work with database.
    db = DataBase(config.DATABASE, config.USER, config.PASSWORD)
    db.insert(records)
    # The script check if the given google spreadsheet has been changed
    # using Google API. It acquires token every 30 sec. If the token 
    # number greater then the current one, we should downloads the 
    # data from google disk.
    previous_token = fetch_start_page_token(service_obj.credentials)
    logging.info('Current token %s', previous_token)
    while True:
        current_token = fetch_start_page_token(service_obj.credentials)
        if current_token != previous_token:
            logging.info('New token %s', current_token)
            changed_files = fetch_changes(previous_token, 
                    service_obj.credentials)
            previous_token = current_token
            if config.SPREADSHEET_ID in changed_files:
                logging.info('The spreadsheet has been changed.')
                sheet = service_obj.get_spreadsheets(config.SPREADSHEET_ID,
                        config.RANGE_NAME)
                records = Service.prepare_data(sheet)
                db.insert(records)
        sleep(30)

if __name__ == '__main__':
    main()
