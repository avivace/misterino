from telegram.ext import CommandHandler
from telegram.ext import Updater
from flask import Flask, request
from telegram import Update
import logging
import json
import sqlite3

# Local imports
from config import loadConfig
from bot import misterBot

# Configure logging
log = logging.getLogger('logger')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.DEBUG)

# Load configuration
config = loadConfig()

# Initialise Sqlite database
dbConn = sqlite3.connect('./db.sqlite', check_same_thread=False)
# Beware that we will commit changes from two threads:
#  Flask (in the Twitch webhook) and the Dispatcher (in command Handlers)
#  sqlite should simply put in wait in case of concurrent writes.

# Instance Telegram Bot
#mybot = misterBot(config, log, dbConn)

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
	return "done", 200

# Confirm Event sub/unsub
@app.route("/tw-webhook", methods=["GET"])
def confirm_wh():
	challenge = request.args.get('hub.challenge')
	print("Confirming ", challenge)
	return challenge, 200

## Start Flask
app.run(host="0.0.0.0",
		port=3000,
		debug=True, 
		use_reloader=False,
		threaded=True)
