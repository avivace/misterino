from telegram.ext import CommandHandler
from telegram.ext import Updater
from flask import Flask, request
from telegram import Update, ParseMode
from twitch import twitch
import logging
import json
import sqlite3
import os

# Local imports
from config import loadConfig
from bot import misterBot

# Configure logging
log = logging.getLogger('logger')
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING)

# Load configuration
config = loadConfig()

if not os.path.isfile('db.sqlite'):
    logging.WARNING("Initialising database with the default tables")
    dbConn = sqlite3.connect('./db.sqlite', check_same_thread=False)
    c = dbConn.cursor()
    c.execute("CREATE TABLE `SUBSCRIPTIONS` ( `ChatID` TEXT, `Sub` TEXT, `Active` TEXT )")
    c.execute("CREATE TABLE `WEBHOOKS` ( `Topic` TEXT, `Expires` TEXT )")
else:
    dbConn = sqlite3.connect('./db.sqlite', check_same_thread=False)


# Beware that we will commit changes from two threads:
#  Flask (in the Twitch webhook) and the Dispatcher (in command Handlers)
#  sqlite should simply put in wait in case of concurrent writes.

twitch = twitch(config)

# Instance Telegram Bot
mybot = misterBot(config, log, dbConn, twitch)

# Webhook listener, Flask
app = Flask(__name__)


## Test route
@app.route("/")
def hello():
    return "Pay no attention to that man behind the curtain!"


if (config["mode"] == "webhook"):
    ## Telegram webhook endpoint
    @app.route("/tg-webhook", methods=["POST"])
    def tg_webhook_handler():
        update = Update.de_json(request.get_json(), mybot.bot)
        mybot.updateQueue.put(update)
        return "done"


## Twitch webhook endpoint
@app.route("/tw-webhook", methods=["POST"])
def twitch_webhook_handler():
    data = json.loads(request.data)
    username = data["data"][0]["user_name"]
    title = data["data"][0]["title"]
    url = "https://twitch.tv/"+username
    c = dbConn.cursor()
    queryParams = (username, )
    sql = 'SELECT * FROM SUBSCRIPTIONS WHERE Sub=?'
    result = c.execute(sql, queryParams)
    for row in result:
        subscriber = row[0]
        text='*{}* è live su Twitch! _{}_ \n{}'.format(username, title, url)
        mybot.bot.send_message(chat_id=subscriber, text=text, parse_mode=ParseMode.MARKDOWN)
    return "done", 200


# Confirm Event sub/unsub
# Sets up Twitch webhooks (Phase 2)
@app.route("/tw-webhook", methods=["GET"])
def confirm_wh():
    challenge = request.args.get('hub.challenge')
    print("Confirming ", challenge)
    return challenge, 200

"""
Syncs the actual (active) webhook subscriptions to our table
"""
def updateWebhooksTable():
    webhooks = twitch.listWebhooks()
    for webhook in webhooks['data']:
        print(webhook)
    return True


## Start Flask
app.run(
    host="0.0.0.0", port=3000, debug=True, use_reloader=False, threaded=True)
