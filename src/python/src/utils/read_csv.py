import logging, csv
from twisted.internet import defer
from sqlalchemy import Table
from sqlalchemy.dialects.mysql import insert, Insert
from rmq.utils.sql_expressions import compile_expression
from rmq.utils import TaskStatusCodes

from database.connection import get_db


class CSVDatabase:
    def __init__(self, csv_file, model: Table) -> None:
        self.model = model
        self.conn = get_db()
        self.csv_file = csv_file

    @defer.inlineCallbacks
    def read_csv_and_insert(self):
        with open(self.csv_file, mode='r') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                yield self.process_row(row[0])

        self.conn.close()
        
    @defer.inlineCallbacks
    def process_row(self, row):
        try:
            stmt: Insert = insert(self.model)
            stmt = stmt.on_duplicate_key_update({
                'status': TaskStatusCodes.NOT_PROCESSED
            }).values(url=row)

            yield self.conn.runQuery(*compile_expression(stmt))
        except Exception as e:
            logging.error("Error inserting item: %s", e)

    def run(self):
        self.read_csv_and_insert()


if __name__ == '__main__':
    csv_file = 'csv_file.csv'
    csvdatabase = CSVDatabase(csv_file)
    csvdatabase.run()
