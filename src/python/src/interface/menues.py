import telebot
from telebot import types


# def start_menu():
#     markup = types.InlineKeyboardMarkup()
#     button_start = types.InlineKeyboardButton(text='Start', callback_data='start')
#     markup.add(button_start)
#     return markup
#
#
# def new_menu():
#     markup = types.InlineKeyboardMarkup()
#     button_back = types.InlineKeyboardButton(text='Back', callback_data='start')
#     markup.add(button_back)
#     return markup
#
#
# def main_menu():
#     markup = types.InlineKeyboardMarkup()
#     button_help = types.InlineKeyboardButton(text='help', callback_data='help')
#     button_enter_code = types.InlineKeyboardButton(text='enter_code', callback_data='enter_code')
#     markup.add(button_help, button_enter_code)
#     return markup

def start_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_start = types.KeyboardButton(text='Start')
    markup.add(button_start)
    return markup


def new_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_back = types.KeyboardButton(text='Back')
    markup.add(button_back)
    return markup


def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_help = types.KeyboardButton(text='/help')
    button_enter_code = types.KeyboardButton(text='/enter_code')
    markup.add(button_help, button_enter_code)
    return markup


def back_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_back = types.KeyboardButton(text='/back')
    markup.add(button_back)
    return markup
