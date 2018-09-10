# Mister Notifier

> Created by [Denni Bevilacqua](https://github.com/dennib) and [Antonio Vivace](https://github.com/avivace).

Telegram bot notifying when your favorite streamers go live on Twitch.tv.


### Get started

```bash
# System dependencies
apt install python3 python3-pip python3-venv

# Get things ready
git clone git@github.com:avivace/mister-notifier.git
cd mister-notifier
python3 -m venv .
source bin/activate
pip3 install -r requirements.txt
```

You need a Telegram bot token (use [BotFather](https://t.me/BotFather)), a Twitch Client ID and a Twitch Client Secret ([register an application on the Twitch dev portal](https://dev.twitch.tv/dashboard/apps/create)).

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

You can now talk to your bot on Telegram.