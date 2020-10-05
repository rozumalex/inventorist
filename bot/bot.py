import telebot
from telebot import types

from settings import config
from db_handler import User, Chat, Category, Position, Transaction
from lexicon import commands, messages, separator


bot = telebot.TeleBot(config.bot.token)


def check_cancel(func):
    def wrapper(message):
        if message.text == commands.cancel:
            return process_cancel(message)
        else:
            return func(message)
    return wrapper


def process_cancel(message):
    Chat.reset(message)
    msg = messages.memory_cleared
    bot.send_message(message.chat.id, msg, reply_markup=get_markup(message))


def base_check(func):
    """Decorator checks if user and chat exists"""
    def wrapper(message):
        if not User.get(message):
            if not User.add(message):
                msg = messages.error_adding_user
                bot.send_message(message.chat.id, msg)

        if not Chat.get(message):
            msg = messages.creating_new_chat
            next_step = bot.send_message(message.chat.id, msg)
            return bot.register_next_step_handler(next_step, set_chat_name)

        return func(message)
    return wrapper


def set_chat_name(message):
    if Chat.add(message):
        msg = messages.new_chat_created
        markup = get_markup(message)
        bot.send_message(message.chat.id, msg, reply_markup=markup)
    else:
        msg = messages.try_again
        next_step = bot.send_message(message.chat.id, msg)
        bot.register_next_step_handler(next_step, set_chat_name)


def get_markup(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                       resize_keyboard=True)
    memory = Chat.get(message).memory.split(separator)
    if memory[0] == commands.none:
        for category in Category.get_all(message):
            markup.row(category)
    elif memory[0] == commands.report:
        if len(memory) == 1:
            for year in Transaction.get_years(message):
                markup.row(year)
        if len(memory) == 2:
            for month in Transaction.get_months(message):
                markup.row(month)
    elif memory[0] == commands.edit:
        markup.row(commands.categories)
        markup.row(commands.positions)
    elif len(memory) == 1:
        for position in Position.get_all_in_category(message):
            markup.row(position)
    if memory[0] != commands.none:
        markup.row(commands.cancel)
    else:
        markup.row(commands.report)
        markup.row(commands.edit)
    return markup


@check_cancel
def select_position(message):
    Chat.set(message)
    Position.add(message)
    msg = messages.input_value
    markup = get_markup(message)
    next_step = bot.send_message(message.chat.id, msg, reply_markup=markup)
    bot.register_next_step_handler(next_step, input_value)


@check_cancel
def select_year(message):
    Chat.set(message)
    msg = messages.select_month
    markup = get_markup(message)
    next_step = bot.send_message(message.chat.id, msg, reply_markup=markup)
    bot.register_next_step_handler(next_step, select_month)


@check_cancel
def select_month(message):
    Chat.set(message)
    msg = messages.report + Transaction.get_report(message)
    Chat.reset(message)
    bot.send_message(message.chat.id, msg, reply_markup=get_markup(message))


@check_cancel
def confirm_edit(message):
    Chat.set(message)
    memory = Chat.get(message).memory.split(separator)
    if memory[3] == commands.remove and memory[4] == commands.yes:
        try:
            if memory[1] == commands.categories:
                Category.remove(message)

            elif memory[1] == commands.positions:
                Position.remove(message)
        except Exception as e:
            print(e)
            msg = messages.error
        else:
            msg = messages.deleted
    elif memory[3] == commands.rename:
        try:
            if memory[1] == commands.categories:
                Category.set_name(message)
            elif memory[1] == commands.positions:
                Position.set_name(message)
        except Exception as e:
            print(e)
            msg = messages.error
        else:
            msg = messages.renamed
    else:
        msg = messages.error
    Chat.reset(message)
    markup = get_markup(message)
    bot.send_message(message.chat.id, msg, reply_markup=markup)


@check_cancel
def select_what_to_do(message):
    Chat.set(message)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                       resize_keyboard=True)
    if message.text == commands.rename or commands.remove:
        if message.text == commands.rename:
            msg = messages.enter_new_name
        else:
            msg = messages.confirm_delete
            markup.row(commands.yes)
        markup.row(commands.cancel)
        next_step = bot.send_message(message.chat.id, msg, reply_markup=markup)
        bot.register_next_step_handler(next_step, confirm_edit)
    else:
        msg = messsages.try_again
        next_step = bot.send_message(message.chat.id, msg, reply_markup=markup)
        bot.register_next_step_handler(next_step, select_what_to_do)


@check_cancel
def select_pos(message):
    Chat.set(message)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                       resize_keyboard=True)
    if message.text in Category.get_all(message)\
            or Position.get_all(message) or Transaction.get_all(message):
        msg = messages.select_edit
        markup.row(commands.rename)
        markup.row(commands.remove)
        markup.row(commands.cancel)
        next_step = bot.send_message(message.chat.id, msg, reply_markup=markup)
        bot.register_next_step_handler(next_step, select_what_to_do)
    else:
        msg = messages.try_again
        memory = Chat.get(message).memory.split(separator)
        if memory[1] == commands.categories:
            res = Category.get_all(message)
        else:
            res = Position.get_all(message)
        for pos in res:
            markup.row(pos)
        markup.row(commands.cancel)
        next_step = bot.send_message(message.chat.id, msg, reply_markup=markup)
        bot.register_next_step_handler(next_step, select_pos)


@check_cancel
def select_edit(message):
    Chat.set(message)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                       resize_keyboard=True)
    memory = Chat.get(message).memory.split(separator)
    if memory[1] == commands.categories:
        res = Category.get_all(message)
    else:
        res = Position.get_all(message)
    for pos in res:
        markup.row(pos)
    markup.row(commands.cancel)
    if message.text == commands.categories or commands.positions:
        if message.text == commands.categories:
            msg = messages.select_category_to_edit
        else:
            msg = messages.select_position_to_edit
        next_step = bot.send_message(message.chat.id, msg, reply_markup=markup)
        bot.register_next_step_handler(next_step, select_pos)
    else:
        msg = messages.try_again
        next_step = bot.send_message(message.chat.id, msg, reply_markup=markup)
        bot.register_next_step_handler(next_step, select_edit)


@check_cancel
def input_value(message):
    if not Transaction.add(message):
        msg = messages.try_again
        next_step = bot.send_message(message.chat.id, msg)
        bot.register_next_step_handler(next_step, input_value)
    else:
        Chat.reset(message)
        msg = messages.transaction_success
        bot.send_message(message.chat.id, msg,
                         reply_markup=get_markup(message))


@bot.message_handler(commands=['start'])
@base_check
def process_start(message):
    process_cancel(message)


@bot.message_handler(content_types=['text'])
@check_cancel
@base_check
def process_message(message):
    Chat.set(message)
    markup = get_markup(message)
    if message.text == commands.report:
        msg = messages.select_year
        next_step = bot.send_message(message.chat.id, msg, reply_markup=markup)
        bot.register_next_step_handler(next_step, select_year)
    elif message.text == commands.edit:
        msg = messages.select_edit
        next_step = bot.send_message(message.chat.id, msg, reply_markup=markup)
        bot.register_next_step_handler(next_step, select_edit)
    else:
        Category.add(message)
        msg = messages.select_position
        next_step = bot.send_message(message.chat.id, msg, reply_markup=markup)
        bot.register_next_step_handler(next_step, select_position)


if __name__ == '__main__':
    bot.polling(none_stop=True)
