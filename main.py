from telegram.ext import CommandHandler
from telegram.ext import Updater
from flask import Flask, request
from telegram import Update
import logging
import json

# Local imports
from config import loadConfig
from bot import misterBot

# Configure logging
log = logging.getLogger('logger')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.DEBUG)

# Load configuration
config = loadConfig()

# Instance Telegram Bot
mybot = misterBot(config, log)


if (config["mode"] == "webhook"):
	# Webhook listener
	app = Flask(__name__)

	## Test route
	@app.route("/")
	def hello():
		return "Pay no attention to that man behind the curtain!"

	## Telegram webhook endpoint
	@app.route("/webhook", methods=["POST"])
	def tg_webhook_handler():
		update = Update.de_json(request.get_json(), mybot.bot)
		mybot.updateQueue.put(update)
		return "done"

	## Twitch webhook endpoint
	@app.route("/webhook", methods=["POST"])
	def twitch_webhook_handler():
		return "done"

	## Start Flask
	app.run(host="0.0.0.0",
			port=3000,
			debug=True, 
			use_reloader=False,
			threaded=True)