from argparse import Namespace
from utils.read_csv import CSVDatabase
from rmq.utils import TaskStatusCodes
from rmq.commands import Producer
from sqlalchemy import select, update

from database.models import CategoryTargets


"""
Example of calling this command:
scrapy produce_category --file=csv_file.csv --task_queue=task --reply_to_queue=reply --chunk_size=500 --mode=worker
"""
class ProduceCategory(Producer):
    def __init__(self):
        super().__init__()
        self.csv_file = None

    def add_options(self, parser):
        super().add_options(parser)
        parser.add_argument(
            "-f",
            "--file",
            type=str,
            dest="csv_file",
            help="path to csv file",
        )

    def init_csv_file_name(self, opts: Namespace):
        csv_file = getattr(opts, "csv_file", None)
        if csv_file is None:
            raise NotImplementedError(
                "csv file name must be provided with options or override this method to return it"
            )
        self.csv_file = csv_file
        return csv_file
    
    def execute(self, _args: list[str], opts: Namespace):
        self.init_csv_file_name(opts)
        self.csv_database = CSVDatabase(self.csv_file, CategoryTargets)
        self.csv_database.read_csv_and_insert()
        super().execute(_args, opts)
    
    def build_task_query_stmt(self, chunk_size):
        """This method must returns sqlalchemy Executable or string that represents valid raw SQL select query

        stmt = select([DBModel]).where(
            DBModel.status == TaskStatusCodes.NOT_PROCESSED.value,
        ).order_by(DBModel.id.asc()).limit(chunk_size)
        return stmt
        """
        stmt = select(CategoryTargets).where(
            CategoryTargets.status == TaskStatusCodes.NOT_PROCESSED.value,
        ).order_by(CategoryTargets.id.asc()).limit(chunk_size)
        return stmt
    
    def build_task_update_stmt(self, db_task, status):
        """This method must returns sqlalchemy Executable or string that represents valid raw SQL update query

        return update(DBModel).where(DBModel.id == db_task['id']).values({'status': status})
        """
        return update(CategoryTargets).where(CategoryTargets.id == db_task['id']).values({'status': status})