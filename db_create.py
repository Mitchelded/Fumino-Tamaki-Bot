import sqlite3


def create_tweet_id_table():
    conn = sqlite3.connect('tweet_ids.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS used_tweet_ids
                 (tweet_id TEXT PRIMARY KEY)''')
    conn.commit()
    conn.close()


def create_channels_table():
    conn = sqlite3.connect('channels.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS channels (
                      channel_id INTEGER PRIMARY KEY,
                      guild_id INTEGER NOT NULL,
                      translate INTEGER NOT NULL)''')
    conn.commit()
    conn.close()