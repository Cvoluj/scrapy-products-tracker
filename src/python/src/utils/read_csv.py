import logging, csv
from furl import furl
from twisted.internet import reactor
from sqlalchemy import Table, select, desc
from sqlalchemy.dialects.mysql import insert, Insert
from rmq.utils.sql_expressions import compile_expression
from rmq.utils import TaskStatusCodes

from database.connection import get_db
from database.models import Sessions, ProductTargets


class CSVDatabase:
    def __init__(self, csv_file, model: Table) -> None:
        self.model = model
        self.conn = get_db()
        self.csv_file = csv_file

    def insert_from_csv(self):
        d = self.create_session()
        d.addCallback(lambda _: self.process_csv_with_session())
        
    def process_csv_with_session(self):
        with open(self.csv_file, mode='r') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                domain = self.parse_domain(row[0])
                self.process_row(row[0], domain)

    def process_row(self, row, domain):
        try:
            values = {
                "url": row,
                "domain": domain,
            }
            
            if type(self.model) is ProductTargets:
                values['external_id'] = row
                
            stmt: Insert = insert(self.model)
            stmt = stmt.on_duplicate_key_update({
                'status': TaskStatusCodes.NOT_PROCESSED,
            }).values(**values)

            self.conn.runQuery(*compile_expression(stmt))
        except Exception as e:
            logging.error("Error inserting item: %s", e)

    def create_session(self):
        try:
            stmt: Insert = insert(Sessions).values(csv_file=self.csv_file)
            return self.conn.runQuery(*compile_expression(stmt))
        except Exception as e:
            logging.error("Error inserting item: %s", e)

    def parse_domain(self, url):
        return furl(url).netloc
        


if __name__ == '__main__':
    csv_file = 'csv_file.csv'
    csvdatabase = CSVDatabase(csv_file)
    csvdatabase.insert_from_csv()
    reactor.run()
