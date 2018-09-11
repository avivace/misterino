from telegram.ext import CommandHandler
from telegram.ext import Updater
from jsonschema import validate, exceptions
from flask import Flask
import logging
import json
import os
import sys

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					 level=logging.INFO)

## Configuration Setup
defaultConfig = {
    'botToken': '',
    'TwitchAppClientID': '',
    'TwitchAppClientSecret': ''
}
defaultConfigFile = "config.json"
activeConfigFile = defaultConfigFile

if "-c" in sys.argv:
	if len(sys.argv) > sys.argv.index('-c') + 1:
		activeConfigFile = sys.argv[sys.argv.index('-c') + 1]
		print("Loading custom config file: " + activeConfigFile)
	else:
		sys.exit("You specified a -c flag but you didn't tell me which config fileyou want to use!\n\nExample syntax:\npython main.py -c customConfig.json\n")

if os.path.exists(activeConfigFile):
	with open('configSchema.json', 'r') as configSchemaFile:
		configSchema = json.load(configSchemaFile)

	with open(activeConfigFile, 'r') as configFile:
		try:
			config = json.load(configFile)
		except:
			sys.exit("Cannot read config file correctly")

	try:
		validate(config, configSchema)
	except exceptions.ValidationError as e:
		sys.exit("Something's wrong with your config file:\nInstance: {}\nError: {}".format(e.path[0],e.message))
else:
	if activeConfigFile	== defaultConfigFile:
		with open('config.json', 'w') as blankConfigFile:
			json.dump(defaultConfig, blankConfigFile, indent=4)
		sys.exit("Config file not found!\nI've created a blank one for you")
	else:
		sys.exit("Sorry, the config file you specified ({}) doesn't exist".format(activeConfigFile))

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