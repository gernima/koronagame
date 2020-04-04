import telebot
import time
from telebot import types
from threading import Thread
import pymorphy2
import sqlite3

bot = telebot.TeleBot('1077053623:AAE8yg9jrRas7h7mTgKaNQAjOTeIsgwJHGI')
print('start')
return_family_menu = telebot.types.InlineKeyboardMarkup()
return_family_menu.add(telebot.types.InlineKeyboardButton(text='Назад', callback_data='bunker_family_return'))

a = {0: {'inventory': [], 'name': 'a', 'mom': 1, 'dad': 1, 'brother': 1, 'sister': 1, 'day': 1,
         'dad_bd': {'mood': 50, 'hungry': 50, 'water': 50, 'immunity': 50, 'emoji': '😕'},
         'mother_bd': {'mood': 50, 'hungry': 50, 'water': 50, 'immunity': 50, 'emoji': '😌'},
         'brother_bd': {'mood': 50, 'hungry': 50, 'water': 50, 'immunity': 50, 'emoji': '🤨'},
         'sister_bd': {'mood': 50, 'hungry': 50, 'water': 50, 'immunity': 50, 'emoji': '😔'}}}
con = sqlite3.connect("bd.db", check_same_thread=False)
cur = con.cursor()


def bd_family(chat_id, data):
    x = 0
    for i in a[chat_id]['dad_bd'].keys():
        a[chat_id][i] = data[x]
        x += 1


def get_data_from_bd(chat_id):
    try:
        if chat_id not in a.keys():
            a[chat_id] = a[0]
        q = """Select {} from {} where chat_id == {}"""
        bd_family(chat_id, list(cur.execute(q.format('*', 'dad', chat_id)).fetchone()[1:]))
        bd_family(chat_id, list(cur.execute(q.format('*', 'mother', chat_id)).fetchone()[1:]))
        bd_family(chat_id, list(cur.execute(q.format('*', 'brother', chat_id)).fetchone()[1:]))
        bd_family(chat_id, list(cur.execute(q.format('*', 'sister', chat_id)).fetchone()[1:]))

        a[chat_id]['inventory'] = str(cur.execute(q.format('inventory', 'saves', chat_id)).fetchone()[0]).split(';')
        a[chat_id]['name'] = cur.execute(q.format('name', 'saves', chat_id)).fetchone()[0]
        a[chat_id]['mom'] = cur.execute(q.format('mom', 'saves', chat_id)).fetchone()[0]
        a[chat_id]['dad'] = cur.execute(q.format('dad', 'saves', chat_id)).fetchone()[0]
        a[chat_id]['brother'] = cur.execute(q.format('brother', 'saves', chat_id)).fetchone()[0]
        a[chat_id]['sister'] = cur.execute(q.format('sister', 'saves', chat_id)).fetchone()[0]
        a[chat_id]['day'] = cur.execute(q.format('day', 'saves', chat_id)).fetchone()[0]
    except:
        pass


def get_bunker_keyboard(chat_id):
    get_data_from_bd(chat_id)
    bunker = telebot.types.InlineKeyboardMarkup(row_width=5)
    butts = []
    if a[chat_id]['dad']:
        butts.append(telebot.types.InlineKeyboardButton(text=f'Папа {a[chat_id]["dad_bd"]["emoji"]}',
                                                  callback_data='bunker_family_dad'))
    if a[chat_id]['mom']:
        butts.append(telebot.types.InlineKeyboardButton(text=f'Мама {a[chat_id]["mother_bd"]["emoji"]}',
                                                  callback_data='bunker_family_mother'))
    if a[chat_id]['brother']:
        butts.append(telebot.types.InlineKeyboardButton(text=f'Брат {a[chat_id]["brother_bd"]["emoji"]}',
                                                  callback_data='bunker_family_brother'))
    if a[chat_id]['brother']:
        butts.append(telebot.types.InlineKeyboardButton(text=f'Сестра {a[chat_id]["sister_bd"]["emoji"]}',
                                                  callback_data='bunker_family_sister'))
    bunker.add(*butts)
    bunker.add(telebot.types.InlineKeyboardButton(text='Журнал', callback_data='bunker_journal'),
               telebot.types.InlineKeyboardButton(text='Следующий день', callback_data='bunker_next_day'))
    bunker.add(telebot.types.InlineKeyboardButton(text='Выход в пустошь', callback_data='bunker_wasteland'))

    return bunker


