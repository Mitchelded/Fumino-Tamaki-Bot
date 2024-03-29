import sqlite3
import discord
from discord.ext import commands
import re
import translate_tweets
import twitter_scrapper
import asyncio
import psutil
import time
import yaml
import db_create
import os
import subprocess

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)
channel_id = None
tweet_loop_task = None
is_tweeting = True


@bot.hybrid_command(name="ping",
                    description="Показать задержку и нагрузку системы")
async def ping(ctx):
    # Measure latency
    start_time = time.time()
    message = await ctx.send("Pinging...")
    end_time = time.time()
    latency = (end_time - start_time) * 1000  # Latency in milliseconds
    # System load
    cpu_load = psutil.cpu_percent()
    mem_load = psutil.virtual_memory().percent

    # Send ping message with latency and system load
    await message.edit(content=f"Pong! Latency: {int(latency)}ms | CPU Load: {cpu_load}% | Memory Load: {mem_load}%")


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)
    # Check if tweet_loop was active before bot restart, and restart it if necessary
    global is_tweeting
    if is_tweeting:
        await asyncio.create_task(tweet_loop())
    await asyncio.create_task(auto_update())


@bot.hybrid_command(name="sync",
                    description="Синхронизировать команды для их отображения")
async def sync(ctx: commands.Context):
    try:
        await bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"Synced commands")
    except Exception as e:
        print(e)


@bot.hybrid_command(name="start_tweeting",
                    description="Установить id канала и начать постить твиты в канале, в котором была вписана команда")
async def start_tweeting(ctx: commands.Context, translate: bool = False):
    # Check if the command is invoked by an administrator
    if ctx.message.author.guild_permissions.administrator:
        global tweet_loop_task, is_tweeting

        channel = ctx.channel  # Get the channel where the command was invoked
        if not os.path.exists(os.path.join(os.path.dirname(__file__), 'channels.db')):
            db_create.create_channels_table()
        # Store channel ID and translation settings in the database
        conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'channels.db'))
        cursor = conn.cursor()

        # Check if there's an existing record for this channel
        cursor.execute("SELECT * FROM channels WHERE channel_id = ?", (channel.id,))
        existing_channel = cursor.fetchone()
        if existing_channel:
            # Update the existing record
            cursor.execute("UPDATE channels SET translate = ? WHERE channel_id = ?",
                           (int(translate), channel.id))
        else:
            # Insert a new record
            cursor.execute("INSERT INTO channels (channel_id, guild_id, translate) VALUES (?, ?, ?)",
                           (channel.id, ctx.guild.id, int(translate)))

        conn.commit()
        conn.close()
        is_tweeting = True
        # Start the tweet loop task
        tweet_loop_task = asyncio.create_task(tweet_loop(translate))
        await ctx.send('Tweet loop started successfully!')
    else:
        await ctx.send('You do not have permission to use this command.')


@bot.hybrid_command(name="stop_tweeting",
                    description="Удалить id канала и перестать постить твиты в канале, в котором была вписана команда")
async def stop_tweeting(ctx: commands.Context):
    # Check if the command is invoked by an administrator
    if ctx.message.author.guild_permissions.administrator:
        global tweet_loop_task

        channel = ctx.channel  # Get the channel where the command was invoked
        if not os.path.exists(os.path.join(os.path.dirname(__file__), 'channels.db')):
            db_create.create_channels_table()
        # Store channel ID and translation settings in the database
        conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'channels.db'))
        cursor = conn.cursor()

        # Delete the record for this channel, if it exists
        cursor.execute("DELETE FROM channels WHERE channel_id = ?", (channel.id,))

        conn.commit()
        conn.close()
        await ctx.send('Tweet loop stopped successfully!')
    else:
        await ctx.send('You do not have permission to use this command.')


async def send_tweet_to_discord(tweet):
    # Load the channel IDs and translation settings from the database
    global content
    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'channels.db')):
        db_create.create_channels_table()
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'channels.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT channel_id, translate FROM channels")
    channels_info = cursor.fetchall()
    conn.close()
    print(tweet)
    for channel_info in channels_info:
        channel_id_from_info, translate = channel_info
        channel = bot.get_channel(channel_id_from_info)
        if not channel:
            print(f"Channel with ID {channel_id} not found.")
            continue

        cleaned_raw_content = re.sub(r'https://t.co/\w+', '', tweet.rawContent)

        content_prefix1 = "@everyone 🎉 **Новый твит от"
        content_prefix2 = "@everyone nekokan_chu ретвитнула"
        if tweet.user.username == "nekokan_chu" and "RT" not in tweet.rawContent:
            content = f"{content_prefix1} {tweet.user.username}:\n\n*\"{cleaned_raw_content}\"*\n\n"
        elif "RT" in tweet.rawContent:
            content = f"{content_prefix2}:\n\n*\"{cleaned_raw_content.replace("RT", "")}\"*\n\n"
        if len(tweet.links) > 0:
            content += f"Cсылки из твита: "
            for link in tweet.links:
                content += f"{link.url}\n"
        # Include quoted tweet content if available
        if tweet.quotedTweet is not None:
            quoted_raw_content = re.sub(r'https://t.co/\w+', '', tweet.quotedTweet.rawContent)
            content += f"**Цитата:**\n\n*\"{quoted_raw_content}\"*\n\n"
            if len(tweet.quotedTweet.links) > 0:
                content += f"Cсылки из Цитаты: "
                for link in tweet.quotedTweet.links:
                    content += f"{link.url}\n"
        if tweet.retweetedTweet is not None:
            if len(tweet.retweetedTweet.links) > 0:
                content += f"Cсылки из ретвита: "
                for link in tweet.retweetedTweet.links:
                    content += f"{link.url}\n"

        if translate:
            content = translate_tweets.translate_language("ja", "ru", content)

        media_urls = []
        for media in tweet.media.photos + tweet.media.videos:
            if media:
                if hasattr(media, 'type') and media.type != 'photo':
                    media_urls.append(media.url)
                elif not hasattr(media, 'type'):
                    media_urls.append(media.url)

        content += "\n".join(media_urls)

        await channel.send(content)


async def tweet_loop(translate=False):
    while True:
        try:
            # Fetch the tweet using twitter_scrapper_test
            tweets = await twitter_scrapper.tweet_text_processing_db(971925378913611776, 1, True)
            for tweet in tweets:
                await send_tweet_to_discord(tweet)
                if translate:
                    await send_tweet_to_discord(tweet)

        except Exception as e:
            print(f"An error occurred: {e}")

        # Sleep for 1 hour before sending the next tweet
        await asyncio.sleep(1800)


async def auto_update():
    while True:
        try:
            # Run git pull command to update the bot code
            subprocess.run(["git", "pull", "https://github.com/Mitchelded/Fumino-Tamaki-Bot.git", "master"])
            print("Bot code updated successfully!")
        except Exception as e:
            print(f"An error occurred during auto-update: {e}")

        # Sleep for 24 hours before checking for updates again
        await asyncio.sleep(86400)  # 24 hours in seconds


with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'r') as file:
    discord_data = yaml.safe_load(file)

discord_bot = discord_data.get('discord_bot', [])
token = discord_bot.get('bot_token')
bot.run(token)
