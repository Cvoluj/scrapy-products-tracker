from scrapy.utils.project import get_project_settings
from commands.exporter import SessionExporter, HistoryExporter, CategoryExporter
from interface.core.markups import *
from database.models import ProductTargets, CategoryTargets
from utils import CSVDatabase
from argparse import Namespace
import logging


project_settings = get_project_settings()
bot = telebot.TeleBot(project_settings.get("BOT_TOKEN"))
access_code = project_settings.get("ACCESS_CODE")
user_has_access = {}


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
        bot.send_message(message.chat.id, 'access denied! Please, enter access code',
                         bot.register_next_step_handler(message=message, callback=handle_access_code))


@bot.message_handler(commands=['categories'])
def categories_upload(message):
    if user_has_access.get(message.from_user.id):
        bot.send_message(message.chat.id, 'Please upload a CSV file with categories',
                         bot.register_next_step_handler(message=message, callback=handle_csv_file, bot=bot,
                                                        upload_prefix='CategoryTargets'))
    else:
        bot.send_message(message.chat.id, 'access denied! Please, enter access code',
                         bot.register_next_step_handler(message=message, callback=handle_access_code))


@bot.message_handler(commands=['products'])
def products_upload(message):
    if user_has_access.get(message.from_user.id):
        bot.send_message(message.chat.id, 'Please upload a CSV file with products',
                         bot.register_next_step_handler(message=message, callback=handle_csv_file, bot=bot,
                                                        upload_prefix='ProductTargets'))
    else:
        bot.send_message(message.chat.id, 'access denied! Please, enter access code',
                         bot.register_next_step_handler(message=message, callback=handle_access_code))


@bot.message_handler(commands=['download'])
def download(message):
    if user_has_access.get(message.from_user.id):
        # сделать метод и достать из базы все текущие сессии. А также подсчитать сколько всего записей в таблицах
        # product_targets, category_targets
        number_of_sessions = 10
        category_targets = 100
        product_targets = 10000
        bot.send_message(message.chat.id, f'In this menu you can get the results of the sessions.\n'
                                          f'We have currently completed:\n '
                                          f'{number_of_sessions} sessions \n'
                                          f'by {category_targets} categories \n'
                                          f'with {product_targets} products \n'
                                          f'You can get results by session number, product link, category link',
                         reply_markup=get_results_markup())
    else:
        bot.send_message(message.chat.id, 'access denied! Please, enter access code',
                         bot.register_next_step_handler(message=message, callback=handle_access_code))


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
        else:
            model = CategoryTargets

        csv_reader = CSVDatabase(file_path, model)
        reactor.callInThread(csv_reader.insert_from_csv)

        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.send_message(message.chat.id, f'Saved! {upload_prefix}')
    else:
        bot.reply_to(message.chat.id, "Please upload a CSV file.")


@bot.message_handler(commands=['category-link'])
def handle_category_link(message):
    if user_has_access.get(message.from_user.id):
        bot.send_message(message.chat.id, 'Please enter the category link:',
                         bot.register_next_step_handler(message=message, callback=export_category_results))
    else:
        bot.send_message(message.chat.id, 'Access denied! Please enter access code.',
                         bot.register_next_step_handler(message=message, callback=handle_access_code))


def export_category_results(message):
    category_url = message.text
    opts = Namespace(category=category_url)

    category_exporter = CategoryExporter()
    category_exporter.init()
    category_exporter.logger = logging.getLogger(name=CategoryExporter.__name__)
    category_exporter.settings = project_settings
    reactor.callInThread(category_exporter.execute, None, opts)

    bot.send_message(message.chat.id, 'Exporting category results...')


def start_bot():
    threading.Thread(target=bot.polling, kwargs={'none_stop': True}).start()
    reactor.run()


start_bot()
