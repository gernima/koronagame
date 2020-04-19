import telebot
import time
from telebot import types
from threading import Thread
import pymorphy2
import sqlite3
from random import choice, random, sample
from event import events

bot = telebot.TeleBot('1049041175:AAFHw6FXE2-yCv7L4sJmwg50eImuAusJOG0')
print('start')

a = {0: {'inventory': {}, 'name': 'a', 'mother': 0, 'dad': 0, 'brother': 0, 'sister': 0, 'day': 1,
         'dad_bd': {'hp': 50, 'hungry': 50, 'water': 50, 'immunity': 50, 'emoji': '😕'},
         'mother_bd': {'hp': 50, 'hungry': 50, 'water': 50, 'immunity': 50, 'emoji': '😌'},
         'brother_bd': {'hp': 50, 'hungry': 50, 'water': 50, 'immunity': 50, 'emoji': '🤨'},
         'sister_bd': {'hp': 50, 'hungry': 50, 'water': 50, 'immunity': 50, 'emoji': '😔'}}}
con = sqlite3.connect("bd.db", check_same_thread=False)
cur = con.cursor()
time_list = {}
family = {}
user_list = []
weight_list = {}
morph = pymorphy2.MorphAnalyzer().parse
FOOD = {'father': ('Папа', 'father', 15, 1),
        'daughter': ('Сестра', 'daughter',15, 1),
        'mother': ('Мама', 'mother', 15, 1),
        'son': ('Брат', 'son', 15, 1),
        'mask': ('маска', 'mask', 3, 1),
        'medicinechest': ('аптечка', 'medicinechest', 3, 1),
        'soap': ('мыло', 'soap', 3, 1),
        'obrez': ('обрез', 'obrez', 50, 1, 1),
        'cannedfood': ('консервы', 'cannedfood', 3, 6, 50),
        'water': ('вода', 'water', 2, 6, 50)}
package = {}


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
        inv_items = "\n".join([f"{FOOD[x][0]}: {a[call.from_user.id]['inventory'][x]}" for x in a[call.from_user.id]["inventory"].keys()])
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                              text=f'Ваши вещи:\n{inv_items}',
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
    elif call.data == 'bunker_family_feed':
        name = call.message.text.split("\n")[0]
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(text='Назад', callback_data='bunker_family_return'),
                   types.InlineKeyboardButton(text=f'{1} x Консервы + 50 сытости',
                                              callback_data=f'bunker_food_cannedfood_{name}'),
                   types.InlineKeyboardButton(text=f'{1} x Вода + 50 вода', callback_data=f'bunker_food_water_{name}'))
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
    elif 'food' in call.data:
        name_ = call.data.split('_')[-1]
        name = ''
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(text='Назад', callback_data='bunker_family_return'),
                   types.InlineKeyboardButton(text=f'{1} x Консервы + 50 сытости',
                                              callback_data=f'bunker_food_cannedfood_{name_}'),
                   types.InlineKeyboardButton(text=f'{1} x Вода + 50 вода',
                                              callback_data=f'bunker_food_water_{name_}'))
        if 'Папа' in name_:
            name = 'dad_bd'
        elif 'Мама' in name_:
            name = 'mother_bd'
        elif 'Брат' in name_:
            name = 'brother_bd'
        elif 'Сестра' in name_:
            name = 'sister_bd'
        if 'cannedfood' in call.data:
            if a[call.message.chat.id][name]['hungry'] <= 90:
                a[call.message.chat.id][name]['hungry'] += 10
            else:
                return
        else:
            if a[call.message.chat.id][name]['water'] <= 90:
                a[call.message.chat.id][name]['water'] += 10
            else:
                return
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'{name_}'
                              f'\nНастроение: {a[call.from_user.id][name]["mood"]}'
                              f'\nСытость: {a[call.from_user.id][name]["hungry"]}'
                              f'\nЖажда: {a[call.from_user.id][name]["water"]}'
                              f'\nИммунитет: {a[call.from_user.id][name]["immunity"]}',
                              reply_markup=markup)
    elif call.data == 'bunker_journal':
        chance = random()
        if chance < .4:
            event = choice(events['good'])
        elif .5 > chance > .4:
            event = choice(events['bad'])
        else:
            event = choice(events['choice'])
        event_run(event, call.message)


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
                            (day - 1, chat_id, splited_data[3]))
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
                x = f'Дней до возвращания: {con.execute(q).fetchone()[0] + 1}'
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


