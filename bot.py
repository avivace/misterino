from telegram.ext import Dispatcher, CommandHandler
from telegram import Bot, Update
from queue import Queue
from threading import Thread

class misterBot():
	def __init__(self, botToken, log, webhookURL=None):
		self.bot = Bot(botToken)
		self.log = log
		self.updateQueue = Queue()
		self.dispatcher = Dispatcher(self.bot, self.updateQueue)
		self.dispatcherThread = Thread(target = self.dispatcher.start,
									   name = 'dispatcher',
									   daemon= True)

		self.registerHandlers()
		self.dispatcherThread.start()
		log.info('Bot started')

	def setWebhook(self):
		self.bot.set_webhook(self.webhookURL)

	def registerHandlers(self):
		self.dispatcher.add_handler(
			CommandHandler('life', self.life))

	def life(self, bot, update):
		bot.send_message(chat_id=update.message.chat_id, text='42')