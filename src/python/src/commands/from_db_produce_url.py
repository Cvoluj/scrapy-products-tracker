from sqlalchemy import select, update
from rmq.utils import TaskStatusCodes

from commands.abstract import DomainProducer
from database.models import ProductTargets


class ProduceUrl(DomainProducer):
    """
    Example of calling this command:
    scrapy from_db_produce_url --reply_to_queue=products_reply_queue --chunk_size=500 --mode=worker

    notice, --task_queue became unnecessary, because it alreade defined in CSVProducer. But if you want you still can change it 
    """

    def __init__(self):
        super().__init__()
        self.domain_queue_map = {domain: f'{queue}_products' for domain, queue in self.domain_queue_map.items()}
    
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