def event_run(event, message):
    if event == 'пауки в бункере':
        bot.send_message(message.chat.id,
                         'Это безумие! Мы постоянно находим пауков. Они в нашем '
                         'супе. Они в нашей воде. Мы клянемся, что некоторые из них продолжают возвращаться, и они'
                         ' становятся больше с каждым разом, когда мы их видим! Так продолжаться не может. Пришло '
                         'время вести войну с этими пауками!')

    elif event == 'мама начала чихать':
        bot.send_message(message.chat.id, 'мама кашляет')  # мама теряет иммунитет
    elif event == 'нашли консервы':
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(text='Взять', callback_data='event_canned_food_get'),
            types.InlineKeyboardButton(text='Выбросить', callback_data='event_canned_food_delete'),
            types.InlineKeyboardButton(text='Надеть всем', callback_data='event_canned_food_put_on')
        )
        bot.send_message(message.chat.id, 'Вы нашли консервы', reply_markup=markup)


def bunker(message):
    get_data_from_bd(message.chat.id)
    bot.send_message(message.chat.id, f'Локация: Бункер\nДень {a[message.chat.id]["day"]}',
                     reply_markup=get_bunker_keyboard(message.chat.id))


def get_data_from_bd(chat_id):
    try:
        if chat_id not in a.keys():
            a[chat_id] = a[0]
        q = """Select {} from {} where chat_id == {}"""
        bd_family(chat_id, list(cur.execute(q.format('*', 'dad', chat_id)).fetchone()[1:]))
        bd_family(chat_id, list(cur.execute(q.format('*', 'mother', chat_id)).fetchone()[1:]))
        bd_family(chat_id, list(cur.execute(q.format('*', 'brother', chat_id)).fetchone()[1:]))
        bd_family(chat_id, list(cur.execute(q.format('*', 'sister', chat_id)).fetchone()[1:]))
        inv = {}
        b = cur.execute(q.format('inventory', 'saves', chat_id)).fetchone()[0].split(';')
        if len(b) > 0 and b[0].strip() != '':
            for i in [x.split(':') for x in b]:
                inv[i[0]] = i[1]
            a[chat_id]['inventory'] = inv
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
        cur.execute("""UPDATE wasteland SET day=? where chat_id=? and who=?""",
                    (cur.execute(
                        """Select day from wasteland where chat_id={} and who='{}'""".format(chat_id, who)).fetchone()[
                         0] + 1, chat_id, who))
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
                b = cur.execute("""Select items from wasteland where chat_id={} and who='{}'""".format(chat_id, who)).fetchone()[
                    0].split(';')
                if len(b) != 0:
                    for i in [x.split(':') for x in b]:
                        if i[0] in a[chat_id]['inventory'].keys():
                            n = int(i[1]) + int(a[chat_id]['inventory'][i[0]])
                            a[chat_id]['inventory'][i[0]] = int(n)
                        else:
                            a[chat_id]['inventory'][i[0]] = int(i[1])
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
    who_items = cur.execute("""Select items from wasteland where chat_id={}""".format(chat_id)).fetchone()[0].split(';')
    res_items = {}
    if len(who_items) > 0 and who_items[0].strip() != '':
        for i in [x.split(':') for x in who_items]:
            res_items[i[0]] = int(i[1])
    tf = True
    if res_items:
        wasteland_event_items(event_id, res_items)
    next_event_id = \
        cur.execute("""Select next_event_id from wasteland_events where event_id={}""".format(event_id)).fetchone()[0]
    if next_event_id and tf:
        if type(next_event_id) is type(int()):
            res_items, tf = next_event_items(res_items, next_event_id, tf)
        else:
            for next_event_i in next_event_id.split(';'):
                res_items, tf = next_event_items(res_items, next_event_i, tf)
                if tf is False:
                    break
    if tf:
        text = f'{cur.execute("""Select text from wasteland where who="{}" and chat_id={}""".format(who, chat_id)).fetchone()[0]}День {day}: {cur.execute("""Select text from wasteland_events where event_id={}""".format(event_id)).fetchone()[0]};'
        cur.execute("""UPDATE wasteland SET text=?, day=? where chat_id=?""", (text, day, chat_id))
        x = cur.execute("""Select hp, immunity from wasteland_events where event_id={}""".format(event_id)).fetchall()[0]
        if x[0]:
            a[chat_id][who + '_bd']['hp'] += int(x[0])
        if x[1]:
            a[chat_id][who + '_bd']['immunity'] += int(x[1])
        res_items = ';'.join([f'{x}:{res_items[x]}' for x in res_items.keys()])
        cur.execute("""UPDATE wasteland SET items=? where chat_id=? and who=?""", (res_items, chat_id, who))
        if next_event_id:
            if type(next_event_id) is type(int()):
                wasteland_event_system(chat_id, who, day, next_event_id)
            else:
                wasteland_event_system(chat_id, who, day, choice(next_event_id))


