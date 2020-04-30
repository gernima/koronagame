import telebot
import time
from telebot import types
from threading import Thread, Lock
import pymorphy2
import sqlite3
from random import choice, sample
from event import events

print('start')
bot = telebot.TeleBot('1077053623:AAE8yg9jrRas7h7mTgKaNQAjOTeIsgwJHGI')
lock = Lock()
a = {0: {'inventory': {}, 'name': 'a', 'mother': 0, 'dad': 0, 'brother': 0, 'sister': 0, 'day': 1,
         'dad_bd': {'hp': 50, 'hungry': 50, 'water': 50, 'immunity': 50, 'emoji': '😕', 'weapon': ''},
         'mother_bd': {'hp': 50, 'hungry': 50, 'water': 50, 'immunity': 50, 'emoji': '😌', 'weapon': ''},
         'brother_bd': {'hp': 50, 'hungry': 50, 'water': 50, 'immunity': 50, 'emoji': '🤨', 'weapon': ''},
         'sister_bd': {'hp': 50, 'hungry': 50, 'water': 50, 'immunity': 50, 'emoji': '😔', 'weapon': ''}}}
con = sqlite3.connect("bd.db", check_same_thread=False)
cur = con.cursor()
slice_page = 20
time_list = {}
family = {}
user_list = []
weight_list = {}
wasteland_page = {}  # chat_id: num_page
morph = pymorphy2.MorphAnalyzer().parse
WEAPON_DAMAGE = {'obrez': 1}  # name: damage
FOOD = {'dad': ('Папа', 'dad', 15, 1),  # (rus_name, en_name, weight, n)
        'sister': ('Сестра', 'sister', 15, 1),
        'mother': ('Мама', 'mother', 15, 1),
        'brother': ('Брат', 'brother', 15, 1),
        'mask': ('маска', 'mask', 3, 1),
        'medicinechest': ('аптечка', 'medicinechest', 3, 1),
        'soap': ('мыло', 'soap', 3, 4),
        'obrez': ('обрез', 'obrez', 50, 1),
        'cannedfood': ('консервы', 'cannedfood', 3, 6, 50),
        'water': ('вода', 'water', 2, 6, 50)}
package = {}
things = {'dad': ('Папа', 'dad', 15, 1),  # (rus_name, en_name, weight, n, +char)
        'sister': ('Сестра', 'sister', 15, 1),
        'mother': ('Мама', 'mother', 15, 1),
        'brother': ('Брат', 'brother', 15, 1),
        'mask': ('маска', 'mask', 3, 1),
        'medicinechest': ('аптечка', 'medicinechest', 3, 1),
        'soap': ('мыло', 'soap', 3, 4),
        'obrez': ('обрез', 'obrez', 50, 1),
        'cannedfood': ('консервы', 'cannedfood', 3, 6, 50),
        'water': ('вода', 'water', 2, 6, 50),
        'vaccine': ('вакцина', 'vaccine', 2, 6, 50)}
wasteland_return = types.InlineKeyboardMarkup()
wasteland_return.add(types.InlineKeyboardButton('Назад', callback_data='wasteland_return'))

