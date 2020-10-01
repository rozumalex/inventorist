import telebot
from telebot import types

from settings import config
from db_handler import User, Chat, Category, Position, Transaction
from lexicon import MESSAGES, COMMANDS


bot = telebot.TeleBot(config.bot.token)


def cancel_check(func):
    def wrapper(message):
        if message.text == COMMANDS['cancel']:
            return process_cancel(message)
        else:
            return func(message)
    return wrapper


def process_cancel(message):
    Chat.reset(message)
    msg = MESSAGES['memory_cleared']
    bot.send_message(message.chat.id, msg, reply_markup=get_markup(message))


def base_check(func):
    """Декоратор проверяет существование пользователя и чата."""
    def wrapper(message):
        if not User.get(message):
            if not User.add(message):
                msg = MESSAGES['error_adding_user']
                bot.send_message(message.chat.id, msg)

        if not Chat.get(message):
            msg = MESSAGES['creating_new_chat']
            next_step = bot.send_message(message.chat.id, msg)
            return bot.register_next_step_handler(next_step, set_name)

        return func(message)
    return wrapper


def set_name(message):
    if Chat.add(message):
        msg = MESSAGES['new_chat_created']
        markup = get_markup(message)
        bot.send_message(message.chat.id, msg, reply_markup=markup)
    else:
        msg = MESSAGES['try_again']
        next_step = bot.send_message(message.chat.id, msg)
        bot.register_next_step_handler(next_step, set_name)


def get_markup(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                       resize_keyboard=True)
    memory = Chat.get(message).memory.split(' > ')
    if memory[0] == 'None':
        for category in Category.get_all(message):
            markup.row(category)
    elif memory[0] == COMMANDS['report']:
        if len(memory) == 1:
            for year in Transaction.get_years(message):
                markup.row(year)
        if len(memory) == 2:
            for month in Transaction.get_months(message):
                markup.row(month)
    elif memory[0] == COMMANDS['edit']:
        markup.row('Категории')
        markup.row('Позиции')
    elif len(memory) == 1:
        for position in Position.get_all_in_category(message):
            markup.row(position)
    if memory[0] != 'None':
        markup.row(COMMANDS['cancel'])
    else:
        markup.row(COMMANDS['report'])
        markup.row(COMMANDS['edit'])
    return markup


@cancel_check
def select_position(message):
    Chat.set(message)
    Position.add(message)
    msg = MESSAGES['input_value']
    markup = get_markup(message)
    next_step = bot.send_message(message.chat.id, msg, reply_markup=markup)
    bot.register_next_step_handler(next_step, input_value)


@cancel_check
def select_year(message):
    Chat.set(message)
    msg = MESSAGES['select_month']
    markup = get_markup(message)
    next_step = bot.send_message(message.chat.id, msg, reply_markup=markup)
    bot.register_next_step_handler(next_step, select_month)


@cancel_check
def select_month(message):
    Chat.set(message)
    msg = MESSAGES['report'] + Transaction.get_report(message)
    Chat.reset(message)
    bot.send_message(message.chat.id, msg, reply_markup=get_markup(message))


@cancel_check
def confirm_edit(message):
    Chat.set(message)
    memory = Chat.get(message).memory.split(' > ')
    if memory[3] == 'Удалить' and memory[4] == 'Да':
        if memory[1] == 'Категории':
            Category.remove(message)
            Chat.reset(message)
            msg = 'Удалено'
            markup = get_markup(message)
            bot.send_message(message.chat.id, msg, reply_markup=markup)
        elif memory[1] == 'Позиции':
            Position.remove(message)
            Chat.reset(message)
            msg = 'Удалено'
            markup = get_markup(message)
            bot.send_message(message.chat.id, msg, reply_markup=markup)
        else:
            msg = 'Ошибка'
            Chat.reset(message)
            markup = get_markup(message)
            bot.send_message(message.chat.id, msg, reply_markup=markup)
    elif memory[3] == 'Переименовать':
        if memory[1] == 'Категории':
            Category.set_name(message)
            Chat.reset(message)
            msg = 'Переименовано.'
            markup = get_markup(message)
            bot.send_message(message.chat.id, msg, reply_markup=markup)
        elif memory[1] == 'Позиции':
            Position.set_name(message)
            Chat.reset(message)
            msg = 'Переименовано.'
            markup = get_markup(message)
            bot.send_message(message.chat.id, msg, reply_markup=markup)
        else:
            msg = 'Ошибка'
            Chat.reset(message)
            markup = get_markup(message)
            bot.send_message(message.chat.id, msg, reply_markup=markup)