def wasteland_event_items(event_id, res_items, tf=True):
    first_items = res_items
    items_plus = \
        cur.execute("""Select items_plus from wasteland_events where event_id={}""".format(event_id)).fetchone()[
            0]
    if items_plus and items_plus[0].strip() != '':
        items_plus = items_plus.split(';')
        if len(items_plus) > 0 and items_plus[0].strip() != '':
            for i in [x.split(':') for x in items_plus]:
                if i[0] in res_items.keys():
                    res_items[i[0]] = int(res_items[i[0]]) + int(i[1])
                else:
                    res_items[i[0]] = int(i[1])
    items_minus = \
        cur.execute("""Select items_minus from wasteland_events where event_id={}""".format(event_id)).fetchone()[
            0]
    if items_minus and items_minus[0].strip() != '':
        items_minus = items_minus.split(';')
        if len(items_minus) > 0 and items_minus[0].strip() != '':
            for i in [x.split(':') for x in items_minus]:
                if i[0] in res_items.keys():
                    if res_items[i[0]] - int(i[1]) > 0:
                        res_items[i[0]] = int(res_items[i[0]]) - int(i[1])
                    elif res_items[i[0]] - int(i[1]) == 0:
                        del res_items[i[0]]
                    else:
                        tf = False
                        break
    if tf:
        return res_items, tf
    else:
        return first_items, tf


