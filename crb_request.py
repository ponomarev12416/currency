import requests
import xml.etree.ElementTree as ET

from functools import lru_cache
from decimal import Decimal


def get_daily_currency_data(date=''):
    '''
    Provide the XML with valute curs on the given date.

    Goes to http://www.cbr.ru/scripts/XML_daily.asp and retreive
    valute curs on given date. Returns data in XML format.

    Parameters
    ----------
    date: str
        Date of type string in folowing format: dd/mm/yyyy.

    Returns
    str
        Return srting containing XML file.
    '''
    url = 'http://www.cbr.ru/scripts/XML_daily.asp'
    if date:
        url += f'?date_req={date}'
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(r.text)
    return response.text


def __extract_currency_value(data_xml, iso_code):
    '''
    Extract valute curs from XML file.

    Extract curs of the valute from the
    given XML file, coresponding the given iso_code.

    Parameters
    ----------
    data_xml: str
        String containing XML file
    iso_code: str
        Code of the valute to extract.
    
    Returns
    -------
    Decimal
        The decimal representation of the curs value.
    '''
    root = ET.fromstring(data_xml)
    for child in root:
        if child.attrib['ID'] == iso_code:
            return Decimal(child.find('Value').text.replace(',', '.'))


@lru_cache(maxsize=124)
def get_currency_value(date='', iso_code='R01235'):
    '''
    Return the value of the curs on the given date

    Parameters
    ----------
    date: str
        Date in format dd/mm/yyyy.
    iso_code: str
        Code of the valute which curs must be provided.

    Returns
    -------
    Decimal
        The valute value.
    '''
    return __extract_currency_value(get_daily_currency_data(date), iso_code)


if __name__ == '__main__':
    print(__extract_currency_value(get_daily_currency_data(), 'R01235'))

