import asyncio
from twscrape import API
from datetime import datetime, timedelta
import pytz
import sqlite3
import yaml
import db_create
import os

async def tweet_text_processing(user_id, limit=-1, raw=False):
    api = API()
    processed_tweet_ids = set()
    new_tweets = []  # List to store rawContent of new tweets

    last_tweet_date_moscow = datetime.now(pytz.timezone('Europe/Moscow')) - timedelta(days=1)
    last_tweet_date_utc = last_tweet_date_moscow.astimezone(pytz.utc)
    if raw:
        async for tweet in api.user_tweets(user_id, limit):
            tweet_date_utc = tweet.date.astimezone(pytz.utc)
            if tweet.id not in processed_tweet_ids and tweet_date_utc > last_tweet_date_utc:
                new_tweets.append(tweet)
                processed_tweet_ids.add(tweet.id)
        return new_tweets
    else:
        async for tweet in api.user_tweets(user_id, limit):
            tweet_date_utc = tweet.date.astimezone(pytz.utc)
            if tweet.id not in processed_tweet_ids and tweet_date_utc > last_tweet_date_utc:
                new_tweets.append(tweet.rawContent)
                processed_tweet_ids.add(tweet.id)
        return new_tweets


async def tweet_text_processing_db(user_id, limit=-1, raw=False):
    api = API()
    processed_tweet_ids = set()
    new_tweets = []  # List to store rawContent of new tweets
    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'tweet_ids.db')):
        db_create.create_tweet_id_table()
    # Connect to the database
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'tweet_ids.db'))
    c = conn.cursor()

    last_tweet_date_moscow = datetime.now(pytz.timezone('Europe/Moscow')) - timedelta(days=1)
    last_tweet_date_utc = last_tweet_date_moscow.astimezone(pytz.utc)

    async for tweet in api.user_tweets(user_id, limit):
        tweet_date_utc = tweet.date.astimezone(pytz.utc)
        if tweet.id not in processed_tweet_ids and tweet_date_utc > last_tweet_date_utc:
            # Check if the tweet ID exists in the database
            c.execute("SELECT * FROM used_tweet_ids WHERE tweet_id=?", (tweet.id,))
            result = c.fetchone()
            if result is None:
                processed_tweet_ids.add(tweet.id)
                # If not, insert it into the database
                c.execute("INSERT INTO used_tweet_ids (tweet_id) VALUES (?)", (tweet.id,))
                conn.commit()
                if raw:
                    new_tweets.append(tweet)
                else:
                    new_tweets.append(tweet.rawContent)

    # Close database connection
    conn.close()
    print(f"Success {datetime.now()}")
    return new_tweets


async def tweet_photo_processing(user_id, limit=-1):
    api = API()  # Ваш экземпляр API
    processed_tweet_ids = set()
    new_photos_urls = []  # Список для хранения ссылок на новые фотографии

    # Определение даты последнего твита (1 день назад по Московскому времени)
    last_tweet_date_moscow = datetime.now(pytz.timezone('Europe/Moscow')) - timedelta(days=1)
    last_tweet_date_utc = last_tweet_date_moscow.astimezone(pytz.utc)

    async for tweet in api.user_tweets(user_id, limit):
        tweet_date_utc = tweet.date.astimezone(pytz.utc)
        if tweet.id not in processed_tweet_ids and tweet_date_utc > last_tweet_date_utc:
            if tweet.media and tweet.media.photos:
                for photo in tweet.media.photos:
                    new_photos_urls.append(photo.url)
            processed_tweet_ids.add(tweet.id)
    return new_photos_urls


async def tweet_video_processing(user_id, limit=-1, ):
    api = API()  # Ваш экземпляр API
    processed_tweet_ids = set()
    new_video_urls = []  # Список для хранения ссылок на новые видео

    # Определение даты последнего твита (1 день назад по Московскому времени)
    last_tweet_date_moscow = datetime.now(pytz.timezone('Europe/Moscow')) - timedelta(days=1)
    last_tweet_date_utc = last_tweet_date_moscow.astimezone(pytz.utc)

    async for tweet in api.user_tweets(user_id, limit):
        tweet_date_utc = tweet.date.astimezone(pytz.utc)
        if tweet.id not in processed_tweet_ids and tweet_date_utc > last_tweet_date_utc:
            if tweet.media and tweet.media.videos:
                for video in tweet.media.videos:
                    new_video_urls.append(video.url)
            processed_tweet_ids.add(tweet.id)
    return new_video_urls


async def main():
    api = API(os.path.join(os.path.dirname(__file__), 'accounts.db'))  # or API("path-to.db") - default is `accounts.db`

    with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'r') as file:
        accounts_data = yaml.safe_load(file)

    accounts = accounts_data.get('accounts', [])
    cookies_list = []

    # Создаем список куки для каждого аккаунта
    for account in accounts:
        cookies = (f"auth_token={account['cookies']['auth_token']}; "
                   f"ct0={account['cookies']['ct0']}")
        cookies_list.append(cookies)

    # Добавляем аккаунты в пул и выполняем вход
    for i, account in enumerate(accounts):
        await api.pool.add_account(account.get('username'), account.get('password'), account.get('email'),
                                   account.get('password'),
                                   cookies=cookies_list[i])

    await api.pool.login_all()

    user_id = 971925378913611776  # nekokan_chu

    new_tweets = await tweet_text_processing_db(user_id, 1, True)

    print(new_tweets)


if __name__ == "__main__":
    asyncio.run(main())