wasteland_return_from_inventory = types.InlineKeyboardMarkup()
wasteland_return_from_inventory.add(types.InlineKeyboardButton('Назад', callback_data='wasteland_return_from_inv'))


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
    elif 'bunker_weapon_' in call.data:
        splited_data = call.data.split('_')
        who = splited_data[2]
        weapon = splited_data[3]
        if weapon == 'none':
            a[call.from_user.id]['inventory'][a[call.from_user.id][who + '_bd']['weapon']] += 1
            a[call.from_user.id][who + '_bd']['weapon'] = ''
        else:
            prev_weapon = a[call.from_user.id][who + '_bd']['weapon']
            if prev_weapon != '' and prev_weapon:
                if a[call.from_user.id]['inventory'][prev_weapon]:
                    a[call.from_user.id]['inventory'][prev_weapon] += 1
                else:
                    a[call.from_user.id]['inventory'][prev_weapon] = 1
            if a[call.from_user.id]['inventory'][weapon] and a[call.from_user.id]['inventory'][weapon] - 1 > 0:
                a[call.from_user.id]['inventory'][weapon] -= 1
            else:
                del a[call.from_user.id]['inventory'][weapon]
            a[call.from_user.id][who + '_bd']['weapon'] = weapon
        cur.execute(f"""UPDATE {who} SET weapon='{a[call.from_user.id][who + '_bd']['weapon']}' where chat_id={call.from_user.id}""")
        edit_message_for_family(call, who)
        con.commit()
    elif 'weapon' in call.data:
        who = call.data.split('_')[3]
        weapons_menu = telebot.types.InlineKeyboardMarkup(row_width=3)
        weapons_menu.add(telebot.types.InlineKeyboardButton(text='Назад', callback_data='bunker_family_return'))
        weapons_menu.add(telebot.types.InlineKeyboardButton(text=f'Убрать оружие',
                                                            callback_data=f'bunker_weapon_{who}_none'))
        butts = []
        for item in a[call.from_user.id]['inventory'].keys():
            if item in WEAPON_DAMAGE.keys():
                butts.append(telebot.types.InlineKeyboardButton(text=f'{things[item][0]}-⚔{WEAPON_DAMAGE[item]}', callback_data=f'bunker_weapon_{who}_{item}'))
        for i in range(0, len(butts), 3):
            if len(butts) - i >= 3:
                weapons_menu.add(butts[i], butts[i + 1], butts[i + 2])
            elif len(butts) - i >= 2:
                weapons_menu.add(butts[i], butts[i + 1])
            else:
                weapons_menu.add(butts[i])
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                              text='Выберите чем вооружить:',
                              reply_markup=weapons_menu)
    elif call.data == 'bunker_inventory':
        send_inventory(call, wasteland_return)
    elif call.data == 'bunker_family_return':
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                              text=f'Локация: Бункер\nДень {a[call.from_user.id]["day"]}',
                              reply_markup=get_bunker_keyboard(call.from_user.id))
    elif 'bunker_next_day' in call.data:
        try:
            lock.acquire(True)
            add_wasteland_event(2, call.from_user.id)
            a[call.from_user.id]['day'] += 1
            save_update_to_bd(call.from_user.id)
            if 'wasteland' in call.data:
                bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                      text=f'Люди в пустоши ',
                                      reply_markup=get_wasteland_mans_keyboard(call.from_user.id))
                bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                      text=f'Люди в пустоши:',
                                      reply_markup=get_wasteland_mans_keyboard(call.from_user.id))
            else:
                bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                      text=f'Локация: Бункер\nДень {a[call.from_user.id]["day"]}',
                                      reply_markup=get_bunker_keyboard(call.from_user.id))
        finally:
            lock.release()
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
                a[call.from_user.id]["inventory"]["cannedfood"] -= 1
                item_zero(call.message, "cannedfood")
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


def send_inventory(call, keyboard, is_wasteland_inv=False, who=''):
    if is_wasteland_inv:
        bd_inv = cur.execute("""Select items from wasteland where who='{}' and chat_id={}""".format(who, call.from_user.id)).fetchone()[0].split(';')
        inv = {}
        if len(bd_inv) > 0 and bd_inv[0] != '':
            for i in [x.split(':') for x in bd_inv]:
                inv[i[0]] = int(i[1])
        inv_items = "\n".join([f"{things[x][0]}: {inv[x]}" for x in
                               inv.keys()])
    else:
        inv_items = "\n".join([f"{things[x][0]}: {a[call.from_user.id]['inventory'][x]}" for x in a[call.from_user.id]["inventory"].keys()])
    if not a[call.from_user.id]["inventory"].keys():
        inv_items = 'Пусто'
    bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                          text=f'Инвентарь:\n{inv_items}',
                          reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: 'event' in call.data)
