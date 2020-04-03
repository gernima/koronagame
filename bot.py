import telebot
import sqlite3

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


print('start')

bot = telebot.TeleBot('1049041175:AAFHw6FXE2-yCv7L4sJmwg50eImuAusJOG0')
bunker1 = telebot.types.InlineKeyboardMarkup(row_width=5)
bunker1.add(telebot.types.InlineKeyboardButton(text='Папа', callback_data='bunker_dad'),
            telebot.types.InlineKeyboardButton(text='Мама', callback_data='bunker_mother'),
            telebot.types.InlineKeyboardButton(text='Брат', callback_data='bunker_brother'),
            telebot.types.InlineKeyboardButton(text='Сестра', callback_data='bunker_sister'))
bunker1.add(telebot.types.InlineKeyboardButton(text='Выход в пустошь', callback_data='bunker_wasteland'))
bunker1.add(telebot.types.InlineKeyboardButton(text='Журнал', callback_data='bunker_journal'))


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, ты написал мне /start')


@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == '1':
        bot.send_message(message.chat.id, '😕😌🤨😔', reply_markup=bunker1)


bot.polling()