@cancel_check
def select_what_to_do(message):
    Chat.set(message)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                       resize_keyboard=True)
    if message.text == 'Переименовать':
        msg = 'Введи новое название:'
        markup.row('Отмена')
        next_step = bot.send_message(message.chat.id, msg, reply_markup=markup)
        bot.register_next_step_handler(next_step, confirm_edit)
    elif message.text == 'Удалить':
        msg = 'Точно удалить?'
        markup.row('Да')
        markup.row('Отмена')
        next_step = bot.send_message(message.chat.id, msg, reply_markup=markup)
        bot.register_next_step_handler(next_step, confirm_edit)
    else:
        msg = MESSAGES['try_again']
        next_step = bot.send_message(message.chat.id, msg, reply_markup=markup)
        bot.register_next_step_handler(next_step, select_what_to_do)


@cancel_check
def select_pos(message):
    Chat.set(message)

    if message.text in Category.get_all(message)\
            or Position.get_all(message) or Transaction.get_all(message):
        msg = 'Выбери что сделать:'
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                           resize_keyboard=True)
        markup.row('Переименовать')
        markup.row('Удалить')
        markup.row('Отмена')
        next_step = bot.send_message(message.chat.id, msg, reply_markup=markup)
        bot.register_next_step_handler(next_step, select_what_to_do)
    else:
        msg = MESSAGES['try_again']
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                           resize_keyboard=True)
        memory = Chat.get(message).memory.split(' > ')
        if memory[1] == 'Категории':
            res = Category.get_all(message)
        elif memory[1] == 'Позиции':
            res = Position.get_all(message)
        for pos in res:
            markup.row(pos)
        markup.row(COMMANDS['cancel'])
        next_step = bot.send_message(message.chat.id, msg,
                                     reply_markup=markup)
        bot.register_next_step_handler(next_step, select_pos)


@cancel_check
def select_edit(message):
    Chat.set(message)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                       resize_keyboard=True)
    memory = Chat.get(message).memory.split(' > ')
    if memory[1] == 'Категории':
        res = Category.get_all(message)
    elif memory[1] == 'Позиции':
        res = Position.get_all(message)
    for pos in res:
        markup.row(pos)
    markup.row(COMMANDS['cancel'])
    if message.text == 'Категории':
        msg = 'Выбери категорию:'
        next_step = bot.send_message(message.chat.id, msg, reply_markup=markup)
        bot.register_next_step_handler(next_step, select_pos)
    elif message.text == 'Позиции':
        msg = 'Выбери позицию:'
        next_step = bot.send_message(message.chat.id, msg, reply_markup=markup)
        bot.register_next_step_handler(next_step, select_pos)
    elif message.text == 'Записи':
        msg = 'Выбери запись:'
        next_step = bot.send_message(message.chat.id, msg, reply_markup=markup)
        bot.register_next_step_handler(next_step, select_pos)
    else:
        msg = MESSAGES['try_again']
        next_step = bot.send_message(message.chat.id, msg, reply_markup=markup)
        bot.register_next_step_handler(next_step, select_edit)


@cancel_check
def input_value(message):
    if not Transaction.add(message):
        msg = MESSAGES['try_again']
        next_step = bot.send_message(message.chat.id, msg)
        bot.register_next_step_handler(next_step, input_value)
    else:
        Chat.reset(message)
        msg = MESSAGES['transaction_success']
        bot.send_message(message.chat.id, msg,
                         reply_markup=get_markup(message))


@bot.message_handler(commands=['start'])
@base_check
def process_start(message):
    process_cancel(message)


@bot.message_handler(content_types=['text'])
@cancel_check
@base_check
def process_message(message):
    Chat.set(message)
    if message.text == COMMANDS['report']:
        msg = MESSAGES['select_year']
        markup = get_markup(message)
        next_step = bot.send_message(message.chat.id, msg, reply_markup=markup)
        bot.register_next_step_handler(next_step, select_year)
    elif message.text == COMMANDS['edit']:
        msg = MESSAGES['select_edit']
        markup = get_markup(message)
        next_step = bot.send_message(message.chat.id, msg, reply_markup=markup)
        bot.register_next_step_handler(next_step, select_edit)
    else:
        Category.add(message)
        msg = MESSAGES['select_position']
        markup = get_markup(message)
        next_step = bot.send_message(message.chat.id, msg, reply_markup=markup)
        bot.register_next_step_handler(next_step, select_position)


if __name__ == '__main__':
    bot.polling(none_stop=True)