def event_logic(call):
    text = call.data.split('_')
    event, button = text[1], ''.join(text[2:])
    chat_id = call.message.chat.id
    family = [i for i in ['mother', 'dad', 'brother', 'sister'] if a[chat_id][i] != 0]
    if event == 'spider':
        people = choice(family)
        people_immunity = a[chat_id][people + '_bd']['immunity']
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Назад', callback_data='wasteland_return'))
        if button == 'continue':
            for i in family:
                a[chat_id][i + '_bd']['immunity'] = max(a[chat_id][i + '_bd']['immunity'] - 20, 0)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                text='Не надо было оставлять эту проблему, все члены семьи получили психическое '
                'растройство, а так же их покусали пауки, падение иммунитета у всей семьи', reply_markup=markup)
        elif button == 'medicinechest':
            a[call.message.chat.id]['inventory']['medicinechest'] -= 1
            item_zero(call.message, 'medicinechest')
            a[chat_id][people + '_bd']['immunity'] = min(people_immunity + 10, 100)
            people = morph(FOOD[people][0])[0].inflect({"gent"}).word
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Пауки были вымешленные, вы приняли таблетки и все'
                                                   f' прошло, а у {people} прошла старая болезнь', reply_markup=markup)
        elif button == 'war':
            a[chat_id][people + '_bd']['immunity'] = max(people_immunity - 5, 0)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'Вы отбились от пауков, но один из них укусил {FOOD[people][0]}', reply_markup=markup)
    else:
        if text[2] in str(cur.execute("""Select activ_butts from events where event_id={}""".format(event)).fetchone()[0]).split(';'):
            x = cur.execute("""Select hp_plus, immunity_plus from events where event_id={}""".format(event)).fetchall()[0]
            sum_damage = 0
            for who in ['dad', 'mother', 'sister', 'brother']:
                if a[chat_id][who]:
                    who_weapon = cur.execute("""Select weapon from {} where chat_id={}""".format(who, chat_id)).fetchone()
                    if who_weapon in WEAPON_DAMAGE.keys():
                        sum_damage += WEAPON_DAMAGE[who_weapon[0]]
            need_weapon_damage = cur.execute(
                """Select need_weapon_damage from events where event_id={}""".format(event)).fetchone()[0]
            if not need_weapon_damage or need_weapon_damage == '' or need_weapon_damage == 'None':
                need_weapon_damage = 0
            if sum_damage >= int(need_weapon_damage):
                whos = cur.execute("""Select who from events where event_id={}""".format(event)).fetchone()[0].split(';')
                for who in whos:
                    minus_char(chat_id, who, x)
                res_items = items_plus_and_minus(event, a[chat_id]['inventory'], items_minus_tf=False, bd_name='events')
                a[chat_id]['inventory'] = res_items
            else:
                events_debuff(chat_id, event)
        else:
            events_debuff(chat_id, event)
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                              text=f'Локация: Бункер\nДень {a[call.from_user.id]["day"]}',
                              reply_markup=get_bunker_keyboard(call.from_user.id))


def minus_char(chat_id, who, x):
    if x[0]:
        if int(x[0]) > 0:
            a[chat_id][who + '_bd']['hp'] += max(a[chat_id][who + '_bd']['hp'] + int(x[0]), 100)
        else:
            a[chat_id][who + '_bd']['hp'] += max(a[chat_id][who + '_bd']['hp'] - int(x[0]), 0)
    if x[1]:
        if int(x[1]) > 0:
            a[chat_id][who + '_bd']['immunity'] += min(a[chat_id][who + '_bd']['immunity'] + int(x[1]), 100)
        else:
            a[chat_id][who + '_bd']['immunity'] += min(a[chat_id][who + '_bd']['immunity'] - int(x[1]), 0)


def events_debuff(chat_id, event):
    x = cur.execute("""Select hp_minus, immunity_minus from events where event_id={}""".format(event)).fetchall()[0]
    whos = str(cur.execute("""Select who from events where event_id={}""".format(event)).fetchone()[0]).split(';')
    if len(list(whos)) != 0 and whos[0] != 'None' and whos[0].strip() != '':
        for who in whos:
            if a[chat_id][who + '_bd']:
                minus_char(chat_id, who, x)
    a[chat_id]['inventory'] = items_plus_and_minus(event, a[chat_id]['inventory'], items_plus_tf=False, bd_name='events')


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
        chat_id = call.from_user.id
        if call.data == 'wasteland_return':
            if 'inv' in call.data:
                send_wasteland_logs(call, splited_data)
            else:
                bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                      text=f'Локация: Бункер\nДень {a[call.from_user.id]["day"]}',
                                      reply_markup=get_bunker_keyboard(call.from_user.id))
        elif 'inventory' in call.data:
            send_inventory(call, wasteland_return_from_inventory, True, call.data.split('_')[2])
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
            try:
                send_wasteland_logs(call, splited_data)
            except:
                bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                      text=f'Люди в пустоши:',
                                      reply_markup=get_wasteland_mans_keyboard(call.from_user.id))
        elif 'page' in call.data:
            if 'prev' in call.data:
                if wasteland_page[call.from_user.id] - 1 >= 0:
                    wasteland_page[call.from_user.id] -= 1
                    send_wasteland_logs(call, splited_data)
            else:
                q = f"""Select text from wasteland where chat_id = {call.from_user.id} and who = '{splited_data[2]}'"""
                if len([x.replace('\n', '\n') for x in con.execute(q).fetchone()[0].split(';')]) > wasteland_page[call.from_user.id] * slice_page + slice_page:
                    wasteland_page[call.from_user.id] += 1
                    send_wasteland_logs(call, splited_data)


