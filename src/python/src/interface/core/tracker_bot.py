import logging
import telebot, threading, re, os, gc
from argparse import Namespace
from twisted.internet import reactor, task
from scrapy.utils.project import get_project_settings

from utils import CSVDatabase
from interface.core.markups import *
from database.models import ProductTargets, CategoryTargets
from commands.exporter import SessionExporter, HistoryExporter, CategoryExporter
from commands import StartTracking, StopTracking, GetSessions

from twisted.internet import reactor
import telebot
import threading


project_settings = get_project_settings()
bot = telebot.TeleBot(project_settings.get("BOT_TOKEN"))
access_code = project_settings.get("ACCESS_CODE")
user_has_access = {}
user_has_upload_files = {}
is_tracking_started = {}
sessions_dict = {}


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'You pressed start', reply_markup=start_markup())


@bot.message_handler(commands=['help'])
def help_(message):
    bot.send_message(message.chat.id, f'Hello, {message.from_user.username}!\n'
                                      'This bot is created for interaction with a product tracker. '
                                      'To start working, you need to enter a code to access all functions, '
                                      'namely:'
                                      '\n\n 1. Ability to upload a file.csv with the links of products '
                                      'or categories you are interested in for tracking.'
                                      '\n\n 2. Ability to get tracking results by session number, category link,'
                                      ' or product link.',
                     reply_markup=back_markup())


@bot.message_handler(commands=['back'])
def back(message):
    bot.send_message(message.chat.id, 'Back to start menu', reply_markup=start_markup())


@bot.message_handler(commands=['enter_code'])
def enter_access_code(message):
    bot.send_message(message.chat.id, 'please, enter your access code',
                     bot.register_next_step_handler(message=message,
                                                    callback=handle_access_code))


@bot.message_handler(commands=['main_menu'])
def main_menu_(message):
    bot.send_message(message.chat.id, 'Back to  menu', reply_markup=main_menu())


@bot.message_handler(commands=['upload'])
def upload(message):
    if user_has_access.get(message.from_user.id):
        bot.send_message(message.chat.id, 'Please, choose the type of uploaded links!\n'
                                          'The file must be .csv format!', reply_markup=upload_markup())
    else:
        bot.send_message(message.chat.id, 'access denied! Please, enter access code')
        bot.register_next_step_handler(message=message, callback=handle_access_code)


@bot.message_handler(commands=['categories'])
def categories_upload(message):
    if user_has_access.get(message.from_user.id):
        # Check if the user hasn't already uploaded a file with categories
        if not user_has_upload_files.get(message.from_user.id, {}).get('category'):
            bot.send_message(message.chat.id, 'Please upload a CSV file with categories',
                             bot.register_next_step_handler(message=message, callback=handle_csv_file, bot=bot,
                                                            upload_prefix='CategoryTargets'))
            if message.from_user.id not in user_has_upload_files:
                user_has_upload_files[message.from_user.id] = {}
            # Set the value of "category" key to True to indicate that the user has uploaded a file with categories
            user_has_upload_files[message.from_user.id]["category"] = True
        else:
            bot.send_message(message.chat.id, "Error!\n"
                                              "You have already uploaded a file with categories!\n"
                                              " You can start tracking the current links,"
                                              f" and after stopping tracking upload a new file.{user_has_upload_files}")
    else:
        bot.send_message(message.chat.id, 'access denied! Please, enter access code')
        bot.register_next_step_handler(message=message, callback=handle_access_code)


@bot.message_handler(commands=['products'])
def products_upload(message):
    if user_has_access.get(message.from_user.id):
        # Check if the user hasn't already uploaded a file with products
        if not user_has_upload_files.get(message.from_user.id, {}).get('product'):
            bot.send_message(message.chat.id, 'Please upload a CSV file with products',
                             bot.register_next_step_handler(message=message, callback=handle_csv_file, bot=bot,
                                                            upload_prefix='ProductTargets'))
            if message.from_user.id not in user_has_upload_files:
                user_has_upload_files[message.from_user.id] = {}
            # Set the value of "product" key to True to indicate that the user has uploaded a file with products
            user_has_upload_files[message.from_user.id]["product"] = True
        else:
            bot.send_message(message.chat.id, f'Error!\n'
                                              f'You have already uploaded a file with products!\n'
                                              f'You can start tracking the current links,'
                                              f'and after stopping tracking upload a new file.{user_has_upload_files}')
    else:
        bot.send_message(message.chat.id, 'access denied! Please, enter access code')
        bot.register_next_step_handler(message=message, callback=handle_access_code)