def create_family_bd(chat_id):
    if cur.execute("""Select chat_id from dad where chat_id == {}""".format(chat_id)).fetchone():
        cur.execute(
            """UPDATE dad SET chat_id = ?, mood = ?, hungry = ?, water = ? immunity = ? emoji = ? WHERE chat_id == ?""",
            (chat_id, a[chat_id]['dad_bd']['mood'], a[chat_id]['dad_bd']['hungry'], a[chat_id]['dad_bd']['water'],
             a[chat_id]['dad_bd']['immunity'], a[chat_id]['dad_bd']['emoji'],
             chat_id))
        cur.execute(
            """UPDATE mother SET chat_id = ?, mood = ?, hungry = ?, water = ? immunity = ? emoji = ? WHERE chat_id == ?""",
            (chat_id, a[chat_id]['mother_bd']['mood'], a[chat_id]['mother_bd']['hungry'],
             a[chat_id]['mother_bd']['immunity'], a[chat_id]['mother_bd']['emoji'],
             a[chat_id]['mother_bd']['water']))
        cur.execute(
            """UPDATE brother SET chat_id = ?, mood = ?, hungry = ?, water = ? immunity = ? emoji = ? WHERE chat_id == ?""",
            (chat_id, a[chat_id]['brother_bd']['mood'], a[chat_id]['brother_bd']['hungry'],
             a[chat_id]['brother_bd']['immunity'], a[chat_id]['brother_bd']['emoji'],
             a[chat_id]['brother_bd']['water']))
        cur.execute(
            """UPDATE sister SET chat_id = ?, mood = ?, hungry = ?, water = ? immunity = ? emoji = ? WHERE chat_id == ?""",
            (chat_id, a[chat_id]['sister_bd']['mood'], a[chat_id]['sister_bd']['hungry'],
             a[chat_id]['sister_bd']['immunity'], a[chat_id]['sister_bd']['emoji'],
             a[chat_id]['sister_bd']['water']))
    else:
        cur.execute("""INSERT INTO dad VALUES (?, ?, ?, ?, ?, ?)""",
                    (chat_id, a[chat_id]['dad_bd']['mood'], a[chat_id]['dad_bd']['hungry'],
                     a[chat_id]['dad_bd']['water'], a[chat_id]['dad_bd']['immunity'], a[chat_id]['dad_bd']['emoji']))
        cur.execute("""INSERT INTO mother VALUES (?, ?, ?, ?, ?, ?)""",
                    (chat_id, a[chat_id]['mother_bd']['mood'], a[chat_id]['mother_bd']['hungry'],
                     a[chat_id]['mother_bd']['water'], a[chat_id]['mother_bd']['immunity'],
                     a[chat_id]['mother_bd']['emoji']))
        cur.execute("""INSERT INTO brother VALUES (?, ?, ?, ?, ?, ?)""",
                    (chat_id, a[chat_id]['brother_bd']['mood'], a[chat_id]['brother_bd']['hungry'],
                     a[chat_id]['brother_bd']['water'], a[chat_id]['brother_bd']['immunity'],
                     a[chat_id]['brother_bd']['emoji']))
        cur.execute("""INSERT INTO sister VALUES (?, ?, ?, ?, ?, ?)""",
                    (chat_id, a[chat_id]['sister_bd']['mood'], a[chat_id]['sister_bd']['hungry'],
                     a[chat_id]['sister_bd']['water'], a[chat_id]['sister_bd']['immunity'],
                     a[chat_id]['sister_bd']['emoji']))
    con.commit()