def return_who_data(who_data):
    who = ''
    if who_data == 'dad':
        who = 'Папа'
    if who_data == 'mother':
        who = 'Мама'
    if who_data == 'sister':
        who = 'Сестра'
    if who_data == 'brother':
        who = 'Брат'
    return who


def send_wasteland_logs(call, splited_data):
    who_data = splited_data[2]
    who = return_who_data(who_data)
    q = f"""Select text from wasteland where chat_id = {call.from_user.id} and who = '{who_data}'"""
    n = wasteland_page[call.from_user.id] * slice_page
    logs = '\n'.join([x for x in con.execute(q).fetchone()[0].split(';')][n: n + slice_page])
    q = f"""Select is_return from wasteland where chat_id = {call.from_user.id} and who = '{who_data}'"""
    x = ''
    if con.execute(q).fetchone()[0]:
        q = f"""Select day_return from wasteland where chat_id = {call.from_user.id} and who = '{who_data}'"""
        x = f'Дней до возвращания: {con.execute(q).fetchone()[0] + 1}'
    bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                          text=f'{who} {a[call.from_user.id][who_data + "_bd"]["emoji"]}'
                               f'\nЗдоровье: {a[call.from_user.id][who_data + "_bd"]["hp"]}'
                               f'\nСытость: {a[call.from_user.id][who_data + "_bd"]["hungry"]}'
                               f'\nЖажда: {a[call.from_user.id][who_data + "_bd"]["water"]}'
                               f'\nИммунитет: {a[call.from_user.id][who_data + "_bd"]["immunity"]}'
                               f'\nСтраница: {wasteland_page[call.from_user.id]}\n{logs}\n\n{x}',
                          reply_markup=get_wasteland_mans_keyboard(call.from_user.id, arrows=True, who_arrow=who_data))


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


def bd_family(chat_id, data, who):
    if data:
        x = 0
        data = list(data)[1:]
        for i in a[chat_id][who + '_bd'].keys():
            a[chat_id][who + '_bd'][i] = data[x]
            x += 1


def event_run(message):
    events_bd = [x[0] for x in cur.execute("""Select event_id from events""").fetchall()]
    event = choice(events['choice'] + events['good'] + events['bad'] + events_bd)
    # event = choice(events_bd)
    markup = types.InlineKeyboardMarkup()
    package = set(list(a[message.chat.id]['inventory']))
    if [i for i in ['mother', 'dad', 'brother', 'sister'] if a[chat_id][i] != 0]:
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
            else:
                event_run(message)
        elif event == 'доставка от правительства':
            markup.add(types.InlineKeyboardButton('Назад', callback_data='wasteland_return'))
            item = choice(['water', 'medicinechest', 'cannedfood', 'soap'])
            a[message.chat.id]['inventory'][item] = a[message.chat.id]['inventory'].get(item, 0) + 1
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=f'Вы получаете помощь от правительства: {FOOD[item][0]}', reply_markup=markup)
        elif event == 'консервы просрочены':
            if 'cannedfood' in package:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton('Назад', callback_data='wasteland_return'))
                a[message.chat.id]['inventory']['cannedfood'] -= 1
                item_zero(message, 'cannedfood')
                bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Одна консерва оказалась просрочена, пришлось ее выкинуть', reply_markup=markup)
            else:
                event_run(message)
        else:
            while True:
                q = """Select choiced from events where event_id={}""".format(event)
                if not cur.execute(q).fetchone()[0]:
                    break
                else:
                    event = choice(events_bd)
            bd_events(message.chat.id, event, message)



