# Twitter Scraper

This project is an asynchronous Python script for extracting data from Twitter using the twscrape library. With this script, you can retrieve text tweets, images, and videos from a Twitter user's timeline.

## Installation

1. Install the dependencies by running the following command:

   ```bash
   pip install -r requirements.txt
Ensure you have active Twitter API credentials.

Create a configuration file config.yaml containing the credentials required to access the Twitter API. An example configuration can be found in config.example.yaml.

Create the SQLite database tweet_ids.db, which will be used to store processed tweet IDs to avoid duplication.

Usage
Run the main.py script to fetch data from Twitter. The script retrieves text tweets with the option to save processed IDs in the database to prevent duplication. Separate functions are used for fetching images and videos.

bash
Copy code
python main.py
Additional Information
This project uses the twscrape library for interacting with the Twitter API.
To configure extraction parameters and other settings, edit the config.yaml file.
Please ensure that your use of this script complies with the Twitter API usage rules and does not violate them.
css
Copy code

This `README.md` file provides installation instructions, usage guidelines, and additional information about the project in English, using Markdown syntax. It offers users a clear description of how to use your script to extract data from Twitter.




