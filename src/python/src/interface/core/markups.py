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


def new_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_back = types.KeyboardButton(text='Back')
    markup.add(button_back)
    return markup


def start_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_help = types.KeyboardButton(text='/help')
    button_enter_code = types.KeyboardButton(text='/enter_code')
    markup.add(button_help, button_enter_code)
    return markup


def back_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back = types.KeyboardButton(text='/back')
    markup.add(back)
    return markup


def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    upload_button = types.KeyboardButton(text='/upload')
    download_button = types.KeyboardButton(text='/download')
    tracking_button = types.KeyboardButton(text='/tracker')
    back = types.KeyboardButton(text='/back')
    markup.add(upload_button, download_button,tracking_button, back)
    return markup


def upload_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    category_button = types.KeyboardButton(text='/categories')
    product_button = types.KeyboardButton(text='/products')
    back = types.KeyboardButton(text='/main_menu')
    markup.add(category_button, product_button, back)
    return markup


def get_results_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    get_result_by_session_button = types.KeyboardButton(text='/session_id')
    get_result_by_product_button = types.KeyboardButton(text='/product_link')
    get_result_by_category_button = types.KeyboardButton(text='/category_link')
    back = types.KeyboardButton(text='/main_menu')
    markup.add(get_result_by_category_button, get_result_by_product_button, get_result_by_session_button, back)
    return markup


def tracker_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_tracking = types.KeyboardButton(text='start_tracking')
    stop_tracking = types.KeyboardButton(text='stop_tracking')
    back = types.KeyboardButton(text='/download')
    markup.add(start_tracking, stop_tracking, back)
    return markup
