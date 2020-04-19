import telebot
import time
from telebot import types
from threading import Thread
import pymorphy2
import sqlite3
from random import choice, random, sample
from event import events

bot = telebot.TeleBot('1077053623:AAE8yg9jrRas7h7mTgKaNQAjOTeIsgwJHGI')
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
        'sister': ('Сестра', 'sister',15, 1),
        'mother': ('Мама', 'mother', 15, 1),
        'brother': ('Брат', 'brother', 15, 1),
        'mask': ('маска', 'mask', 3, 1),
        'medicinechest': ('аптечка', 'medicinechest', 3, 1),
        'soap': ('мыло', 'soap', 3, 4),
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
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Назад', callback_data='wasteland_return'))
        inv_items = "\n".join([f"{FOOD[x][0]}: {a[call.from_user.id]['inventory'][x]}" for x in
                               a[call.from_user.id]["inventory"].keys()])
        if not a[call.from_user.id]["inventory"].keys():
            inv_items = 'Пусто'
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                              text=f'Ваши вещи:\n{inv_items}',
                              reply_markup=markup)
    elif call.data == 'bunker_family_return':
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                              text=f'Локация: Бункер\nДень {a[call.from_user.id]["day"]}',
                              reply_markup=get_bunker_keyboard(call.from_user.id))
    elif call.data == 'bunker_next_day':
        # try:
        # add_wasteland_event
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
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=water_and_canned(call, name))
    elif 'food' in call.data:
        name_ = call.data.split('_')[-1]
        name = ''
        if 'Папа' in name_:
            name = 'dad_bd'
        elif 'Мама' in name_:
            name = 'mother_bd'
        elif 'Брат' in name_:
            name = 'brother_bd'
        elif 'Сестра' in name_:
            name = 'sister_bd'
        if 'cannedfood' in call.data:
            if a[call.message.chat.id][name]['hungry'] <= 90 and a[call.from_user.id]["inventory"].get("cannedfood", 0) > 0:
                a[call.message.chat.id][name]['hungry'] += 10
            else:
                return
        else:
            if a[call.message.chat.id][name]['water'] <= 90 and a[call.from_user.id]["inventory"].get("water", 0) > 0:
                a[call.message.chat.id][name]['water'] += 10
            else:
                return
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'{name_}'
                              f'\nНастроение: {a[call.from_user.id][name]["hp"]}'
                              f'\nСытость: {a[call.from_user.id][name]["hungry"]}'
                              f'\nЖажда: {a[call.from_user.id][name]["water"]}'
                              f'\nИммунитет: {a[call.from_user.id][name]["immunity"]}',
                              reply_markup=water_and_canned(call, name_))
    elif call.data == 'bunker_journal':
        event_run(call.message)


@bot.callback_query_handler(func=lambda call: 'event' in call.data)
def event_logic(call):
    text = call.data.split('_')
    event, button = text[1], ''.join(text[2:])
    print(button)
    chat_id = call.message.chat.id
    family = [i for i in ['mother', 'dad', 'brother', 'sister'] if a[chat_id][i] != 0]
    if event == 'spider':
        people = choice(family)
        people_immunity = a[chat_id][people + '_bd']['immunity']
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Назад', callback_data='wasteland_return'))
        if button == 'continue':
            for i in family:
                a[chat_id][i + '_bd']['immunity'] = min(a[chat_id][i + '_bd']['immunity'] - 20, 0)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                text='Не надо было оставлять эту проблему, все члены семьи получили психическое '
                'растройство, а так же их покусали пауки, падение иммунитета у всей семьи', reply_markup=markup)
        elif button == 'medicinechest':
            a[chat_id][people + '_bd']['immunity'] = max(people_immunity + 10, 100)
            people = morph(FOOD[people][0])[0].inflect({"gent"}).word
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Пауки были вымешленные, вы приняли таблетки и все'
                                                   f' прошло, а у {people} прошла старая болезнь', reply_markup=markup)
        elif button == 'war':
            a[chat_id][people + '_bd']['immunity'] = min(people_immunity - 5, 0)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'Вы отбились от пауков, но один из них укусил {FOOD[people][0]}', reply_markup=markup)


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


def water_and_canned(call, name_):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton(text='Назад', callback_data='bunker_family_return'),
               types.InlineKeyboardButton(
                   text=f'{a[call.from_user.id]["inventory"].get("cannedfood", 0)} x Консервы + 50 сытости',
                   callback_data=f'bunker_food_cannedfood_{name_}'),
               types.InlineKeyboardButton(
                   text=f'{a[call.from_user.id]["inventory"].get("water", 0)} x Вода + 50 вода',
                   callback_data=f'bunker_food_water_{name_}'))
    return markup


