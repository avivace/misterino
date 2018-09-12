from telegram import Update
from telegram.ext import CommandHandler
from telegram.ext import Updater
from flask import Flask, request
from configSetup import loadConfig
import telegram_flask

telegramBot = telegram_flask.telegram_bot()

import logging


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					 level=logging.INFO)

logging.info('test')

## Configuration Setup
config = loadConfig()

# Dispatch and handle /start
def start(bot, update):
	bot.send_message(chat_id=0, 
		text="43!")

start_handler = CommandHandler('start', start)

telegramBot.dispatcher.add_handler(start_handler)

## Webhook listener - Flask server
app = Flask(__name__)

@app.route("/")
def hello():
	return "Pay no attention to that man behind the curtain!"

@app.route("/webhook", methods=["POST"])
def webhook_handler():
	update = Update.de_json(request.json, telegramBot.bot)
	telegramBot.dispatcher.process_update(request
		.json)
	return "done"

app.run(host="0.0.0.0",
		port=3000,
		debug=True, 
		use_reloader=False,
		threaded=True)