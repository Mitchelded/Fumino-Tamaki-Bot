# Twitter-Discord Bot

This is a Python application that fetches tweets from Twitter and posts them to Discord channels. It includes functionalities for translating tweets, processing tweet text, photos, and videos, as well as managing tweet IDs and channel settings.

## Features

- Fetch tweets from a specific Twitter user's timeline.
- Translate tweets from one language to another.
- Post tweets, including text, photos, and videos, to Discord channels.
- Manage tweet IDs to avoid duplicate postings.
- Support for asynchronous processing using asyncio.

## Requirements

- Python 3.x
- Required Python packages (install via `pip`):
  - `discord.py`
  - `twscrape`
  - `pytz`
  - `sqlite3`
  - `requests`

## Installation

1. Clone the repository:

  ```bash
  git clone https://github.com/Mitchelded/Fumino-Tamaki-Bot
  ```
2. Navigate to the project directory:

  ```bash
  cd Fumino-Tamaki-Bot
  ```
3. Install the required packages:

  ```bash
  pip install -r requirements.txt
  ```
4. Set up configuration:
* Create a [config.yaml](config.yaml) file containing your Discord bot token and any other configuration settings.

```bash
# Example config.yaml
  accounts:
  - username: Twitter login №1
    password: Twitter password №1
    email: Email linked to Twitter №1
    cookies:
      auth_token: auth_token cookies №1
      ct0: ct0 cookies №1
  - username: Twitter login №2
    password: Twitter password №2
    email: Email linked to Twitter №2
    cookies:
      auth_token: auth_token cookies №2
      ct0: ct0 cookies №2
  - username: Twitter login №3
    password: Twitter password №3
    email: Email linked to Twitter №3
    cookies:
      auth_token: auth_token cookies №3
      ct0: ct0 cookies №3
  # There can be as many accounts as you like
discord_bot:
  bot_token: "Your_Bot_Token"
  ```
5. Run the application:

```bash
  python discord_bot.py
  ```
## Configuration
* **config.yaml:** Contains Discord bot token and other configuration settings.
* **channels.db:** This SQLite database file stores information about Discord channels, such as their IDs and translation settings.
* **tweet_ids.db:** This SQLite database file is used to keep track of processed tweet IDs to avoid duplicate postings.
* **accounts.db:** This SQLite database by the twscrape library to store twitter account data

### **_At the moment, the password for the email and twitter account must match_**
## Usage
Once the bot is running, use Discord commands to interact with it.
Supported commands:
/ping: Display system latency and load.
/start_tweeting: Start posting tweets to the current Discord channel.
/stop_tweeting: Stop posting tweets to the current Discord channel.
/sync: Sync commands for display in the current Discord guild.
## Contributing
Contributions are welcome! If you'd like to contribute to this project, please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.