def item_zero(message, item):
    if a[message.chat.id]['inventory'][item] == 0:
        del a[message.chat.id]['inventory'][item]


def bunker(message):
    get_data_from_bd(message.chat.id)
    bot.send_message(message.chat.id, f'Локация: Бункер\nДень {a[message.chat.id]["day"]}',
                     reply_markup=get_bunker_keyboard(message.chat.id))


def bd_events(chat_id, event_id, message):
    tf = True
    who_tf = True
    whos = cur.execute("""Select who from events where event_id={}""".format(event_id)).fetchone()[0].split(';')
    for who in whos:
        if a[chat_id][who + '_bd']:
            who_tf = False
    if who_tf:
        res_items = a[chat_id]['inventory']
        if res_items:
            res_items, tf = event_items(event_id, res_items, tf, bd_name='events')
        if tf:
            markup = types.InlineKeyboardMarkup()
            butts = []
            event_butts = str(cur.execute("""Select butts from events where event_id={}""".format(event_id)).fetchone()[0]).split(';')
            for butt in event_butts:
                butts.append(types.InlineKeyboardButton(text=str(butt), callback_data=f'event_{event_id}_{butt}'))
            markup.add(*butts)
            text = cur.execute("""Select text from events where event_id={}""".format(event_id))
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                                  text=text, reply_markup=markup)
        else:
            event_run(message)
    else:
        event_run(message)


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


def get_wasteland_mans_keyboard(chat_id, arrows=False, who_arrow=''):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=3)
    q = f"""Select who from wasteland where chat_id = {chat_id}"""
    who = con.execute(q).fetchall()
    butts = []
    keyboard.add(telebot.types.InlineKeyboardButton(text=f'Назад', callback_data='wasteland_return'))
    if arrows:
        keyboard.add(telebot.types.InlineKeyboardButton(text=f'Пред.Стр', callback_data=f'wasteland_prev_{who_arrow}_page'),
                     telebot.types.InlineKeyboardButton(text=f'След.Стр', callback_data=f'wasteland_next_{who_arrow}_page'))
    keyboard.add(telebot.types.InlineKeyboardButton(text=f'След.День', callback_data='bunker_next_day_wasteland'))
    for i in who:
        i = i[0]
        q = f"""Select is_return from wasteland where chat_id={chat_id} and who='{i}'"""
        who_wast = return_who_data(i)
        butts.append(telebot.types.InlineKeyboardButton(text=f'{who_wast} {a[chat_id][f"{i}_bd"]["emoji"]}',
                                                        callback_data=f'wasteland_family_{i}'))
        butts.append(telebot.types.InlineKeyboardButton(text='Инвентарь',
                                                        callback_data=f'wasteland_inventory_{i}'))
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

                if len(b) != 0 and b[0].strip() != '':
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
        res_items, tf = event_items(event_id, res_items, tf)
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
        x = cur.execute("""Select hp, immunity from wasteland_events where event_id={}""".format(event_id)).fetchall()[0]
        who_weapon = cur.execute("""Select weapon from {} where chat_id={}""".format(who, chat_id)).fetchone()[0]
        need_weapon_damage = cur.execute(
            """Select need_weapon_damage from wasteland_events where event_id={}""".format(event_id)).fetchone()[0]
        if need_weapon_damage and who_weapon in WEAPON_DAMAGE.keys() and WEAPON_DAMAGE[who_weapon] >= int(need_weapon_damage):
            res_items = items_plus_and_minus(event_id, res_items)
        else:
            minus_char(chat_id, who, x)
            res_items = items_plus_and_minus(event_id, res_items)
        res_items = ';'.join([f'{x}:{res_items[x]}' for x in res_items.keys()])
        cur.execute("""UPDATE wasteland SET text=?, day=?, items=? where chat_id=? and who=?""", (text, day, res_items, chat_id, who))
        if next_event_id:
            if type(next_event_id) is type(int()):
                wasteland_event_system(chat_id, who, day, next_event_id)
            else:
                wasteland_event_system(chat_id, who, day, choice(next_event_id.split(';')))


