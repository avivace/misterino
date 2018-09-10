from telegram.ext import CommandHandler
from telegram.ext import Updater
from jsonschema import validate
from flask import Flask
import logging
import json

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					 level=logging.INFO)

with open('configSchema.json', 'r') as configSchemaFile:
	configSchema = json.load(configSchemaFile)

with open('config.json', 'r') as configFile:
	config = json.load(configFile)

validate(config, configSchema)

## Telegram Bot
updater = Updater(token=config["botToken"])

dispatcher = updater.dispatcher

# Dispatch and handle /start
def start(bot, update):
	bot.send_message(chat_id=update.message.chat_id, 
		text="42!")

start_handler = CommandHandler('life', start)
dispatcher.add_handler(start_handler)

# Run the bot
updater.start_polling()

## Webhook listener - Flask server
app = Flask(__name__)

@app.route("/")
def hello():
	return "Pay no attention to that man behind the curtain!"

app.run(host="0.0.0.0",
		port=3000,
		debug=True, 
		use_reloader=False,
		threaded=True)