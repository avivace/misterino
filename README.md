# Mister Notifier

> Created by [Denni Bevilacqua](https://github.com/dennib) and [Antonio Vivace](https://github.com/avivace).

Telegram bot notifying when your favorite streamers go live on Twitch.tv.

### Stack

We make use of 

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot);
- [Flask](http://flask.pocoo.org/docs/1.0/api/) as webhook listener;
- [SQLite3](https://www.sqlite.org/docs.html) for persistence and multi-user experience;
- [_New_ Twitch API](https://dev.twitch.tv/docs/api/reference/);
- [Twitch Webhooks](https://dev.twitch.tv/docs/api/webhooks-reference/) to subscribe to events instead of polling for them.

### Get started

```bash
# System dependencies
apt install python3 python3-pip

# Get things ready
git clone git@github.com:avivace/mister-notifier.git
cd mister-notifier
python3 -m venv .
source bin/activate
# Python dependencies
pip3 install -r requirements.txt
```

You need a Telegram bot token (use [BotFather](https://t.me/BotFather)), a Twitch Client ID and a Twitch Client Secret (register an application on the [Twitch dev portal](https://dev.twitch.tv/dashboard/apps/create)).

Create a `config.json`:

```json
{
    "botToken": "TELGRAM_BOT_TOKEN",
    "TwitchAppClientID": "TWITCH_APP_CLIENT_ID",
    "TwitchAppClientSecret": "TWITCH_APP_CLIENT_SECRET"
}
```

With the mentioned values.


Start the bot

```bash
python3 main.py
```

If the script can't find `config.json`, it'll create a default one for you.

You can specify the configuration file to use using `python3 main.py -c config2.json`.

Bot is up and running, talk to it on Telegram.