def items_plus_and_minus(event_id, res_items, bd_name='wasteland_events', items_plus_tf=True, items_minus_tf=True):
    if items_plus_tf:
        items_plus = \
            cur.execute("""Select items_plus from {} where event_id={}""".format(bd_name, event_id)).fetchone()[0]
        if items_plus and items_plus[0].strip() != '':
            items_plus = items_plus.split(';')
            if len(items_plus) > 0 and items_plus[0].strip() != '':
                for i in [x.split(':') for x in items_plus]:
                    if i[0] in res_items.keys():
                        res_items[i[0]] = int(res_items[i[0]]) + int(i[1])
                    else:
                        res_items[i[0]] = int(i[1])
    if items_minus_tf:
        items_minus = \
            cur.execute("""Select items_minus from {} where event_id={}""".format(bd_name, event_id)).fetchone()[0]
        if items_minus and items_minus[0].strip() != '':
            items_minus = items_minus.split(';')
            if len(items_minus) > 0 and items_minus[0].strip() != '':
                for i in [x.split(':') for x in items_minus]:
                    if i[0] in res_items.keys():
                        if res_items[i[0]] - int(i[1]) > 0:
                            res_items[i[0]] = int(res_items[i[0]]) - int(i[1])
                        elif res_items[i[0]] - int(i[1]) == 0:
                            del res_items[i[0]]
    return res_items


def event_items(event_id, res_items, tf=True, bd_name='wasteland_events'):
    try:
        if tf:
            items_minus = \
                cur.execute("""Select items_minus from {} where event_id={}""".format(bd_name, event_id)).fetchone()
            print('minus', items_minus)
            if items_minus:
                if items_minus and items_minus[0] != '' and items_minus[0] is not None:
                    items_minus = items_minus[0].split(';')
                    if len(items_minus) > 0 and items_minus[0].strip() != '' and items_minus[0] != 'None':
                        for i in [x.split(':') for x in items_minus]:
                            if i[0] in res_items.keys():
                                if res_items[i[0]] - int(i[1]) < 0:
                                    tf = False
                                    break
                            else:
                                tf = False
                                break
        return res_items, tf
    except Exception as e:
        print('items_minus', event_id, res_items, bd_name, e)
        return res_items, False


def next_event_items(res_items, event_id, tf, bd_name='wasteland_events'):
    res_items, tf = event_items(event_id, res_items, tf)
    if tf:
        next_event_id = \
            cur.execute("""Select next_event_id from {} where event_id={}""".format(bd_name, event_id)).fetchone()
        if next_event_id and next_event_id[0] and str(next_event_id).strip() != '' and next_event_id != 'None':
            if type(next_event_id[0]) is type(int()):
                res_items, tf = next_event_items(res_items, next_event_id[0], tf)
            else:
                next_event_id = next_event_id[0].split(';')
                for next_event_i in next_event_id:
                    res_items, tf = next_event_items(res_items, next_event_i, tf)
                    if tf is False:
                        break
    return res_items, tf


def update_family_bd(chat_id, who):
    q = """UPDATE {} SET hp = {}, hungry = {}, immunity = {}, emoji = "{}", water = {}, weapon= "{}" WHERE chat_id == {}"""
    cur.execute(q.format(who, a[chat_id][who + '_bd']['hp'], a[chat_id][who + '_bd']['hungry'],
                         a[chat_id][who + '_bd']['immunity'], a[chat_id][who + '_bd']['emoji'],
                         a[chat_id][who + '_bd']['water'], a[chat_id][who + '_bd']['weapon'], chat_id))


def create_family_bd(chat_id):
    if chat_id in [int(x[0]) for x in cur.execute("""Select chat_id from dad""").fetchall()] or \
            chat_id in [int(x[0]) for x in cur.execute("""Select chat_id from mother""").fetchall()] or \
            chat_id in [int(x[0]) for x in cur.execute("""Select chat_id from brother""").fetchall()] or \
            chat_id in [int(x[0]) for x in cur.execute("""Select chat_id from sister""").fetchall()]:
        if a[chat_id]['dad']:
            update_family_bd(chat_id, 'dad')
        if a[chat_id]['mother']:
            update_family_bd(chat_id, 'mother')
        if a[chat_id]['brother']:
            update_family_bd(chat_id, 'brother')
        if a[chat_id]['sister']:
            update_family_bd(chat_id, 'sister')
    else:
        if a[chat_id]['dad']:
            insert_bd_family(chat_id, 'dad')
        if a[chat_id]['mother']:
            insert_bd_family(chat_id, 'mother')
        if a[chat_id]['brother']:
            insert_bd_family(chat_id, 'brother')
        if a[chat_id]['sister']:
            insert_bd_family(chat_id, 'sister')
    con.commit()


