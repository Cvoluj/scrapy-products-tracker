from sqlalchemy import select, update
from rmq.utils import TaskStatusCodes

from commands import CSVProducer
from database.models import CategoryTargets


class ProduceCategory(CSVProducer):
    """
    Example of calling this command:
    scrapy from_csv_category_producer --file=csv_file.csv --reply_to_queue=category_reply_queue --chunk_size=500 --mode=worker

    notice, --task_queue became unnecessary, because it alreade defined in CSVProducer. But if you want you still can change it
    """
    model = CategoryTargets
    _DEFAULT_DELAY_TIMEOUT = 3

    def __init__(self):
        super().__init__()
        self.domain_queue_map = {domain: f'{queue}_category_task_queue' for domain, queue in self.domain_queue_map.items()}

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
