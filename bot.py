import telebot
import time
from telebot import types
from threading import Thread
import pymorphy2
import sqlite3

bot = telebot.TeleBot('1077053623:AAE8yg9jrRas7h7mTgKaNQAjOTeIsgwJHGI')
print('start')

a = {1: {'chat_id': 0, 'inventory': [], 'name': 'a', 'mom': True, 'dad': False, 'brother': True, 'sister': False,
         'immunity': 5}}


def save_and_update(chat_id, a):
    con = sqlite3.connect("bd.db")
    cur = con.cursor()
    a['inventory'] = ' '.join(a['inventory'])
    a = list(a[chat_id].values())
    if cur.execute("""Select chat_id from saves where chat_id == {}""".format(a[0])).fetchone():
        cur.execute(
            """UPDATE saves SET chat_id = ?, inventory = ?, name = ?, mom = ?, dad = ?, brother = ?, sister = ?, immunity = ? WHERE chat_id == ?""",
            (a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[0]))
    else:
        cur.execute("""INSERT INTO saves VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7]))
    con.commit()
    con.close()


def items():
    murkup = types.InlineKeyboardMarkup(row_width=2)
    item_1 = types.InlineKeyboardButton(text='', callback_data='item_')
    murkup.add(
        types.InlineKeyboardButton(text='водка - 1', callback_data='item_vodka'),
        types.InlineKeyboardButton(text='колбаса - 3', callback_data='item_sausage'),
        types.InlineKeyboardButton(text='аптечка - 3', callback_data='item_medicinechest'),
        types.InlineKeyboardButton(text='мыло - 3', callback_data='item_soap'),
        types.InlineKeyboardButton(text='маска - 3', callback_data='item_mask')
    )
    return murkup


def time_(call, user):
    second = 60
    sms = bot.send_message(call.message.chat.id, 'У тебя осталось {} {} и {} места'.format(
            second, morph('секунда')[0].make_agree_with_number(second).word, weight_list[user]), reply_markup=items())
    while second > 0:
        time.sleep(1)
        second -= 1
        bot.edit_message_text(chat_id=sms.chat.id, message_id=sms.message_id,
            text='У тебя осталось {} {}  и {} места'.format(
                second, morph('секунда')[0].make_agree_with_number(second).word, weight_list[user]), reply_markup=items())
        if weight_list[user] == 0 or second == 0:
            bot.send_message(call.message.chat.id, 'Вот что вы взяли с собой:\n' + '\n'.join(
                '{}. {}'.format(i + 1, item) for i, item in enumerate(package.get(user, ['Пусто']))))
            bot.edit_message_text(chat_id=sms.chat.id, message_id=sms.message_id, text='Время закончилось' if second == 0 else 'Место закончилось')
            markup = types.ReplyKeyboardMarkup(True)
            markup.add(
                types.InlineKeyboardButton('Донат'),
                types.InlineKeyboardButton('Поддержка'),
                types.InlineKeyboardButton('Помощь новичкам')
            )
            bot.send_message(call.message.chat.id, 'Пора в бункер', reply_markup=markup)
            bunker(call.message)
            print('сумка ', package[user])
            return
    #  save BD package


def bunker(message):
    bot.send_message(message.chat.id, 'Локация: Бункер', reply_markup=bunker1)


morph = pymorphy2.MorphAnalyzer().parse
FOOD = {'vodka': ('водка', 1), 'mask': ('маска', 3), 'medicinechest': ('аптечка', 3), 'soap': ('мыло', 3), 'sausage': ('колбаса', 3)}
package = {}
user_list = []
weight_list = {}
time_list = {}
bunker1 = telebot.types.InlineKeyboardMarkup(row_width=5)
bunker1.add(telebot.types.InlineKeyboardButton(text='Папа', callback_data='bunker_dad'),
            telebot.types.InlineKeyboardButton(text='Мама', callback_data='bunker_mother'),
            telebot.types.InlineKeyboardButton(text='Брат', callback_data='bunker_brother'),
            telebot.types.InlineKeyboardButton(text='Сестра', callback_data='bunker_sister'))
bunker1.add(telebot.types.InlineKeyboardButton(text='Выход в пустошь', callback_data='bunker_wasteland'))
bunker1.add(telebot.types.InlineKeyboardButton(text='Журнал', callback_data='bunker_journal'))


@bot.message_handler(commands=['start', 'new_game'])
def start_message(message):
    if message.text == '/start':
        laste_name = message.from_user.last_name
        if not laste_name:
            laste_name = ''
        name = message.from_user.first_name + ' ' + laste_name
        murkup = types.InlineKeyboardMarkup(row_width=2)
        item_1 = types.InlineKeyboardButton('Да', callback_data='play_yes')
        item_2 = types.InlineKeyboardButton('Нет', callback_data='play_no')
        murkup.add(item_1, item_2)
        bot.send_message(message.chat.id, '{}, ты выжил?\nРешишься сыграть в игру?'.format(name), reply_markup=murkup)
        user_list.append(message.from_user.username)
        print("Список пользователей", user_list)
    elif message.text == '/new_game':
        murkup = types.InlineKeyboardMarkup(row_width=2)
        item_1 = types.InlineKeyboardButton('Да', callback_data='play_start')
        item_2 = types.InlineKeyboardButton('Нет', callback_data='play_continue')
        murkup.add(item_1, item_2)
        bot.send_message(message.chat.id, 'Ты точно хочешь начать все с начала?', reply_markup=murkup)


@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == '1':
        bunker(message)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    global weight_list
    user = call.from_user.username
    name = call.data
    name_type = name.split('_')[0]
    if name_type == 'play':
        type = name.split('_')[1]
        try:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        except Exception as e:
            print(e, call.message.chat.id, call.message.message_id)
        if type == 'yes':
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text='Спяртаться', callback_data='play_start'),
                       types.InlineKeyboardButton(text='Сдаться', callback_data='play_end'))
            bot.send_message(call.message.chat.id, 'Приготовься выживать в новом мире, которому грозит пандемия, вы решаетесь спрятаться в бункере, у тебя есть 60 секунд чтобы собрать все вещи до того как приедет полиция из-за подозрений на заражение', reply_markup=markup)
        elif type == 'no':
            murkup = types.InlineKeyboardMarkup(row_width=2)
            item_1 = types.InlineKeyboardButton('Да', callback_data='play_yes')
            item_2 = types.InlineKeyboardButton('Нет', callback_data='play_no')
            murkup.add(item_1, item_2)
            bot.send_message(call.message.chat.id, 'Сыканул, может все таки сыграешь?',
                             reply_markup=murkup)
        elif type == 'start':
            print('Счетчик: ' + call.from_user.username)
            weight_list[user] = 20
            thread1 = Thread(target=time_, args=(call, user))
            thread1.start()
            time_list[call.from_user.username] = thread1
        elif type == 'end':
            bot.send_message(call.message.chat.id, 'Справедливо, но из-за этого вы уже реально заразились в общей больнице, а ведь могли рискнуть и выжить')
        elif type == 'continue':
            pass
    elif name_type == 'item':
        item = name.split('_')[1]
        if weight_list[user] != 0:
            if weight_list[user] - FOOD[item][1] < 0:
                bot.answer_callback_query(callback_query_id=call.id, text='Недостаточно места')
            else:
                package[call.from_user.username] = package.get(call.from_user.username, []) + [FOOD[item][0]]
                weight_list[user] -= FOOD[item][1]
                bot.answer_callback_query(callback_query_id=call.id, text='Мы положили в сумку: {}'.format(morph(FOOD[item][0])[0].inflect({'accs'}).word))


try:
    bot.polling()
except Exception as e:
    bot.polling()
    print(e)