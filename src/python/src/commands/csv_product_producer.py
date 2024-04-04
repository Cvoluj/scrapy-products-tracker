from sqlalchemy import select, update
from rmq.utils import TaskStatusCodes

from commands import CSVProducer
from database.models import ProductTargets


class CSVProductProducer(CSVProducer):
    """
    Example of calling this command:
    scrapy csv_product_producer --chunk_size=500 --mode=worker
    notice, --task_queue became unnecessary, because it already defined. But if you want you still can change it
    """
    model = ProductTargets

    def __init__(self):
        super().__init__()
        self.csv_file = self.project_settings.get("PRODUCTS_FILE")
        self.logger.warning(self.csv_file)
        self.domain_queue_map = {domain: f'{queue}_products_task_queue' for domain, queue in self.domain_queue_map.items()}
        self.reply_to_queue_name = self.project_settings.get("RMQ_PRODUCT_REPLY_QUEUE")

    def build_task_query_stmt(self, chunk_size):
        """This method must returns sqlalchemy Executable or string that represents valid raw SQL select query

        stmt = select([DBModel]).where(
            DBModel.status == TaskStatusCodes.NOT_PROCESSED.value,
        ).order_by(DBModel.id.asc()).limit(chunk_size)
        return stmt
        """
        stmt = select(ProductTargets).where(
            ProductTargets.status == TaskStatusCodes.NOT_PROCESSED.value,
        ).order_by(ProductTargets.id.asc()).limit(chunk_size)
        return stmt

    def build_task_update_stmt(self, db_task, status):
        """This method must returns sqlalchemy Executable or string that represents valid raw SQL update query

        return update(DBModel).where(DBModel.id == db_task['id']).values({'status': status})
        """
        return update(ProductTargets).where(ProductTargets.id == db_task['id']).values({'status': status})
