import telebot
import time
from telebot import types
from threading import Thread
import pymorphy2
import sqlite3
from random import choice, random
from event import events

bot = telebot.TeleBot('1077053623:AAE8yg9jrRas7h7mTgKaNQAjOTeIsgwJHGI')
print('start')


return_family_menu = telebot.types.InlineKeyboardMarkup(row_width=1)
return_family_menu.add(
    telebot.types.InlineKeyboardButton(text='Назад', callback_data='bunker_family_return'),
    telebot.types.InlineKeyboardButton(text='Покормить', callback_data='bunker_family_feed')
    )
a = {0: {'inventory': [], 'name': 'a', 'mother': 1, 'dad': 1, 'brother': 1, 'sister': 1, 'day': 1,
         'dad_bd': {'mood': 50, 'hungry': 50, 'water': 50, 'immunity': 50, 'emoji': '😕'},
         'mother_bd': {'mood': 50, 'hungry': 50, 'water': 50, 'immunity': 50, 'emoji': '😌'},
         'brother_bd': {'mood': 50, 'hungry': 50, 'water': 50, 'immunity': 50, 'emoji': '🤨'},
         'sister_bd': {'mood': 50, 'hungry': 50, 'water': 50, 'immunity': 50, 'emoji': '😔'}}}

con = sqlite3.connect("bd.db", check_same_thread=False)
cur = con.cursor()
time_list = {}
family = {}
user_list = []
weight_list = {}
morph = pymorphy2.MorphAnalyzer().parse
FOOD = {'father': ('Папа', 'father', 15, 1),
        'daughter': ('Дочь', 'daughter',15, 1),
        'mother': ('Мама', 'mother', 15, 1),
        'son': ('Сын', 'son', 15, 1),
        'mask': ('маска', 'mask', 3, 1),
        'medicinechest': ('аптечка', 'medicinechest', 3, 1),
        'soap': ('мыло', 'soap', 3, 1),
        'obrez': ('обрез', 'obrez', 50, 1, 1),
        'cannedfood': ('консервы', 'cannedfood', 3, 6, 50),
        'water': ('вода', 'water', 2, 6, 50)}
package = {}


def bd_family(chat_id, data):
    x = 0
    for i in a[chat_id]['dad_bd'].keys():
        a[chat_id][i] = data[x]
        x += 1


def event_run(event, message):
    if event == 'пауки в бункере':
        bot.send_message(message.chat.id, 'Это безумие! Мы постоянно находим пауков. Они в нашем '
                                          'супе. Они в нашей воде. Мы клянемся, что некоторые из них продолжают возвращаться, и они'
                                          ' становятся больше с каждым разом, когда мы их видим! Так продолжаться не может. Пришло '
                                          'время вести войну с этими пауками!')
        markup.add(
            types.InlineKeyboardButton(text='Взять', callback_data='event_canned_food_get'),
            types.InlineKeyboardButton(text='Выбросить', callback_data='event_canned_food_delete'),
            types.InlineKeyboardButton(text='Надеть всем', callback_data='event_canned_food_put_on'))
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

        a[chat_id]['inventory'] = str(
            cur.execute(q.format('inventory', 'saves', chat_id)).fetchone()[0]).split(';')
        a[chat_id]['name'] = cur.execute(q.format('name', 'saves', chat_id)).fetchone()[0]
        a[chat_id]['mother'] = cur.execute(q.format('mother', 'saves', chat_id)).fetchone()[0]
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
    if a[chat_id]['mother']:
        butts.append(
            telebot.types.InlineKeyboardButton(text=f'Мама {a[chat_id]["mother_bd"]["emoji"]}',
                                               callback_data='bunker_family_mother'))
    if a[chat_id]['brother']:
        butts.append(
            telebot.types.InlineKeyboardButton(text=f'Брат {a[chat_id]["brother_bd"]["emoji"]}',
                                               callback_data='bunker_family_brother'))
    if a[chat_id]['brother']:
        butts.append(
            telebot.types.InlineKeyboardButton(text=f'Сестра {a[chat_id]["sister_bd"]["emoji"]}',
                                               callback_data='bunker_family_sister'))
    bunker.add(*butts)
    bunker.add(telebot.types.InlineKeyboardButton(text='Журнал', callback_data='bunker_journal'),
               telebot.types.InlineKeyboardButton(text='Инвентарь', callback_data='bunker_inventory'))
    bunker.add(
        telebot.types.InlineKeyboardButton(text='Выход в пустошь', callback_data='bunker_wasteland'),
        telebot.types.InlineKeyboardButton(text='Следующий день', callback_data='bunker_next_day'))

    return bunker


def create_family_bd(chat_id):
    if cur.execute("""Select chat_id from dad where chat_id == {}""".format(chat_id)).fetchone():
        cur.execute(
            """UPDATE dad SET chat_id = ?, mood = ?, hungry = ?, water = ? immunity = ? emoji = ? WHERE chat_id == ?""",
            (chat_id, a[chat_id]['dad_bd']['mood'], a[chat_id]['dad_bd']['hungry'],
             a[chat_id]['dad_bd']['water'],
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
                     a[chat_id]['dad_bd']['water'], a[chat_id]['dad_bd']['immunity'],
                     a[chat_id]['dad_bd']['emoji']))
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
            car(call.message)
            bunker(call.message)
            # a[call.from_user.id] = a[0]
            # a[call.from_user.id]['inventory'] = package[user]
            # save_update_to_bd(call.from_user.id)
            print(package)
            for i in (package, weight_list, family):
                if user in i:
                    del i[user]
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
        except Exception as e:
            pass
    elif call.data == 'bunker_family_feed':
        name = call.message.text.split("\n")[0]
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(text='Назад', callback_data='bunker_family_return'),
                   types.InlineKeyboardButton(text=f'{1} x Консервы + 50 сытости', callback_data=f'bunker_food_cannedfood_{name}'),
                   types.InlineKeyboardButton(text=f'{1} x Вода + 50 вода', callback_data=f'bunker_food_water_{name}'))
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
    elif 'food' in call.data:
        name_ = call.data.split('_')[-1]
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
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{name_}'
                                f'\nНастроение: {a[call.from_user.id][name]["mood"]}'
                               f'\nСытость: {a[call.from_user.id][name]["hungry"]}'
                               f'\nЖажда: {a[call.from_user.id][name]["water"]}'
                               f'\nИммунитет: {a[call.from_user.id][name]["immunity"]}', reply_markup=markup)
    elif call.data == 'bunker_journal':
        chance = random()
        if chance < .4:
            event = choice(events['good'])
        elif .5 > chance > .4:
            event = choice(events['bad'])
        else:
            event = choice(events['choice'])
        event_run(event, call.message)


@bot.callback_query_handler(func=lambda call: 'event' in call.data)
def event_logic(call):
    event_type = call.data[6:]
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if event_type == 'canned_food_get':
        bot.send_message(call.message.chat.id, 'вы взяли маски')
    if event_type == 'canned_food_delete':
        bot.send_message(call.message.chat.id, 'вы выбросили маски')
    if event_type == 'canned_food_put_on':
        bot.send_message(call.message.chat.id,
                         'вы одели маски, они оказались чем то заразны у всей семьи падает иммунитет')


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    global weight_list
    user = call.from_user.username
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
    print('бот упал, молодца\n', e)
