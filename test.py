import sqlite3


def save_and_update(chat_id, a):
    con = sqlite3.connect("bd.db")
    cur = con.cursor()
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


a = {1: {'chat_id': 0, 'inventory': 'a', 'name': 'a', 'mom': True, 'dad': False, 'brother': True, 'sister': False, 'immunity': 5}}
save_and_update(1, a)
