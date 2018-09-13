from telegram import Update
from telegram.ext import CommandHandler
from telegram.ext import Updater
from flask import Flask, request
from configSetup import loadConfig
import logging
import json
from bot import misterBot

log = logging.getLogger('logger')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					 level=logging.INFO)

log.info('test')

## Configuration Setup
config = loadConfig()

# Telegram Bot
mybot = misterBot(config["botToken"], log)

## Webhook listener
app = Flask(__name__)

@app.route("/")
def hello():
	return "Pay no attention to that man behind the curtain!"

@app.route("/webhook", methods=["POST"])
def webhook_handler():
	update = Update.de_json(request.get_json(), mybot.bot)
	mybot.updateQueue.put(update)
	return "done"

app.run(host="0.0.0.0",
		port=3000,
		debug=True, 
		use_reloader=False,
		threaded=True)