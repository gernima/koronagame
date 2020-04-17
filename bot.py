import telebot
import time
from telebot import types
from threading import Thread
import pymorphy2
import sqlite3
from random import choice, sample

bot = telebot.TeleBot('1049041175:AAFHw6FXE2-yCv7L4sJmwg50eImuAusJOG0')
print('start')

a = {0: {'inventory': [], 'name': 'a', 'mother': 1, 'dad': 1, 'brother': 1, 'sister': 1, 'day': 1,
         'dad_bd': {'hp': 50, 'hungry': 50, 'water': 50, 'immunity': 50, 'emoji': '😕'},
         'mother_bd': {'hp': 50, 'hungry': 50, 'water': 50, 'immunity': 50, 'emoji': '😌'},
         'brother_bd': {'hp': 50, 'hungry': 50, 'water': 50, 'immunity': 50, 'emoji': '🤨'},
         'sister_bd': {'hp': 50, 'hungry': 50, 'water': 50, 'immunity': 50, 'emoji': '😔'}}}
con = sqlite3.connect("bd.db", check_same_thread=False)
cur = con.cursor()


@bot.callback_query_handler(func=lambda call: 'bunker' in call.data and 'wasteland_return' not in call.data)
def bunker_logic(call):
    if call.data == 'bunker_family_dad':
        edit_message_for_family(call)
    elif call.data == 'bunker_family_mother':
        edit_message_for_family(call)
    elif call.data == 'bunker_family_sister':
        edit_message_for_family(call)
    elif call.data == 'bunker_family_brother':
        edit_message_for_family(call)
    elif call.data == 'bunker_wasteland':
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                              text='Люди в пустоши:',
                              reply_markup=get_wasteland_mans_keyboard(call.from_user.id))
    elif call.data == 'bunker_inventory':
        inv_items = "\n".join(a[call.from_user.id]["inventory"])
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                              text=f'Ваши вещи:\n {inv_items}',
                              reply_markup=get_bunker_keyboard(call.from_user.id))
    elif call.data == 'bunker_family_return':
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                              text=f'Локация: Бункер\nДень {a[call.from_user.id]["day"]}',
                              reply_markup=get_bunker_keyboard(call.from_user.id))
    elif call.data == 'bunker_next_day':
        # try:
        add_wasteland_event(2, call.from_user.id)
        a[call.from_user.id]['day'] += 1
        save_update_to_bd(call.from_user.id)
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                              text=f'Локация: Бункер\nДень {a[call.from_user.id]["day"]}',
                              reply_markup=get_bunker_keyboard(call.from_user.id))
        # except Exception as e:
        #     print(call.data, '|', e)
    elif call.data == 'bunker_journal':
        pass


