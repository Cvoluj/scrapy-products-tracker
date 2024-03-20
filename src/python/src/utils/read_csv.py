import logging, csv
from database.connection import get_db
from rmq.utils.sql_expressions import compile_expression
from twisted.internet import defer
from twisted.internet import reactor
from sqlalchemy import insert
from database.models import Target          # TODO: replace with actual Target model
# from items.url_item import TargetItem     # same


class CSVDatabase():
    def __init__(self, csv_file) -> None:
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
            query = insert(Target).prefix_with('IGNORE').values(url=row)
            yield self.conn.runQuery(*compile_expression(query))
        except Exception as e:
            logging.error("Error inserting item: %s", e)

    def run(self):
        self.read_csv_and_insert()
        reactor.run()


if __name__ == '__main__':
    csv_file = 'csv_file.csv'
    csvdatabase = CSVDatabase(csv_file)
    csvdatabase.run()