def bd_family(chat_id, data):
    x = 0
    for i in a[chat_id]['dad_bd'].keys():
        a[chat_id][i] = data[x]
        x += 1


def event_run(message):
    chance = random()
    event = ''
    if chance < .3:
        event = choice(events['good'])
    elif .6> chance > .3:
        event = choice(events['bad'])
    else:
        event = choice(events['choice'])
    markup = types.InlineKeyboardMarkup()
    package = set(list(a[message.chat.id]['inventory']))
    if event == 'пауки в бункере':
        if 'medicinechest' in package:
            markup.add(
                types.InlineKeyboardButton(text='аптечка', callback_data='event_spider_medicinechest'),
                types.InlineKeyboardButton(text='война с пауками', callback_data='event_spider_war')
                    )
            markup.add(types.InlineKeyboardButton(text='не обращать внимания', callback_data='event_spider_continue'))
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                             text='Это безумие! Мы постоянно находим пауков. Они в нашем '
                             'супе. Они в нашей воде. Мы клянемся, что некоторые из них продолжают возвращаться, и они'
                             ' становятся больше с каждым разом, когда мы их видим! Так продолжаться не может. Пришло '
                             'время вести войну с этими пауками!', reply_markup=markup)
            a[message.chat.id]['inventory']['medicinechest'] -= 1
            if a[message.chat.id]['inventory']['medicinechest'] == 0:
                del a[message.chat.id]['inventory']['medicinechest']
        else:
            event_run(message)
    elif event == 'доставка от правительства':
        markup.add(types.InlineKeyboardButton('Назад', callback_data='wasteland_return'))
        item = choice(['water', 'medicinechest', 'cannedfood'])
        a[message.chat.id]['inventory'][item] = a[message.chat.id
                                                ]['inventory'].get(item, 0) + 1
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=f'Вы получаете помощь от правительства: {FOOD[item][0]}', reply_markup=markup)
    elif event == 'консервы просрочены':
        if 'cannedfood' in package:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Назад', callback_data='wasteland_return'))
            a[message.chat.id]['inventory']['cannedfood'] -= 1
            if a[message.chat.id]['inventory']['cannedfood'] == 0:
                del a[message.chat.id]['inventory']['medicinechest']
            bot.edit_message_text(message.chat.id, 'Одна консерва оказалась просрочена, пришлось ее выкинуть', reply_markup=markup)
        else:
            event_run(message)


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
        if len(b) > 0 and b[0] != '':
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
                            n = i[1] + a[chat_id]['inventory'][i[0]]
                            a[chat_id]['inventory'][i[0]] = n
                        else:
                            a[chat_id]['inventory'][i[0]] = i[1]
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
    if x[0]:
        a[chat_id][who + '_bd']['hp'] += int(x[0])
    if x[1]:
        a[chat_id][who + '_bd']['immunity'] += int(x[1])
    b = cur.execute("""Select items from wasteland_events where event_id={}""".format(event_id)).fetchone()[0]
    cur.execute("""UPDATE wasteland SET items=? where chat_id=? and who=?""", (b, chat_id, who))
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
    family_menu.add(telebot.types.InlineKeyboardButton(text='Кормить', callback_data='bunker_family_feed'))
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
        print(family)
        if family.get(chat_id, False):
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


def items_how_many_things_are_left(chat_id, item):
    return FOOD[item][3] - package.get(chat_id, {}).get(FOOD[item][1], 0)


def items(chat_id):
    markup = types.InlineKeyboardMarkup()
    item_1 = types.InlineKeyboardButton(text='', callback_data='item_')
    markup.add(types.InlineKeyboardButton(text='Бежииим!!!!!', callback_data='run'))
    family_button = {'father': types.InlineKeyboardButton(
        text=f'{items_how_many_things_are_left(chat_id, "father")} x Папа - 15',
        callback_data='item_father'),
        'mother': types.InlineKeyboardButton(
            text=f'{items_how_many_things_are_left(chat_id, "mother")} x Мама - 15',
            callback_data='item_mother'),
        'brother': types.InlineKeyboardButton(
            text=f'{items_how_many_things_are_left(chat_id, "brother")} x Сын - 15',
            callback_data='item_brother'),
        'sister': types.InlineKeyboardButton
        (text=f'{items_how_many_things_are_left(chat_id, "sister")} x Дочь - 15',
         callback_data='item_sister'), }
    item_button = [types.InlineKeyboardButton(
            text=f'{items_how_many_things_are_left(chat_id, key)} x {value[0]} - {value[2]}',
            callback_data=f'item_{key}')
        for key, value in FOOD.items() if package.get(chat_id, {}).get(value[1], 0) != value[3]
                                          and value[1] not in family_button.keys()]
    button = [family_button[i] for i in
              filter(lambda x: FOOD[x][0] not in family.get(chat_id, []), family_button)] + \
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