def next_event_items(res_items, event_id, tf):
    if tf:
        res_items, tf = wasteland_event_items(event_id, res_items, tf)
        if tf:
            next_event_id = \
                cur.execute("""Select next_event_id from wasteland_events where event_id={}""".format(event_id)).fetchone()[
                    0]
            if next_event_id and str(next_event_id).strip() != '':
                if type(next_event_id) is type(int()):
                    res_items, tf = next_event_items(res_items, next_event_id, tf)
                else:
                    for next_event_i in next_event_id.split(';'):
                        res_items, tf = next_event_items(res_items, next_event_i, tf)
    return res_items, tf


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
        inventory = ';'.join([f'{x}:{a[chat_id]["inventory"][x]}' for x in a[chat_id]['inventory'].keys()])
        cur.execute(
            """UPDATE saves SET chat_id = ?, inventory = ?, name = ?, mother = ?, dad = ?, brother = ?, sister = ?, day = ? WHERE chat_id == ?""",
            (chat_id, inventory, a[chat_id]['name'], a[chat_id]['mother'], a[chat_id]['dad'],
             a[chat_id]['brother'], a[chat_id]['sister'], a[chat_id]['day'], chat_id))
        create_family_bd(chat_id)
    else:
        if family[chat_id]:
            if 'Папа' in family[chat_id]:
                a[chat_id]['dad'] = 1
            if 'Сестра' in family[chat_id]:
                a[chat_id]['sister'] = 1
            if 'Брат' in family[chat_id]:
                a[chat_id]['brother'] = 1
            if 'Мама' in family[chat_id]:
                a[chat_id]['mother'] = 1
            if family[chat_id]:
                del family[chat_id]
        inventory = ';'.join([f'{x}:{a[chat_id]["inventory"][x]}' for x in a[chat_id]['inventory'].keys()])
        cur.execute("""INSERT INTO saves VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (chat_id, inventory, a[chat_id]['name'], a[chat_id]['mother'], a[chat_id]['dad'],
                     a[chat_id]['brother'], a[chat_id]['sister'], a[chat_id]['day']))
        create_family_bd(chat_id)
    con.commit()


def items_how_many_things_are_left(user, item):
    return FOOD[item][3] - package.get(user, {}).get(FOOD[item][1], 0)


def items(user):
    markup = types.InlineKeyboardMarkup()
    item_1 = types.InlineKeyboardButton(text='', callback_data='item_')
    markup.add(types.InlineKeyboardButton(text='Бежииим!!!!!', callback_data='run'))
    family_button = {'father': types.InlineKeyboardButton(
        text=f'{items_how_many_things_are_left(user, "father")} x Папа - 15',
        callback_data='item_father'),
        'mother': types.InlineKeyboardButton(
            text=f'{items_how_many_things_are_left(user, "mother")} x Мама - 15',
            callback_data='item_mother'),
        'son': types.InlineKeyboardButton(
            text=f'{items_how_many_things_are_left(user, "son")} x Сын - 15',
            callback_data='item_son'),
        'daughter': types.InlineKeyboardButton
        (text=f'{items_how_many_things_are_left(user, "daughter")} x Дочь - 15',
         callback_data='item_daughter'), }
    item_button = [types.InlineKeyboardButton(
            text=f'{items_how_many_things_are_left(user, key)} x {value[0]} - {value[2]}',
            callback_data=f'item_{key}')
        for key, value in FOOD.items() if package.get(user, {}).get(value[1], 0) != value[3]
                                          and value[1] not in family_button.keys()]
    button = [family_button[i] for i in
              filter(lambda x: FOOD[x][0] not in family.get(user, []), family_button)] + \
             item_button
    for i in range(0, len(button), 2):
        markup.add(*button[i:i + 2])
    return markup


def car(message):
    text = ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_',
            '🚗💨']
    run = bot.send_message(message.chat.id, '_______________🚗💨')
    for i in range(1, len(text)):
        time.sleep(0.1)
        bot.edit_message_text(chat_id=run.chat.id, message_id=run.message_id,
                              text=''.join(text))
        text[- i - 1], text[- i] = text[- i], text[- i - 1]
    bot.edit_message_text(chat_id=run.chat.id, message_id=run.message_id,
                          text='🚗________________')


def time_cheker(call, user):
    second = 60
    sms = bot.send_message(call.message.chat.id, 'У тебя осталось {} {} и {} места в бункере'.format(
        second, morph('секунда')[0].make_agree_with_number(second).word, weight_list[user]),
                           reply_markup=items(user))
    while second > 0:
        time.sleep(1)
        second -= 1
        bot.edit_message_text(chat_id=sms.chat.id, message_id=sms.message_id,
                              text='У тебя осталось {} {}  и {} места в бункере'.format(
                                  second, morph('секунда')[0].make_agree_with_number(second).word,
                                  weight_list[user]), reply_markup=items(user))
        if weight_list[user] < 1 or second == 0:
            if package.get(user, False):
                bot.send_message(call.message.chat.id, 'Вот что вы взяли с собой:\n' +
                                 '\n'.join(
                                     '{}. {} x {}'.format(i + 1, FOOD[item[0]][0], item[1]) for i, item in
                                     enumerate(package[user].items())))
            else:
                bot.send_message(call.message.chat.id,
                                 'Вы ничего с собой не взяли, да ты хардкорный чел')
            bot.send_message(call.message.chat.id, 'Из семьи вы взяли:\n' + '\n'.join(
                '{}. {}'.format(i + 1, item) for i, item in
                enumerate(family.get(user, ['Никого, но как же так?)']))))
            bot.edit_message_text(chat_id=sms.chat.id, message_id=sms.message_id,
                                  text='Время закончилось' if second == 0 else 'Место закончилось')
            markup = types.ReplyKeyboardMarkup(True)
            markup.add(
                types.InlineKeyboardButton('Донат'),
                types.InlineKeyboardButton('Поддержка'),
                types.InlineKeyboardButton('Помощь новичкам')
            )
            bot.send_message(call.message.chat.id, 'Пора в бункер', reply_markup=markup)

            a[call.from_user.id] = a[0]
            if len(package.keys()) != 0:
                a[call.from_user.id]['inventory'] = package[user]
            save_update_to_bd(call.from_user.id)
            for i in (package, weight_list):
                if user in i:
                    del i[user]
            car(call.message)
            bunker(call.message)
            return


@bot.message_handler(commands=['start', 'new_game'])
def start_message(message):
    if message.text == '/start':
        if message.from_user.username not in user_list:
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
            print("Список пользователей", user_list)
        else:
            bot.delete_message(message.chat.id, message.message_id)
    elif message.text == '/new_game':
        murkup = types.InlineKeyboardMarkup(row_width=2)
        item_1 = types.InlineKeyboardButton('Да', callback_data='play_start')
        item_2 = types.InlineKeyboardButton('Нет', callback_data='play_continue')
        murkup.add(item_1, item_2)
        bot.send_message(message.chat.id, 'Ты точно хочешь начать все с начала?',
                         reply_markup=murkup)


@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == '1':
        bunker(message)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    global weight_list
    user = call.from_user.id
    name = call.data
    name_type = name.split('_')[0]
    if name_type == 'play':
        type = name.split('_')[1]
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
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
            print('Счетчик: ' + call.from_user.username)
            weight_list[user] = 50
            thread1 = Thread(target=time_cheker, args=(call, user))
            thread1.start()
            time_list[user] = thread1
        elif type == 'end':
            bot.send_message(call.message.chat.id,
                             'Справедливо, но из-за этого вы уже реально заразились в общей больнице, а ведь могли рискнуть и выжить')
        elif type == 'continue':
            pass
    elif name_type == 'item':
        item = FOOD[name.split('_')[1]]
        item_weight = item[2]
        item_name = item[0]
        if weight_list[user] != 0:
            if weight_list[user] - item_weight < 0:
                bot.answer_callback_query(callback_query_id=call.id, text='Недостаточно места')
            else:
                text = 'Мы положили в сумку: {}'
                if item[1] in ['mother', 'daughter', 'son', 'father']:
                    if item_name not in family.get(user, []):
                        text = 'Вы взяли с собой в бункер: {}'
                        family[user] = family.get(user, []) + [item_name]
                        bot.answer_callback_query(callback_query_id=call.id, text=text.format(
                            morph(item_name)[0].inflect({'accs'}).word))
                        weight_list[user] -= item_weight
                    else:
                        bot.answer_callback_query(callback_query_id=call.id,
                                                  text='Вы уже взяли этого члена семьи')
                else:
                    package[user] = package.get(call.from_user.username, {})
                    if package[user].get(item[1], 0) != item[3]:
                        package[user][item[1]] = package[user].get(item[1], 0) + 1
                        weight_list[user] -= item_weight
                        bot.answer_callback_query(callback_query_id=call.id,
                                                  text=text.format(
                                                      morph(item_name)[0].inflect({'accs'}).word))
    elif name_type == 'run':
        print(user, 'убежал')
        weight_list[user] = 0


try:
    bot.polling()
except Exception as e:
    bot.polling()
    print('бот упал, молодца\n', e)
