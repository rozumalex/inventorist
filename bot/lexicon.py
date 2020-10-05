from dotmap import DotMap


COMMANDS = {
    'cancel': 'Отмена',
    'report': 'Отчет',
    'edit': 'Правка',
    'none': 'None',
    'categories': 'Категории',
    'positions': 'Позиции',
    'remove': 'Удалить',
    'rename': 'Переименовать',
    'yes': 'Да',
}

MESSAGES = {
    'error_adding_user': 'Ошибка добавления пользователя.',
    'creating_new_chat': 'Привет!\n'
                         'Можно начинать работу.\n'
                         'Пришли мне название бара.',
    'new_chat_created': 'Дальше все просто.\n'
                        'Создай свою первую категорию, например "Вино".\n',
    'try_again': 'Попробуй еще раз.',
    'memory_cleared': 'Отмена.',
    'select_position': 'Выбери или добавь новую позицию:',
    'select_year': 'Выбери год:',
    'select_month': 'Выбери месяц:',
    'error': 'Ошибочка.',
    'input_value': 'Введи остаток:',
    'transaction_success': 'Посчитано!',
    'report': 'Отчет:',
    'select_edit': 'Выбери что нужно сделать:',
    'deleted': 'Удалено.',
    'renamed': 'Переименовано',
    'enter_new_name': 'Введи новое название:',
    'confirm_delete': 'Точно удалить?',
    'select_position_to_edit': 'Выбери позицию:',
    'select_category_to_edit': 'Выбери категорию:'

}

separator = ' > '

commands = DotMap(COMMANDS)
messages = DotMap(MESSAGES)