def insert_bd_family(chat_id, who):
    q = """INSERT INTO {} VALUES (?, ?, ?, ?, ?, ?, ?)""".format(who)
    cur.execute(q,
                (chat_id, a[chat_id][who + '_bd']['hp'], a[chat_id][who + '_bd']['hungry'],
                 a[chat_id][who + '_bd']['water'], a[chat_id][who + '_bd']['immunity'],
                 a[chat_id][who + '_bd']['emoji'], a[chat_id][who + '_bd']['weapon']))


def get_data_from_bd(chat_id):
    if chat_id not in a.keys():
        a[chat_id] = a[0]
    q = """Select {} from {} where chat_id = {}"""
    bd_family(chat_id, cur.execute(q.format('*', 'dad', chat_id)).fetchone(), 'dad')
    bd_family(chat_id, cur.execute(q.format('*', 'mother', chat_id)).fetchone(), 'mother')
    bd_family(chat_id, cur.execute(q.format('*', 'brother', chat_id)).fetchone(), 'brother')
    bd_family(chat_id, cur.execute(q.format('*', 'sister', chat_id)).fetchone(), 'sister')
    inv = {}
    b = cur.execute(q.format('inventory', 'saves', chat_id)).fetchone()[0].split(';')
    if len(b) > 0 and b[0] != '':
        for i in [x.split(':') for x in b]:
            inv[i[0]] = int(i[1])
        a[chat_id]['inventory'] = inv
    a[chat_id]['name'] = cur.execute(q.format('name', 'saves', chat_id)).fetchone()[0]
    a[chat_id]['mother'] = cur.execute(q.format('mother', 'saves', chat_id)).fetchone()[0]
    a[chat_id]['dad'] = cur.execute(q.format('dad', 'saves', chat_id)).fetchone()[0]
    a[chat_id]['brother'] = cur.execute(q.format('brother', 'saves', chat_id)).fetchone()[0]
    a[chat_id]['sister'] = cur.execute(q.format('sister', 'saves', chat_id)).fetchone()[0]
    a[chat_id]['day'] = cur.execute(q.format('day', 'saves', chat_id)).fetchone()[0]


def edit_message_for_family(call, who=None):
    if who is None:
        who = ''
        if call.data[len('bunker_family_'):] == 'dad':
            who = 'Папа'
        elif call.data[len('bunker_family_'):] == 'mother':
            who = 'Мама'
        elif call.data[len('bunker_family_'):] == 'sister':
            who = 'Сестра'
        elif call.data[len('bunker_family_'):] == 'brother':
            who = 'Брат'
        who_bd = call.data[len('bunker_family_'):] + '_bd'
    else:
        who_bd = who + '_bd'
        who = return_who_data(who)
    family_menu = telebot.types.InlineKeyboardMarkup()
    family_menu.add(telebot.types.InlineKeyboardButton(text='Назад', callback_data='bunker_family_return'))
    family_menu.add(telebot.types.InlineKeyboardButton(text='Отправить в пустошь',
                                                       callback_data=f"wasteland_{call.data[len('bunker_family_'):]}_go"))
    family_menu.add(telebot.types.InlineKeyboardButton(text='Кормить', callback_data='bunker_family_feed'))
    family_menu.add(telebot.types.InlineKeyboardButton(text='Вооружение', callback_data=f'bunker_family_weapon_{call.data[len("bunker_family_"):]}'))
    if a[call.from_user.id][who_bd]["weapon"]:
        weapon = things[a[call.from_user.id][who_bd]["weapon"]][0] + ' ⚔' + str(WEAPON_DAMAGE[a[call.from_user.id][who_bd]["weapon"]])
    else:
        weapon = 'ничего'
    bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                          text=f'{who} {a[call.from_user.id][who_bd]["emoji"]}'
                               f'\nЗдоровье: {a[call.from_user.id][who_bd]["hp"]}'
                               f'\nСытость: {a[call.from_user.id][who_bd]["hungry"]}'
                               f'\nЖажда: {a[call.from_user.id][who_bd]["water"]}'
                               f'\nИммунитет: {a[call.from_user.id][who_bd]["immunity"]}'
                               f'\nВооружение: {weapon}',
                          reply_markup=family_menu)


