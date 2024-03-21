from sqlalchemy import select, update
from rmq.utils import TaskStatusCodes

from commands import CSVProducer
from database.models import ProductTargets


"""
Example of calling this command:
scrapy produce_url --file=csv_file.csv --reply_to_queue=reply --chunk_size=500 --mode=worker

notice, --task_queue became unnecessary, because it alreade defined in CSVProducer. But if you want you still can change it 

"""
class ProduceUrl(CSVProducer):
    model = ProductTargets

    domain_queue_map = {
        "www.zoro.com": "zoro_task",
        "chat.openai.com": "chat_task"
    }

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