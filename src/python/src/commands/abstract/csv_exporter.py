import csv, datetime
from os import path
from argparse import Namespace
from twisted.internet import reactor
from rmq.utils.sql_expressions import compile_expression
from scrapy.utils.project import get_project_settings
from typing import List, Dict
from sqlalchemy.sql import ClauseElement
from commands.base import BaseCommand
from database.connection import get_db


class CSVExporter(BaseCommand):
    """
    Lightweight version of original BaseCSVExporter with option of creating select query by hand
    """
    file_timestamp_format: str = '%Y%b%d%H%M%S'
    file_extension: str = 'csv'
    file_path: str = ''
    file_exists: bool = False
    headers: List[str] = []
    new_mapping: Dict[str, str] = {}
    filename_prefix: str = ''
    filename_postfix: str = ''
    project_setting = get_project_settings()

    def init(self):
        self.conn = get_db()

    def select_results(self):
        """
        This method must returns sqlalchemy Executable or string that represents valid raw SQL select query
        """
        raise NotImplementedError

    def get_interaction(self, transaction):
        """If building task requires several queries to db or single query has extreme difficulty
        then this method could be overridden.
        In this case using of self.build_task_query_stmt method is not required
        and could be overridden with pass statement"""
        stmt = self.select_results()
        if isinstance(stmt, ClauseElement):
            # parameter passing method describes here: https://peps.python.org/pep-0249/#id20
            transaction.execute(*compile_expression(stmt))
        else:
            transaction.execute(stmt)

        return transaction.fetchall()

    def get_headers(self, row: Dict) -> None:
        """
        Get headers for csv file
        """
        if not self.headers:
            self.headers = list(row.keys())

    def map_columns(self, rows: List[Dict]) -> List[Dict]:
        if self.new_mapping:
            for row in rows:
                for old_name, new_name in self.new_mapping.items():
                    row[new_name] = row.pop(old_name)
            return rows
        return rows

    def process_export(self, rows):
        """
        if we got rows - create file
        if no rows and file created - export finished
        if no rows and file don't created - nothing found
        """
        if not rows:
            if self.file_exists:
                self.logger.warning(f'Export finished successfully to {path.basename(self.file_path)}.')
            else:
                self.logger.warning('Nothing found')
            reactor.stop()
        else:
            rows = self.map_columns(rows)
            self.get_headers(rows[0])
            self.save(rows)

    def save(self, rows: List[Dict]) -> None:
        """
        use context manager to create csv file, add results from interaction and
        write header for file
        """
        with open(self.file_path, 'a', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.headers)
            if not self.file_exists:
                writer.writeheader()
                self.file_exists = True
            self.logger.warning(f'Exporting to {self.file_path}...')
            writer.writerows(rows)
        self.process_export(None)

    def execute(self, args, opts: Namespace):
        """
        prepare `self.file_path`, call `get_interaction`,
        on results call callback for processing export
        """
        self.file_path = self.get_file_path()
        d = self.conn.runInteraction(self.get_interaction)
        d.addCallback(self.process_export)

    def get_file_path(self, timestamp_format=None, prefix=None, postfix=None, extension=None):
        """
        creating file name + export path
        """
        if timestamp_format is None:
            timestamp_format = self.file_timestamp_format
        if prefix is None:
            prefix = self.filename_prefix
        if postfix is None:
            postfix = self.filename_postfix
        if extension is None:
            extension = self.file_extension
        export_path = path.join(path.abspath(self.project_setting.get("STORAGE_PATH")), 'export')
        file_name = f'{prefix}{datetime.datetime.now().strftime(timestamp_format)}{postfix}.{extension}'
        return path.join(export_path, file_name)

    def run(self, args: list[str], opts: Namespace):
        reactor.callLater(0, self.execute, args, opts)
        reactor.run()

