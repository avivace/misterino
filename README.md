# <img src="logo.png" alt="misterino" width="250px"/>

> Developed by [Denni Bevilacqua](https://github.com/dennib) and [Antonio Vivace](https://github.com/avivace).

Telegram bot notifying when your favorite streamers go live on Twitch.tv. Users can subscribe to Twitch streamers and receive a message when they go online (privately or in a group).

The telegram bot can function in `polling` or in `webhook` mode. Those modes are idem-potent and you *should* see the same results and behaviours.

### Stack

We make use of 

- [_New_ Twitch API](https://dev.twitch.tv/docs/api/reference/);
- [Twitch Webhooks](https://dev.twitch.tv/docs/api/webhooks-reference/) to subscribe to events instead of polling for them.
- [Flask](http://flask.pocoo.org/docs/1.0/api/) as webhook listener;
- [SQLite3](https://www.sqlite.org/docs.html) for persistence and multi-user experience;
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot);

#### Webhook mode

The bot was developed to work in `webhook` (this is also why it _may_ seem over-engineered). Please understand that the webhook mode requires additional work and maintenance. You need:

- A public IP address or domain;
- A SSL certificate;
- A webhook listener;
- A reverse proxy exposing the webhook listener.

We don't use the python-telegram-bot integrated webserver, but we listen for webhooks with Flask, then we dispatch the de-jsonified (is this even a word?) payloads to another thread, using a shared Queue.

During development, we use the polling mode to get the payload from messages sent to the bot, then pipe them to `webhookTest.sh` to simulate the Telegram server sending webhook to our listener.

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

Create a `config.json` with the mentioned values:

```json
{
    "mode": "polling",
    "botToken": "TELGRAM_BOT_TOKEN",
    "TwitchAppClientID": "TWITCH_APP_CLIENT_ID",
    "TwitchAppClientSecret": "TWITCH_APP_CLIENT_SECRET"
}
```

Start the bot

```bash
python3 main.py
```

If the script can't find `config.json`, it'll create a default one for you.

You can specify the configuration file to use using `python3 main.py -c config2.json`.

Bot is up and running, talk to it on Telegram.