def save_update_to_bd(chat_id):
    if chat_id in [int(x[0]) for x in cur.execute("""Select chat_id from saves""").fetchall()]:
        inventory = ';'.join([f'{x}:{a[chat_id]["inventory"][x]}' for x in a[chat_id]['inventory'].keys()])
        cur.execute(
            """UPDATE saves SET chat_id = ?, inventory = ?, name = ?, mother = ?, dad = ?, brother = ?, sister = ?, day = ? WHERE chat_id = ?""",
            (chat_id, inventory, a[chat_id]['name'], a[chat_id]['mother'], a[chat_id]['dad'],
             a[chat_id]['brother'], a[chat_id]['sister'], a[chat_id]['day'], chat_id))
    else:
        a[chat_id]['dad'] = 0
        a[chat_id]['sister'] = 0
        a[chat_id]['brother'] = 0
        a[chat_id]['mother'] = 0
        if family.get(chat_id, False):
            if 'Папа' in family[chat_id]:
                a[chat_id]['dad'] = 1
            if 'Сестра' in family[chat_id]:
                a[chat_id]['sister'] = 1
            if 'Брат' in family[chat_id]:
                a[chat_id]['brother'] = 1
            if 'Мама' in family[chat_id]:
                a[chat_id]['mother'] = 1
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
    family_button = {'dad': types.InlineKeyboardButton(
        text=f'{items_how_many_things_are_left(chat_id, "dad")} x Папа - 15',
        callback_data='item_dad'),
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
            # car(call.message)
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


good = types.InlineKeyboardMarkup()
good.add(types.InlineKeyboardButton(text='Хорошо', callback_data='bunker_family_return'))


@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == '1':
        bunker(message)
    elif message.text == 'Помощь новичкам':
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text='Для старта введите /start, такис образом вы начнете новую игру. '
                                   'При старте вы прячетесь в бункер, но перед этим вы собираете все вам необходимые вещи, которые понадобятся вам в выживании в бункере.\n'
                                   'В бункере вы можете просмотреть информацию по каждому взятому члену семьи, нажав по члену семьи.'
                                   'При нажатии на инвентарь вы увидете инвентарь бункера.'
                                   'Если вы нажмете на журнал, то вы получите ивент для бункера, который может что-то дать или забрать.'
                                   'Если вы захотели перейти в следующий день, то нажмите на кнопку след.день.'
                                   'Неотлемлемой частью игры является пустошь, в которой вы можете получить все необходимые '
                                   'вещи для выживания, но для этого вы должны отправить кого-то в пустошь. Сделать это вы можете нажав на члена семьи и нажать отправить в пустошь, но есть риск, ведь он или она может умереть, так что постарайтесь не убить всех)'
                                   'Отправив человека в пустошь он появится в пустоши, нажав на пустошь вы сможете увидеть что сделали ваши люди в пустоши, нажав на соответствующего человека. Вы заметите, что добавились кнопки переключения между страницами, нажав на них вы просматриваете следующие или предыдущие ивенты пустоши, которые произошли с вашим человекоа.'
                                   'Рядом с человеком есть кнопка инвентарь, в котором вы увидете инвентарь. Если вы хотите вернуть человека в бункер, то нажмите на "Вернуть в бункер", если хотите вернуть в пустошь, то "Вернуть в пустошь"',
                              reply_markup=good)


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
                if item[1] in ['mother', 'dad', 'brother', 'sister']:
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


chat_ids = [int(x[0]) for x in cur.execute("""Select chat_id from saves""").fetchall()]
if chat_ids:
    for chat_id in chat_ids:
        wasteland_page[chat_id] = 0
        get_data_from_bd(chat_id)


bot.polling()
