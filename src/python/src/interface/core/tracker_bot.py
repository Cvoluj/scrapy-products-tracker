from scrapy.utils.project import get_project_settings
from menues import *


project_settings = get_project_settings()
bot = telebot.TeleBot(project_settings.get("BOT_TOKEN"))
access_code = project_settings.get("ACCESS_CODE")
is_user_access = {}


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'You pressed start', reply_markup=start_menu())


@bot.message_handler(commands=['help'])
def start_message(message):
    bot.send_message(message.chat.id, f'Hello, {message.from_user.username}!\n'
                                      'This bot is created for interaction with a product tracker. '
                                      'To start working, you need to enter a code to access all functions, '
                                      'namely:'
                                      '\n\n 1. Ability to upload a file.csv with the links of products '
                                      'or categories you are interested in for tracking.'
                                      '\n\n 2. Ability to get tracking results by session number, category link,'
                                      ' or product link.',
                     reply_markup=back_menu())


@bot.message_handler(commands=['back'])
def back_handler(message):
    bot.send_message(message.chat.id, 'Back to main menu', reply_markup=start_menu())


@bot.message_handler(commands=['enter_code'])
def enter_access_code(message):
    bot.send_message(message.chat.id, 'please, enter your access code',
                     bot.register_next_step_handler(message=message,
                                                    callback=handle_access_code))


@bot.message_handler(commands=['upload'])
def handle_upload(message):
    if message.from_user.id in is_user_access.keys():
        bot.send_message(message.chat.id, 'Please, choose the type of uploaded links!\n'
                                          'The file must be .csv format!', reply_markup=upload_menu())
    else:
        bot.send_message(message.chat.id, 'access denied! Please, enter access code',
                         bot.register_next_step_handler(message=message, callback=handle_access_code))


@bot.message_handler(commands=['categories'])
def handle_categories_file_upload(message):
    bot.send_message(message.chat.id, 'Please upload a CSV file with categories',
                     bot.register_next_step_handler(message=message, callback=handle_csv_file,
                                                    upload_prefix='CategoryTargets'))


@bot.message_handler(commands=['products'])
def handle_products_file_upload(message):
    bot.send_message(message.chat.id, 'Please upload a CSV file with products',
                     bot.register_next_step_handler(message=message, callback=handle_csv_file,
                                                    upload_prefix='ProductTargets'))


def handle_access_code(message):
    if message:
        if message.text == access_code:
            is_user_access[message.from_user.id] = True
            bot.send_message(message.chat.id, f"Your code accepted, {message.from_user.username}",
                             reply_markup=csv_menu())

        else:
            bot.send_message(message.chat.id, "Incorrect code!")


def handle_csv_file(message, upload_prefix):
    if message.document.mime_type == 'text/csv':
        # Download the CSV file
        file_info = bot.get_file(message.document.file_id)
        # downloaded_file = bot.download_file(file_info.file_path)
        # Save the CSV file
        # file_path = f'uploads/{message.document.file_name}'
        # with open(file_path, 'wb') as new_file:
        #     new_file.write(downloaded_file)
        bot.send_message(message.chat.id, f'Saved!{upload_prefix}')
    else:
        bot.reply_to(message.chat.id, "Please upload a CSV file.")


bot.polling(none_stop=True)
