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


def new_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_back = types.KeyboardButton(text='Back')
    markup.add(button_back)
    return markup


def start_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_help = types.KeyboardButton(text='/help')
    button_enter_code = types.KeyboardButton(text='/enter_code')
    markup.add(button_help, button_enter_code)
    return markup


def back_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back = types.KeyboardButton(text='/back')
    markup.add(back)
    return markup


def csv_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    upload_button = types.KeyboardButton(text='/upload')
    back = types.KeyboardButton(text='/back')
    markup.add(upload_button, back)
    return markup


def upload_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    category_button = types.KeyboardButton(text='/categories')
    product_button = types.KeyboardButton(text='/products')
    back = types.KeyboardButton(text='/back')
    markup.add(category_button, product_button, back)
    return markup