def edit_message_for_family(call):
    who_bd = call.data[len('bunker_family_'):] + '_bd'
    who = ''
    if call.data[len('bunker_family_'):] == 'dad':
        who = 'Папа'
    elif call.data[len('bunker_family_'):] == 'mother':
        who = 'Мама'
    elif call.data[len('bunker_family_'):] == 'sister':
        who = 'Сестра'
    elif call.data[len('bunker_family_'):] == 'brother':
        who = 'Брат'
    bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                          text=f'{who} {a[call.from_user.id][who_bd]["emoji"]}'
                               f'\nНастроение: {a[call.from_user.id][who_bd]["mood"]}'
                               f'\nСытость: {a[call.from_user.id][who_bd]["hungry"]}'
                               f'\nЖажда: {a[call.from_user.id][who_bd]["water"]}'
                               f'\nИммунитет: {a[call.from_user.id][who_bd]["immunity"]}',
                          reply_markup=return_family_menu)


@bot.callback_query_handler(func=lambda call: 'bunker' in call.data)
def bunker_logic(call):
    get_data_from_bd(call.from_user.id)
    if call.data == 'bunker_family_dad':
        edit_message_for_family(call)
    elif call.data == 'bunker_family_mother':
        edit_message_for_family(call)
    elif call.data == 'bunker_family_sister':
        edit_message_for_family(call)
    elif call.data == 'bunker_family_brother':
        edit_message_for_family(call)
    elif call.data == 'bunker_family_return':
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                              text=f'Локация: Бункер\nДень {a[call.from_user.id]["day"]}',
                              reply_markup=get_bunker_keyboard(call.from_user.id))
    elif call.data == 'bunker_next_day':
        try:
            a[call.from_user.id]['day'] += 1
            save_update_to_bd(call.from_user.id)
            bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                  text=f'Локация: Бункер\nДень {a[call.from_user.id]["day"]}',
                                  reply_markup=get_bunker_keyboard(call.from_user.id))
        except:
            pass


def save_update_to_bd(chat_id, inv=None):
    x = cur.execute("""Select chat_id from saves where chat_id == ?""", (chat_id,)).fetchone()
    if x:
        if inv:
            a[chat_id]['inventory'] = inv[a[chat_id]['name']]
        inventory = ';'.join(a[chat_id]['inventory'])
        cur.execute(
            """UPDATE saves SET chat_id = ?, inventory = ?, name = ?, mom = ?, dad = ?, brother = ?, sister = ?, day = ? WHERE chat_id == ?""",
            (chat_id, inventory, a[chat_id]['name'], a[chat_id]['mom'], a[chat_id]['dad'],
             a[chat_id]['brother'], a[chat_id]['sister'], a[chat_id]['day'], chat_id))
    else:
        a[chat_id] = a[0]
        if inv:
            a[chat_id]['inventory'] = inv[a[chat_id]['name']]
        inventory = ';'.join(a[chat_id]['inventory'])
        cur.execute("""INSERT INTO saves VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (chat_id, inventory, a[chat_id]['name'], a[chat_id]['mom'], a[chat_id]['dad'],
                     a[chat_id]['brother'], a[chat_id]['sister'], a[chat_id]['day']))
        create_family_bd(chat_id)
    con.commit()


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
    save_update_to_bd(call.from_user.id, package)


def bunker(message):
    get_data_from_bd(message.chat.id)
    bot.send_message(message.chat.id, f'Локация: Бункер\nДень {a[message.chat.id]["day"]}',
                     reply_markup=get_bunker_keyboard(message.chat.id))


time_list = {}
user_list = []
weight_list = {}
morph = pymorphy2.MorphAnalyzer().parse
FOOD = {'vodka': ('водка', 1), 'mask': ('маска', 3), 'medicinechest': ('аптечка', 3), 'soap': ('мыло', 3), 'sausage': ('колбаса', 3)}
package = {}



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
        if message.chat.id not in a.keys():
            a[message.chat.id] = a[0]
        a[message.chat.id]['name'] = name.strip()
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
            markup.add(types.InlineKeyboardButton(text='Спрятаться', callback_data='play_start'),
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

