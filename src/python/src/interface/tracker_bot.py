import telebot
from telebot import types
from scrapy.utils.project import get_project_settings
from src.python.src.interface.menues import *


project_settings = get_project_settings()
bot = telebot.TeleBot(project_settings.get("BOT_TOKEN"))
access_code = project_settings.get("ACCESS_CODE")

users_entered_codes = {}  # Словарь для хранения введенных пользователем кодов


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'You pressed start', reply_markup=main_menu())


@bot.message_handler(commands=['help'])
def start_message(message):
    bot.send_message(message.chat.id, 'You pressed start', reply_markup=back_menu())


@bot.message_handler(commands=['back'])
def back_handler(message):
    bot.send_message(message.chat.id, 'Back to main menu', reply_markup=main_menu())


@bot.message_handler(commands=['enter_code'])
def enter_access_code(message):
    bot.send_message(message.chat.id, 'please, enter your access code',
                     bot.register_next_step_handler(message=message,
                                                    callback=handle_access_code))


def handle_access_code(message):
    if message:
        if message.text == access_code:
            bot.send_message(message.chat.id, f"your code accepted, {message.text}")

        else:
            bot.send_message(message.chat.id, "Incorrect code!")


bot.polling(none_stop=True)