def time_cheker(call, chat_id):
    second = 60
    sms = bot.send_message(call.message.chat.id, 'У тебя осталось {} {} и {} места в бункере'.format(
        second, morph('секунда')[0].make_agree_with_number(second).word, weight_list[chat_id]),
                           reply_markup=items(chat_id))
    while second > 0:
        time.sleep(1)
        second -= 1
        bot.edit_message_text(chat_id=sms.chat.id, message_id=sms.message_id,
                              text='У тебя осталось {} {}  и {} места в бункере\nНе забудь взять минимум 1 члена семьи'.format(
                                  second, morph('секунда')[0].make_agree_with_number(second).word,
                                  weight_list[chat_id]), reply_markup=items(chat_id))
        if weight_list[chat_id] < 1 or second == 0:
            if package.get(chat_id, False):
                bot.send_message(call.message.chat.id, 'Вот что вы взяли с собой:\n' +
                                 '\n'.join(
                                     '{}. {} x {}'.format(i + 1, FOOD[item[0]][0], item[1]) for i, item in
                                     enumerate(package[chat_id].items())))
            else:
                bot.send_message(call.message.chat.id,
                                 'Вы ничего с собой не взяли, да ты хардкорный чел')
            bot.send_message(call.message.chat.id, 'Из семьи вы взяли:\n' + '\n'.join(
                '{}. {}'.format(i + 1, item) for i, item in
                enumerate(family.get(chat_id, ['Никого, но как же так?)']))))
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
                a[call.from_user.id]['inventory'] = package[chat_id]
            save_update_to_bd(call.from_user.id)
            for i in (package, weight_list):
                if chat_id in i:
                    del i[chat_id]
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
    chat_id = call.message.chat.id
    name = call.data
    name_type = name.split('_')[0]
    if name_type == 'play':
        type = name.split('_')[1]
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if type == 'yes':
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text='Спрятаться', callback_data='play_start'))
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
            if chat_id not in weight_list:
                cur.execute("""Delete from wasteland where chat_id={}""".format(chat_id))
                cur.execute("""Delete from brother where chat_id={}""".format(chat_id))
                cur.execute("""Delete from dad where chat_id={}""".format(chat_id))
                cur.execute("""Delete from mother where chat_id={}""".format(chat_id))
                cur.execute("""Delete from saves where chat_id={}""".format(chat_id))
                cur.execute("""Delete from sister where chat_id={}""".format(chat_id))
                print('Счетчик: ' + call.from_user.username)
                weight_list[chat_id] = 100
                thread1 = Thread(target=time_cheker, args=(call, chat_id))
                thread1.start()
                time_list[chat_id] = thread1
        elif type == 'continue':
            pass
    elif name_type == 'item':
        item = FOOD[name.split('_')[1]]
        item_weight = item[2]
        item_name = item[0]
        if weight_list[chat_id] != 0:
            if weight_list[chat_id] - item_weight < 0:
                bot.answer_callback_query(callback_query_id=call.id, text='Недостаточно места')
            else:
                text = 'Мы положили в сумку: {}'
                if item[1] in ['mother', 'father', 'brother', 'sister']:
                    if item_name not in family.get(chat_id, []):
                        text = 'Вы взяли с собой в бункер: {}'
                        family[chat_id] = family.get(chat_id, []) + [item_name]
                        bot.answer_callback_query(callback_query_id=call.id, text=text.format(
                            morph(item_name)[0].inflect({'accs'}).word))
                        weight_list[chat_id] -= item_weight
                    else:
                        bot.answer_callback_query(callback_query_id=call.id,
                                                  text='Вы уже взяли этого члена семьи')
                else:
                    package[chat_id] = package.get(chat_id, {})
                    if package[chat_id].get(item[1], 0) != item[3]:
                        package[chat_id][item[1]] = package[chat_id].get(item[1], 0) + 1
                        weight_list[chat_id] -= item_weight
                        bot.answer_callback_query(callback_query_id=call.id,
                                                  text=text.format(
                                                      morph(item_name)[0].inflect({'accs'}).word))
    elif name_type == 'run':
        print(chat_id, 'убежал')
        weight_list[chat_id] = 0


try:
    bot.polling()
except Exception as e:
    bot.polling()
    print('бот упал, молодца\n', e)

