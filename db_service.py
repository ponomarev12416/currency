from __future__ import print_function

import os.path
import psycopg2
import psycopg2.extras
import logging

from collections import namedtuple
from datetime import datetime
from decimal import Decimal
from crb_request import get_currency_value


class DataBase:

    # Column "keep_it" is used to keep the data up to date.
    sql_init_statement = '''
        CREATE TABLE IF NOT EXISTS stock(
            number       VARCHAR(5)     UNIQUE NOT NULL,
            order_number VARCHAR(14)    UNIQUE NOT NULL,
            cost_usd     DECIMAL(14, 2)        NOT NULL,
            supply_date  DATE                  NOT NULL,
            cost_rub     DECIMAL(14, 2)        NOT NULL,
            keep_it      BOOLEAN               NOT NULL DEFAULT FALSE,

            PRIMARY KEY (order_number)
        );
        '''
    sql_insert_statement = '''
        INSERT INTO stock 
            VALUES(
                 %(number)s,
                 %(order_number)s,
                 %(cost_usd)s, 
                 %(supply_date)s, 
                 %(cost_rub)s, 
                 %(keep_it)s
            )
        ON CONFLICT (order_number) DO UPDATE
            SET 
                number = %(number)s,
                order_number = %(order_number)s,
                cost_usd = %(cost_usd)s,
                supply_date = %(supply_date)s,
                cost_rub = %(cost_rub)s,
                keep_it = %(keep_it)s;
        '''

    def __init__(self, data_base, user, password):
        self.data_base = data_base
        self.user = user
        self.password = password

        con = self.__get_connection()
        with con:
            with con.cursor() as cursor:
                cursor.execute(self.sql_init_statement)
            con.commit()
        con.close()
        logging.info('Connected to %s as %s', data_base, user)
    
    def __get_connection(self):
        return psycopg2.connect(
                f'dbname={self.data_base} user={self.user} password={self.password}')

    def insert(self, processed_data):
        '''
        Insert the given batch of rows to the table.

        If the record with the given "order_number" is already exists, 
        update its data. If table contains record, which correspondent
        row in spreadsheet was deleted, this record would be deleted.

        Parameters
        ----------
        processed_data: List
            List of rows to be inserted in table.

        Returns
        -------
        None
        '''
        con = self.__get_connection()
        print('INSERTING DATA TO THE DATABASE.')
        with con, con.cursor() as cursor:
                logging.info('Inserting record to the table.')
                try:
                    psycopg2.extras.execute_batch(
                        cur=cursor,
                        sql=self.sql_insert_statement,
                        argslist=processed_data,
                        page_size=100,
                    )
                    logging.info('Data inserted successfully.')
                    # Delete rows from table, which were added earlier,
                    # but now do not present in the spreadsheet.
                    cursor.execute('''
                            DELETE FROM
                                stock
                            WHERE
                                keep_it = FALSE;
                            ''')
                    cursor.execute('''
                            UPDATE 
                                stock
                            SET
                                keep_it = FALSE;
                            ''')
                except Exception as e:
                    logging.error(e)
                con.commit()
        con.close()