@bot.message_handler(commands=['download'])
def download(message):
    if user_has_access.get(message.from_user.id):
        sessions = GetSessions()
        sessions.init()
        result = sessions.execute(None)

        def send_products(msg):
            product_sessions = "\n".join([str(item['id']) for item in msg if item['target'] == 'product'])
            bot.send_message(message.chat.id, f"Session numbers by PRODUCT:\n{product_sessions}")
            return msg

        def send_categories(msg):
            category_sessions = "\n".join([str(item['id']) for item in msg if item['target'] == 'category'])
            bot.send_message(message.chat.id, f"Session numbers by CATEGORY:\n{category_sessions}")
            return msg

        result.addCallback(lambda result: send_products(result))
        result.addCallback(lambda result: send_categories(result))
        bot.send_message(message.chat.id, f'In this menu you can get the results.\n'
                                          f'You can get results by session number, product link, category link',
                         reply_markup=get_results_markup())

    else:
        bot.send_message(message.chat.id, 'access denied! Please, enter access code')
        bot.register_next_step_handler(message=message, callback=handle_access_code)


@bot.message_handler(commands=['category_link'])
def handle_category_link(message):
    if user_has_access.get(message.from_user.id):
        bot.send_message(message.chat.id, 'Please enter the category link:')
        bot.register_next_step_handler(message=message, callback=export_category_results)
    else:
        bot.send_message(message.chat.id, 'Access denied! Please enter access code.')
        bot.register_next_step_handler(message=message, callback=handle_access_code)


@bot.message_handler(commands=['product_link'])
def handle_history_link(message):
    if user_has_access.get(message.from_user.id):
        bot.send_message(message.chat.id, 'Please enter the product link, to get history:')
        bot.register_next_step_handler(message=message, callback=export_history_results)
    else:
        bot.send_message(message.chat.id, 'Access denied! Please enter access code.')
        bot.register_next_step_handler(message=message, callback=handle_access_code)


@bot.message_handler(commands=['session_id'])
def handle_session_id(message):
    if user_has_access.get(message.from_user.id):
        bot.send_message(message.chat.id, 'Please enter the session id:',)
        bot.register_next_step_handler(message=message, callback=export_session_results)
    else:
        bot.send_message(message.chat.id, 'Access denied! Please enter access code.')
        bot.register_next_step_handler(message=message, callback=handle_access_code)


@bot.message_handler(commands=['tracker'])
def tracker_menu(message):
    user_id = message.from_user.id
    if user_has_access.get(user_id):
        bot.send_message(message.from_user.id, "In this menu, you can start tracking the categories\n"
                                               " and products you have uploaded, \n"
                                               "as well as stop tracking if it was initiated earlier.",
                         reply_markup=tracker_markup())
    else:
        bot.send_message(message.chat.id, 'Access denied! Please enter access code.')
        bot.register_next_step_handler(message=message, callback=handle_access_code)


