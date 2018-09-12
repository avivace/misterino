import telegram, logging
from telegram.ext import Dispatcher, CommandHandler

class telegram_bot:
	def __init__(self):
		self.bot = telegram.Bot(token='0')
		self.dispatcher = Dispatcher(self.bot, None, workers=0)
		self.dispatcher.add_error_handler(self.error)

	@staticmethod
	def error(bot, update, error):
		print('error')