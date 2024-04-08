from argparse import Namespace
from scrapy.commands import ScrapyCommand
from twisted.internet import reactor, task
from sqlalchemy import update, select, desc
from sqlalchemy.dialects.mysql import Insert, insert
from rmq.utils.sql_expressions import compile_expression
from rmq.utils import TaskStatusCodes
from commands.base import BaseCommand
from database.models import *
from database.connection import get_db


class StartTracking(BaseCommand):
    """
    StartTracking class sets model.status=0 and updates model.session field.
    Depending on model: ProductTargets or CategoryTargets sets Session.target to 'product' or 'category'

    Example of command line:
    scrapy start_tracking --model=ProductTargets
    """
    MINUTE = 60

    def init(self):
        """
        Initialize StartTracking instance.

        This method sets the interval for session tracking, initializes some instance variables, and establishes a database connection.

        Returns:
            None
        """

        self.interval = self.settings.getint(("SESSION_INTERVAL")) * self.MINUTE
        self.model = None
        self.session_file = None
        self.current_session_id = None
        self.previous_session_id = None
        self.conn = get_db()

    def add_options(self, parser):
        """
        Add command-line options for the StartTracking command.

        Args:
            parser (argparse.ArgumentParser): The ArgumentParser instance to which options will be added.

        Returns:
            None
        """

        ScrapyCommand.add_options(self, parser)
        parser.add_argument(
            "-m",
            "--model",
            type=str,
            dest="model",
            help="SQLAlchemy model name",
        )

    def init_model_name(self, opts: Namespace):
        """
        Initialize the model class based on the provided command-line options.

        Args:
            opts (argparse.Namespace): The Namespace object containing command-line options.

        Raises:
            NotImplementedError: If the model name is not provided with options or overridden method.

        Returns:
            class: The model class.
        """

        model = getattr(opts, "model", None)
        if model is None:
            raise NotImplementedError(
                "Model name must be provided with options or override this method to return it"
            )
        model_class = globals().get(model)
        if model_class is None or not issubclass(model_class, Base):
            raise ImportError(f"Model class '{model}' not found or is not a subclass of Table")

        self.model = model_class
        if hasattr(self.model, 'title'):
            self.target = 'product'
        else:
            self.target = 'category'

        return model_class

    def get_previous_session(self):
        """
        Get the previous session information from the database.

        Returns:
            twisted.internet.defer.Deferred: A deferred object representing the asynchronous database query.
        """

        stmt = select(Sessions).where(Sessions.target == self.target).order_by(desc(Sessions.id)).limit(1)
        deferred = self.conn.runQuery(*compile_expression(stmt))
        deferred.addCallback(self.handle_previous_session_result)
        return deferred

    def get_current_session(self):
        """
        Get the current session information from the database.

        Returns:
            twisted.internet.defer.Deferred: A deferred object representing the asynchronous database query.
        """

        stmt = select(Sessions).where(Sessions.target == self.target).order_by(desc(Sessions.id)).limit(1)
        deferred = self.conn.runQuery(*compile_expression(stmt))
        deferred.addCallback(self.handle_current_session_result)
        return deferred

    def handle_current_session_result(self, result):
        """
        Handle the result of the current session query.

        Args:
            result: The result of the query.

        Returns:
            None
        """

        self.current_session_id = result[0].get('id') if result else None

    def handle_previous_session_result(self, result):
        """
        Handle the result of the previous session query.

        Args:
            result: The result of the query.

        Returns:
            None
        """

        self.session_file = self.session_file = result[0].get('csv_file') if result else None
        self.previous_session_id = result[0].get('id') if result else None

    def execute(self, args, opts: Namespace):
        """
        Execute the StartTracking command.

        Args:
            args (list): The command-line arguments.
            opts (argparse.Namespace): The Namespace object containing command-line options.

        Returns:
            None
        """

        self.init_model_name(opts)

        repeat_session_task = task.LoopingCall(self.repeat_session)
        reactor.callLater(self.interval, repeat_session_task.start, self.interval)

    def update_session(self):
        """
        Update the session information in the database.

        Returns:
            twisted.internet.defer.Deferred: A deferred object representing the asynchronous database query.
        """

        try:
            stmt: Insert = insert(Sessions).values(csv_file=self.session_file, target=self.target)

            return self.conn.runQuery(*compile_expression(stmt))
        except Exception as e:
            self.logger.error("Error inserting item: %s", e)

    def update_status(self):
        """
        Update the status of tracked items in the database.

        Returns:
            twisted.internet.defer.Deferred: A deferred object representing the asynchronous database query.
        """

        try:
            self.logger.warning(self.current_session_id)
            stmt = update(self.model).where(self.model.is_tracked == 1, self.model.session == self.previous_session_id).values(
                status=TaskStatusCodes.NOT_PROCESSED,
                session=self.current_session_id
            )

            self.conn.runQuery(*compile_expression(stmt))
        except Exception as e:
            self.loggerr.error("Error updating item: %s", e)

    def repeat_session(self):
        """
        Repeat the session tracking process.

        Returns:
            None
        """

        d = self.get_previous_session()
        d.addCallback(lambda _: self.update_session())
        d.addCallback(lambda _: self.get_current_session())
        d.addCallback(lambda _: self.update_status())
        self.logger.warning('STATUS WERE UPDATED')

    def run(self, args: list[str], opts: Namespace):
        """
        Run the StartTracking command.

        Args:
            args (list[str]): The command-line arguments.
            opts (argparse.Namespace): The Namespace object containing command-line options.

        Returns:
            None
        """

        reactor.callLater(0, self.execute, args, opts)
        reactor.run()