@bot.message_handler(content_types=["text"])
def handle_text_commands(message):
    global product_tracker
    global category_tracker
    user_id = message.from_user.id
    product_file = user_has_upload_files.get(message.from_user.id, {}).get('product')
    category_file = user_has_upload_files.get(message.from_user.id, {}).get('category')

    if user_has_access.get(user_id):
        match message.text, is_tracking_started.get(user_id):
            case "start_tracking", None:
                bot.send_message(message.chat.id, f"Tracking has been started")

                if product_file:
                    opts_product = Namespace(model='ProductTargets')

                    product_tracker = StartTracking()
                    product_tracker.settings = project_settings
                    product_tracker.init()
                    product_tracker.logger = logging.getLogger(name=StartTracking.__name__)

                    product_tracker.execute(None, opts_product)
                if category_file:
                    opts_category = Namespace(model='CategoryTargets')

                    category_tracker = StartTracking()
                    category_tracker.settings = project_settings
                    category_tracker.init()
                    category_tracker.logger = logging.getLogger(name=StartTracking.__name__)

                    category_tracker.execute(None, opts_category)
                is_tracking_started[user_id] = True

            case "stop_tracking", True:
                bot.send_message(message.chat.id, f"stop_tracking {user_has_upload_files}")

                if product_file:
                    opts_product = Namespace(model='ProductTargets', csv_file=product_file)

                    product_tracker.stop()

                    product_disabler = StopTracking()
                    product_disabler.settings = project_settings
                    product_disabler.init()
                    product_disabler.logger = logging.getLogger(name=StopTracking.__name__)

                    product_disabler.execute(None, opts_product)
                if category_file:
                    opts_category = Namespace(model='CategoryTargets', csv_file=category_file)

                    category_tracker.stop()

                    category_disabler = StopTracking()
                    category_disabler.settings = project_settings
                    category_disabler.init()
                    category_disabler.logger = logging.getLogger(name=StopTracking.__name__)

                    category_disabler.execute(None, opts_category)
                is_tracking_started[user_id] = None

            case "start_tracking", True:
                bot.send_message(message.chat.id, "Tracking has been already activated")

            case "stop_tracking", None:
                bot.send_message(message.chat.id, "Tracking has been already stopped")

    else:
        bot.send_message(message.chat.id, 'Access denied! Please enter access code.')
        bot.register_next_step_handler(message=message, callback=handle_access_code)

def handle_access_code(message):
    if message:
        if message.text == access_code:
            user_has_access[message.from_user.id] = True
            bot.send_message(message.chat.id, f"Your code accepted, {message.from_user.username}",
                             reply_markup=main_menu())

        else:
            bot.send_message(message.chat.id, "Incorrect code!")


def handle_csv_file(message, upload_prefix, bot):
    if message.document.mime_type == 'text/csv':

        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        file_name = message.document.file_name
        file_path = f'../../../../storage/{file_name}'

        if upload_prefix == "ProductTargets":
            model = ProductTargets
            key = 'product'
        else:
            model = CategoryTargets
            key = 'category'

        csv_reader = CSVDatabase(file_path, model)
        reactor.callInThread(csv_reader.insert_from_csv)
        user_has_upload_files[message.from_user.id][key] = file_path
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.send_message(message.chat.id, f'Saved! {upload_prefix}')
    else:
        bot.reply_to(message.chat.id, "Please upload a CSV file.")


def export_history_results(message):
    product_url = message.text
    opts = Namespace(url=product_url)

    history_exporter = HistoryExporter()
    history_exporter.init()
    history_exporter.logger = logging.getLogger(name=HistoryExporter.__name__)
    history_exporter.settings = project_settings

    d = task.deferLater(reactor, 0, history_exporter.execute, None, opts)
    bot.send_message(message.chat.id, f'Exporting history results...')
    d.addCallback(lambda _: history_exporter.callback_filepath())
    d.addCallback(lambda file_path: send_file(message, file_path))


def export_category_results(message):
    category_url = message.text
    opts = Namespace(category=category_url)

    category_exporter = CategoryExporter()
    category_exporter.init()
    category_exporter.logger = logging.getLogger(name=CategoryExporter.__name__)
    category_exporter.settings = project_settings

    d = task.deferLater(reactor, 0, category_exporter.execute, None, opts)
    bot.send_message(message.chat.id, f'Exporting category results...')
    d.addCallback(lambda _: category_exporter.callback_filepath())
    d.addCallback(lambda file_path: send_file(message, file_path))

def export_session_results(message):
    session_id = int(message.text)
    opts = Namespace(session=session_id)

    session_exporter = SessionExporter()
    session_exporter.init()
    session_exporter.logger = logging.getLogger(name=CategoryExporter.__name__)
    session_exporter.settings = project_settings

    d = task.deferLater(reactor, 0, session_exporter.execute, None, opts)
    bot.send_message(message.chat.id, f'Exporting session results...')
    d.addCallback(lambda _: session_exporter.callback_filepath())
    d.addCallback(lambda file_path: send_file(message, file_path))


def send_file(message, file_path):
    try:
        with open(file_path, 'rb') as file:
            bot.send_document(chat_id=message.chat.id, document=file)
    except:
        bot.send_message(message.chat.id, "File wasn't created, try send correct query")


def start_bot():
    threading.Thread(target=bot.polling, kwargs={'none_stop': True}).start()
    reactor.run()

start_bot()