@bot.callback_query_handler(func=lambda call: 'wasteland' in call.data)
def wasteland_logic(call):
    if 'go' in call.data:
        who = call.data.split('_')[1]
        a[call.from_user.id][who] = 0
        cur.execute("""INSERT INTO wasteland VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (call.from_user.id, who, 'День 1: Я в пустоши;', 1, False, 0, ''))
        con.commit()
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                              text=f'Локация: Бункер\nДень {a[call.from_user.id]["day"]}',
                              reply_markup=get_bunker_keyboard(call.from_user.id))
    else:
        splited_data = call.data.split('_')
        data = splited_data[2:]
        chat_id = call.from_user.id
        if call.data == 'wasteland_return':
            bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                  text=f'Локация: Бункер\nДень {a[call.from_user.id]["day"]}',
                                  reply_markup=get_bunker_keyboard(call.from_user.id))
        elif 'wasteland_return_' in call.data:
            splited_data = call.data.split('_')
            if splited_data[2] == 'bunker':
                day = cur.execute(
                    """Select day from wasteland where chat_id={} and who='{}'""".format(chat_id,
                                                                                         splited_data[3])).fetchone()[0]
                cur.execute("""UPDATE wasteland SET is_return=1, day_return=? where chat_id=? and who=?""",
                            (day, chat_id, splited_data[3]))
            else:
                day = 0
                cur.execute("""UPDATE wasteland SET is_return=0, day_return=? where chat_id=? and who=?""",
                            (day, chat_id, splited_data[3]))
            con.commit()
            bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                  text='Люди в пустоши:',
                                  reply_markup=get_wasteland_mans_keyboard(call.from_user.id))
        elif 'family' in call.data:
            who_data = splited_data[2]
            who = ''
            if who_data == 'dad':
                who = 'Папа'
            if who_data == 'mother':
                who = 'Мама'
            if who_data == 'sister':
                who = 'Сестра'
            if who_data == 'brother':
                who = 'Брат'
            q = f"""Select text from wasteland where chat_id = {chat_id} and who = '{who_data}'"""
            logs = "\n".join(con.execute(q).fetchone()[0].split(';'))
            q = f"""Select is_return from wasteland where chat_id = {chat_id} and who = '{who_data}'"""
            x = ''
            if con.execute(q).fetchone()[0]:
                q = f"""Select day_return from wasteland where chat_id = {chat_id} and who = '{who_data}'"""
                x = f'Дней до возвращания: {con.execute(q).fetchone()[0]}'
            bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                  text=f'{who} {a[chat_id][who_data + "_bd"]["emoji"]}'
                                       f'\nЗдоровье: {a[call.from_user.id][who_data + "_bd"]["hp"]}'
                                       f'\nСытость: {a[call.from_user.id][who_data + "_bd"]["hungry"]}'
                                       f'\nЖажда: {a[call.from_user.id][who_data + "_bd"]["water"]}'
                                       f'\nИммунитет: {a[call.from_user.id][who_data + "_bd"]["immunity"]}'
                                       f'\n\n{logs}\n\n{x}',
                                  reply_markup=get_wasteland_mans_keyboard(call.from_user.id))


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
        a[chat_id]['mother'] = cur.execute(q.format('mother', 'saves', chat_id)).fetchone()[0]
        a[chat_id]['dad'] = cur.execute(q.format('dad', 'saves', chat_id)).fetchone()[0]
        a[chat_id]['brother'] = cur.execute(q.format('brother', 'saves', chat_id)).fetchone()[0]
        a[chat_id]['sister'] = cur.execute(q.format('sister', 'saves', chat_id)).fetchone()[0]
        a[chat_id]['day'] = cur.execute(q.format('day', 'saves', chat_id)).fetchone()[0]
    except:
        pass


def get_bunker_keyboard(chat_id):
    bunker = telebot.types.InlineKeyboardMarkup(row_width=5)
    butts = []
    if a[chat_id]['dad']:
        butts.append(telebot.types.InlineKeyboardButton(text=f'Папа {a[chat_id]["dad_bd"]["emoji"]}',
                                                        callback_data='bunker_family_dad'))
    if a[chat_id]['mother']:
        butts.append(telebot.types.InlineKeyboardButton(text=f'Мама {a[chat_id]["mother_bd"]["emoji"]}',
                                                        callback_data='bunker_family_mother'))
    if a[chat_id]['brother']:
        butts.append(telebot.types.InlineKeyboardButton(text=f'Брат {a[chat_id]["brother_bd"]["emoji"]}',
                                                        callback_data='bunker_family_brother'))
    if a[chat_id]['sister']:
        butts.append(telebot.types.InlineKeyboardButton(text=f'Сестра {a[chat_id]["sister_bd"]["emoji"]}',
                                                        callback_data='bunker_family_sister'))
    bunker.add(*butts)
    bunker.add(telebot.types.InlineKeyboardButton(text='Инвентарь', callback_data='bunker_inventory'))
    bunker.add(telebot.types.InlineKeyboardButton(text='Журнал', callback_data='bunker_journal'),
               telebot.types.InlineKeyboardButton(text='Следующий день', callback_data='bunker_next_day'))
    bunker.add(telebot.types.InlineKeyboardButton(text='Пустошь', callback_data='bunker_wasteland'))

    return bunker


def get_wasteland_mans_keyboard(chat_id):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    q = f"""Select who from wasteland where chat_id = {chat_id}"""
    who = con.execute(q).fetchall()
    butts = []
    keyboard.add(telebot.types.InlineKeyboardButton(text=f'Назад',
                                                    callback_data='wasteland_return'))
    for i in who:
        i = i[0]
        q = f"""Select is_return from wasteland where chat_id={chat_id} and who='{i}'"""
        if i == 'dad':
            butts.append(telebot.types.InlineKeyboardButton(text=f'Папа {a[chat_id][f"{i}_bd"]["emoji"]}',
                                                            callback_data=f'wasteland_family_{i}'))
            if cur.execute(q).fetchone()[0]:
                butts.append(telebot.types.InlineKeyboardButton(text=f'Вернуть в пустошь',
                                                                callback_data=f'wasteland_return_wasteland_{i}'))
            else:
                butts.append(telebot.types.InlineKeyboardButton(text=f'Вернуть в бункер',
                                                                callback_data=f'wasteland_return_bunker_{i}'))
        elif i == 'mother':
            butts.append(telebot.types.InlineKeyboardButton(text=f'Мама {a[chat_id][f"{i}_bd"]["emoji"]}',
                                                            callback_data=f'wasteland_family_{i}'))
            if cur.execute(q).fetchone()[0]:
                butts.append(telebot.types.InlineKeyboardButton(text=f'Вернуть в пустошь',
                                                                callback_data=f'wasteland_return_wasteland_{i}'))
            else:
                butts.append(telebot.types.InlineKeyboardButton(text=f'Вернуть в бункер',
                                                                callback_data=f'wasteland_return_bunker_{i}'))
        elif i == 'brother':
            butts.append(telebot.types.InlineKeyboardButton(text=f'Брат {a[chat_id][f"{i}_bd"]["emoji"]}',
                                                            callback_data=f'wasteland_family_{i}'))
            if cur.execute(q).fetchone()[0]:
                butts.append(telebot.types.InlineKeyboardButton(text=f'Вернуть в пустошь',
                                                                callback_data=f'wasteland_return_wasteland_{i}'))
            else:
                butts.append(telebot.types.InlineKeyboardButton(text=f'Вернуть в бункер',
                                                                callback_data=f'wasteland_return_bunker_{i}'))
        elif i == 'sister':
            butts.append(telebot.types.InlineKeyboardButton(text=f'Сестра {a[chat_id][f"{i}_bd"]["emoji"]}',
                                                            callback_data=f'wasteland_family_{i}'))
            if cur.execute(q).fetchone()[0]:
                butts.append(telebot.types.InlineKeyboardButton(text=f'Вернуть в пустошь',
                                                                callback_data=f'wasteland_return_wasteland_{i}'))
            else:
                butts.append(telebot.types.InlineKeyboardButton(text=f'Вернуть в бункер',
                                                                callback_data=f'wasteland_return_bunker_{i}'))
    keyboard.add(*butts)
    return keyboard


def add_wasteland_event(count, chat_id):
    who_list = cur.execute("""Select who from wasteland where chat_id={}""".format(chat_id)).fetchall()
    for who in who_list:
        who = who[0]
        event_list = [x[0] for x in cur.execute("""Select event_id from wasteland_events""").fetchall()]
        event_list = sample(choice_event_id(event_list), k=count)
        for event_id in event_list:
            wasteland_event_system(chat_id, who, cur.execute(
                """Select day from wasteland where chat_id={} and who='{}'""".format(chat_id, who)).fetchone()[
                0], event_id)
        print(who, cur.execute(
                        """Select day from wasteland where chat_id={} and who='{}'""".format(chat_id, who)).fetchone()[
                         0])
        cur.execute("""UPDATE wasteland SET day=? where chat_id=? and who=?""",
                    (cur.execute(
                        """Select day from wasteland where chat_id={} and who='{}'""".format(chat_id, who)).fetchone()[
                         0] + 1, chat_id, who))
        print(who, cur.execute(
                        """Select day from wasteland where chat_id={} and who='{}'""".format(chat_id, who)).fetchone()[
                         0])
        is_return = cur.execute(
            """Select is_return from wasteland where chat_id={} and who='{}'""".format(chat_id, who)).fetchone()[0]
        if is_return:
            day_return = \
                cur.execute("""Select day_return from wasteland where chat_id={} and who='{}'""".format(chat_id,
                                                                                                        who)).fetchone()[
                    0]
            if day_return > 0:
                cur.execute("""UPDATE wasteland SET day_return=? where chat_id=? and who=?""",
                            (day_return - 1, chat_id, who))
            else:
                a[chat_id][who] = 1
                cur.execute("""Delete from wasteland where chat_id={} and who='{}'""".format(chat_id, who))
    con.commit()


def choice_event_id(event_list):
    res = []
    i = 0
    q = """Select not_choiced from wasteland_events where event_id={}"""
    n = len(event_list)
    while i != n:
        if len(event_list) != 0:
            x = choice(event_list)
            if cur.execute(q.format(x)).fetchone()[0] != 1:
                res.append(x)
                event_list.remove(x)
                i += 1
            else:
                event_list.remove(x)
        else:
            break
    return res


def wasteland_event_system(chat_id, who, day, event_id):
    text = f'{cur.execute("""Select text from wasteland where who="{}" and chat_id={}""".format(who, chat_id)).fetchone()[0]}День {day}: {cur.execute("""Select text from wasteland_events where event_id={}""".format(event_id)).fetchone()[0]};'
    cur.execute("""UPDATE wasteland SET text=?, day=? where chat_id=?""", (text, day, chat_id))
    x = cur.execute("""Select hp, immunity from wasteland_events where event_id={}""".format(event_id)).fetchall()[0]
    event_items = cur.execute("""Select items from wasteland_events where event_id={}""".format(event_id)).fetchone()[0]
    if x[0]:
        a[chat_id][who + '_bd']['hp'] += int(x[0])
    if x[1]:
        a[chat_id][who + '_bd']['immunity'] += int(x[1])
    who_items = \
    cur.execute("""Select items from wasteland where who='{}' and chat_id={}""".format(who, chat_id)).fetchone()[0]
    if who_items and event_items:
        res_items = str(who_items + ';' + event_items)
    else:
        res_items = str(who_items + event_items)
    cur.execute("""UPDATE wasteland SET items=? where chat_id=? and who=?""", (res_items, chat_id, who))
    next_event_id = \
    cur.execute("""Select next_event_id from wasteland_events where event_id={}""".format(event_id)).fetchall()[0]
    if next_event_id[0]:
        wasteland_event_system(chat_id, who, day, choice(next_event_id))


def create_family_bd(chat_id):
    if cur.execute("""Select chat_id from dad where chat_id == {}""".format(chat_id)).fetchone():
        q = """UPDATE {} SET hp = {}, hungry = {}, immunity = {}, emoji = "{}", water = {} WHERE chat_id == {}"""
        cur.execute(q.format('dad', a[chat_id]['dad_bd']['hp'], a[chat_id]['dad_bd']['hungry'],
                             a[chat_id]['dad_bd']['immunity'], a[chat_id]['dad_bd']['emoji'],
                             a[chat_id]['dad_bd']['water'], chat_id))
        cur.execute(q.format('mother', a[chat_id]['mother_bd']['hp'], a[chat_id]['mother_bd']['hungry'],
                             a[chat_id]['mother_bd']['immunity'], a[chat_id]['mother_bd']['emoji'],
                             a[chat_id]['mother_bd']['water'], chat_id))
        cur.execute(q.format('brother', a[chat_id]['brother_bd']['hp'], a[chat_id]['brother_bd']['hungry'],
                             a[chat_id]['brother_bd']['immunity'], a[chat_id]['brother_bd']['emoji'],
                             a[chat_id]['brother_bd']['water'], chat_id))
        cur.execute(q.format('sister', a[chat_id]['sister_bd']['hp'], a[chat_id]['sister_bd']['hungry'],
                             a[chat_id]['sister_bd']['immunity'], a[chat_id]['sister_bd']['emoji'],
                             a[chat_id]['sister_bd']['water'], chat_id))
    else:
        cur.execute("""INSERT INTO dad VALUES (?, ?, ?, ?, ?, ?)""",
                    (chat_id, a[chat_id]['dad_bd']['hp'], a[chat_id]['dad_bd']['hungry'],
                     a[chat_id]['dad_bd']['water'], a[chat_id]['dad_bd']['immunity'],
                     a[chat_id]['dad_bd']['emoji']))
        cur.execute("""INSERT INTO mother VALUES (?, ?, ?, ?, ?, ?)""",
                    (chat_id, a[chat_id]['mother_bd']['hp'], a[chat_id]['mother_bd']['hungry'],
                     a[chat_id]['mother_bd']['water'], a[chat_id]['mother_bd']['immunity'],
                     a[chat_id]['mother_bd']['emoji']))
        cur.execute("""INSERT INTO brother VALUES (?, ?, ?, ?, ?, ?)""",
                    (chat_id, a[chat_id]['brother_bd']['hp'], a[chat_id]['brother_bd']['hungry'],
                     a[chat_id]['brother_bd']['water'], a[chat_id]['brother_bd']['immunity'],
                     a[chat_id]['brother_bd']['emoji']))
        cur.execute("""INSERT INTO sister VALUES (?, ?, ?, ?, ?, ?)""",
                    (chat_id, a[chat_id]['sister_bd']['hp'], a[chat_id]['sister_bd']['hungry'],
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
    family_menu = telebot.types.InlineKeyboardMarkup()
    family_menu.add(telebot.types.InlineKeyboardButton(text='Назад', callback_data='bunker_family_return'))
    family_menu.add(telebot.types.InlineKeyboardButton(text='Отправить в пустошь',
                                                       callback_data=f"wasteland_{call.data[len('bunker_family_'):]}_go"))
    bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                          text=f'{who} {a[call.from_user.id][who_bd]["emoji"]}'
                               f'\nЗдоровье: {a[call.from_user.id][who_bd]["hp"]}'
                               f'\nСытость: {a[call.from_user.id][who_bd]["hungry"]}'
                               f'\nЖажда: {a[call.from_user.id][who_bd]["water"]}'
                               f'\nИммунитет: {a[call.from_user.id][who_bd]["immunity"]}',
                          reply_markup=family_menu)


def save_update_to_bd(chat_id):
    x = cur.execute("""Select chat_id from saves where chat_id == ?""", (chat_id,)).fetchone()
    if x:
        inventory = ';'.join(a[chat_id]['inventory'])
        cur.execute(
            """UPDATE saves SET chat_id = ?, inventory = ?, name = ?, mother = ?, dad = ?, brother = ?, sister = ?, day = ? WHERE chat_id == ?""",
            (chat_id, inventory, a[chat_id]['name'], a[chat_id]['mother'], a[chat_id]['dad'],
             a[chat_id]['brother'], a[chat_id]['sister'], a[chat_id]['day'], chat_id))
        create_family_bd(chat_id)
    else:
        inventory = ';'.join(a[chat_id]['inventory'])
        cur.execute("""INSERT INTO saves VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (chat_id, inventory, a[chat_id]['name'], a[chat_id]['mother'], a[chat_id]['dad'],
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
    second = 5
    sms = bot.send_message(call.message.chat.id, 'У тебя осталось {} {} и {} места'.format(
        second, morph('секунда')[0].make_agree_with_number(second).word, weight_list[user]), reply_markup=items())
    while second > 0:
        time.sleep(1)
        second -= 1
        bot.edit_message_text(chat_id=sms.chat.id, message_id=sms.message_id,
                              text='У тебя осталось {} {}  и {} места'.format(
                                  second, morph('секунда')[0].make_agree_with_number(second).word,
                                  weight_list[user]),
                              reply_markup=items())
        if weight_list[user] == 0 or second == 0:
            bot.send_message(call.message.chat.id, 'Вот что вы взяли с собой:\n' + '\n'.join(
                '{}. {}'.format(i + 1, item) for i, item in enumerate(package.get(user, ['Пусто']))))
            bot.edit_message_text(chat_id=sms.chat.id, message_id=sms.message_id,
                                  text='Время закончилось' if second == 0 else 'Место закончилось')
            markup = types.ReplyKeyboardMarkup(True)
            markup.add(
                types.InlineKeyboardButton('Донат'),
                types.InlineKeyboardButton('Поддержка'),
                types.InlineKeyboardButton('Помощь новичкам')
            )
            bot.send_message(call.message.chat.id, 'Пора в бункер', reply_markup=markup)
            bunker(call.message)
    #  save BD package
    a[call.from_user.id] = a[0]
    a[call.from_user.id]['inventory'] = package[user]
    save_update_to_bd(call.from_user.id)


def bunker(message):
    get_data_from_bd(message.chat.id)
    bot.send_message(message.chat.id, f'Локация: Бункер\nДень {a[message.chat.id]["day"]}',
                     reply_markup=get_bunker_keyboard(message.chat.id))


time_list = {}
user_list = []
weight_list = {}
morph = pymorphy2.MorphAnalyzer().parse
FOOD = {'vodka': ('водка', 1), 'mask': ('маска', 3), 'medicinechest': ('аптечка', 3), 'soap': ('мыло', 3),
        'sausage': ('колбаса', 3)}
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
        bot.send_message(message.chat.id, '{}, ты выжил?\nРешишься сыграть в игру?'.format(name),
                         reply_markup=murkup)
        user_list.append(message.from_user.username)
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
            bot.send_message(call.message.chat.id,
                             'Приготовься выживать в новом мире, которому грозит пандемия, вы решаетесь спрятаться в бункере, у тебя есть 60 секунд чтобы собрать все вещи до того как приедет полиция из-за подозрений на заражение',
                             reply_markup=markup)
        elif type == 'no':
            murkup = types.InlineKeyboardMarkup(row_width=2)
            item_1 = types.InlineKeyboardButton('Да', callback_data='play_yes')
            item_2 = types.InlineKeyboardButton('Нет', callback_data='play_no')
            murkup.add(item_1, item_2)
            bot.send_message(call.message.chat.id, 'Сыканул, может все таки сыграешь?',
                             reply_markup=murkup)
        elif type == 'start':
            weight_list[user] = 20
            thread1 = Thread(target=time_, args=(call, user))
            thread1.start()
            time_list[call.from_user.username] = thread1
        elif type == 'end':
            bot.send_message(call.message.chat.id,
                             'Справедливо, но из-за этого вы уже реально заразились в общей больнице, а ведь могли рискнуть и выжить')
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
                bot.answer_callback_query(callback_query_id=call.id, text='Мы положили в сумку: {}'.format(
                    morph(FOOD[item][0])[0].inflect({'accs'}).word))


while True:
    try:
        bot.polling()
    except Exception as e:
        bot.polling()
        print('bot.polling |', e)
