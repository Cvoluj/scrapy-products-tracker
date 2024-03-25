from rmq.commands import Consumer

from sqlalchemy.dialects.mysql import insert, Insert
from database.models import CategoryTargets


class ConsumeCategoryFromQueue(Consumer):
    
    def build_message_store_stmt(self, message_body):
        """If processing message task requires several queries to db or single query has extreme difficulty
        then this self.process_message method could be overridden.
        In this case using of self.build_message_store_stmt method is not required
        and could be overridden with pass statement

        Example:
        message_body['status'] = TaskStatusCodes.SUCCESS.value
        del message_body['created_at']
        del message_body['updated_at']
        stmt = insert(SearchEngineQuery)
        stmt = stmt.on_duplicate_key_update({
            'status': stmt.inserted.status
        }).values(message_body)
        return stmt
        """
        del message_body['created_at']
        del message_body['updated_at']
        stmt: Insert = insert(CategoryTargets)
        stmt = stmt.on_duplicate_key_update({
            'status': stmt.inserted.status
        }).values(message_body)

        return stmt