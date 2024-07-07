import telebot
from db_handle import DBHandler
import os

token = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(token)
allowed = [175048449,1809947905]


@bot.message_handler(commands=['start'])
def start(message):
    """
    Запуск бота
    :param message: message (объект, передаваемый API Telegram)
    :return:
    """
    print(f"[LOG] 'start' function executed.")
    if message.from_user.id in allowed:
        bot.send_message(message.from_user.id, "Вы находитесь в списке пользователей бота и можете использовать его.")
    else:
        bot.send_message(message.from_user.id, "Доступ запрещен!")


@bot.message_handler(commands=['search'])
def search(message):
    """
    Поиск вакансий по запросу
    :param message: message (объект, передаваемый API Telegram)
    :return:
    """
    print(f"[LOG] 'search' function executed.")
    if message.from_user.id in allowed:
        arg = message.text
        key_val = " ".join(arg.split()[1:])
        db_access = DBHandler()
        res = db_access.search_vacs(key_val, message.from_user.id)
        print("[LOG] 'search' function executed. [keyval]: ", key_val)
        if len(res) == 0:
            bot.send_message(message.from_user.id, "Ошибка получения данных."
                                                   "Попробуйте позже или сообщите администратору.")
        else:
            msg_text = f'Вакансии по запросу "{key_val}":'
            for i in range(len(res)):
                msg_text += f"\n\n№ {i + 1}\n" \
                            f"Название: {res[i][0]}\n" \
                            f"Работодатель: {res[i][1]}\n" \
                            f"Ссылка: {res[i][3]}"
            bot.send_message(message.from_user.id, msg_text)
            print("[LOG] 'search' function send message to user. Vacancies found: ", len(res))
    else:
        print("[LOG] 'search' function executed with error")
        bot.send_message(message.from_user.id, "Доступ запрещен! Для использования бота обратитесь к администратору")


@bot.message_handler(commands=['last_searches'])
def last_searches(message):
    """
    Отображение последних поисковых запросов
    :param message: message (объект, передаваемый API Telegram)
    :return:
    """
    print(f"[LOG] 'last_searches' function executed.")
    if message.from_user.id in allowed:
        db_access = DBHandler()
        res = db_access.get_last_searches(message.from_user.id)
        if len(res) > 0:
            msg_text = 'Последние поисковые запросы'
            for i in range(len(res)):
                msg_text += f"\n\n{i + 1}) \"{res[i][0]}\""
            bot.send_message(message.from_user.id, msg_text)
        else:
            bot.send_message(message.from_user.id, "История поиска пуста")
    else:
        bot.send_message(message.from_user.id, "Доступ запрещен!")


@bot.message_handler(commands=['fav'])
def add_to_fav(message):
    """
    Добавление вакансий в избранное
    :param message: message (объект, передаваемый API Telegram)
    :return:
    """
    if message.from_user.id in allowed:
        print(f"[LOG] 'add_to_fav' function executed.")
        db_access = DBHandler()
        arg = message.text
        vac_ids = arg.split()[1:]
        if len(vac_ids) == 0:
            bot.send_message(message.from_user.id, "Необходимо указать вакансии!")
        res = db_access.add_vac_to_favs(vac_ids, message.from_user.id)
        print(f"[LOG] 'add_to_fav' function proceeding. [res] length (number of vacancies found: {len(res)}")
        if len(res) == 0:
            bot.send_message(message.from_user.id, "Ваканссии не добавлены в избранное. Возможно, указаны некорректные номера")
        else:
            msg_text = f'Следующие вакансии добавлены в избранное:\n'
            for i in range(len(res)):
                msg_text += f"\n\n№ {i + 1}\n" \
                            f"Название: {res[i][1]}\n" \
                            f"Работодатель: {res[i][2]}\n" \
                            f"Ссылка: {res[i][3]}"
            msg_text += "\n\nДля получения списка избранного используйте /favs"
            bot.send_message(message.from_user.id, msg_text)
            print("[LOG] 'add_to_fav' function send message to user")
    else:
        bot.send_message(message.from_user.id, "Доступ запрещен!")
    pass


@bot.message_handler(commands=['favs'])
def get_favs(message):
    """
    Отображение избранных вакансий
    :param message: message (объект, передаваемый API Telegram)
    :return:
    """
    print(f"[LOG] 'get_favs' function executed.")
    if message.from_user.id in allowed:
        db_access = DBHandler()
        res = db_access.get_favs(message.from_user.id)
        if len(res) > 0:
            msg_text = 'Избранные вакансии.\n' \
                       'ОБРАТИТЕ ВНИМАНИЕ: список формируется только за последние 24 часа.'
            for i in range(len(res)):
                msg_text += f"\n\n№ {i + 1}\n" \
                            f"Название: {res[i][0]}\n" \
                            f"Работодатель: {res[i][1]}\n" \
                            f"Ссылка: {res[i][2]}"
            bot.send_message(message.from_user.id, msg_text)
            print("[LOG] 'get_favs' function send message to user. Vacancies found: ", len(res))
        else:
            bot.send_message(message.from_user.id, "Список избранных вакансий пуст!")
    else:
        bot.send_message(message.from_user.id, "Доступ запрещен!")


@bot.message_handler(commands=['help'])
def help_message(message):
    """
    Вывод справки о командах
    :param message: message (объект, передаваемый API Telegram)
    :return:
    """
    print(f"[LOG] 'help_message' function executed.")
    if message.from_user.id in allowed:
        bot.send_message(message.from_user.id, "Список команд, доступных к использованию:\n"
                                               "/help - Вывод справки\n"
                                               "/last_searches - Последние поиски\n"
                                               "/search [строка для поиска] - Поиск вакансий по строке\n"
                                               "/fav [номер/номера вакансий] - Добавление в избранное вакансий из последней поисковой выдачи\n"
                                               "/favs - Отображение избранных вакансий")
    else:
        bot.send_message(message.from_user.id, "Доступ запрещен!")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.from_user.id in allowed:
        bot.send_message(message.from_user.id, "Команда не распознана. Используйте /help для вывода справки.")
    else:
        bot.send_message(message.from_user.id, "Доступ запрещен!")
