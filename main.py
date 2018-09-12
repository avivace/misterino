from telegram import Update
from telegram.ext import CommandHandler
from telegram.ext import Updater
from flask import Flask, request
from configSetup import loadConfig
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					 level=logging.INFO)

logging.info('test')

## Configuration Setup
config = loadConfig()

# Telegram Bot, polling for updates
updater = Updater(token=config["botToken"])
dispatcher = updater.dispatcher
def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Oh hello there")
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.start_polling()

## Webhook listener - Flask server
app = Flask(__name__)

@app.route("/")
def hello():
	return "Pay no attention to that man behind the curtain!"

@app.route("/webhook", methods=["POST"])
def webhook_handler():
	return "done"

app.run(host="0.0.0.0",
		port=3000,
		debug=True, 
		use_reloader=False,
		threaded=True)