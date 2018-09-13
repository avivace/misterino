from telegram.ext import Dispatcher, CommandHandler
from telegram import Bot, Update
from queue import Queue
from threading import Thread

class misterBot():
	def __init__(self,
				 botToken,
				 log,
				 webhookURL=None):
		
		self.bot = Bot(botToken)
		self.log = log
		self.updateQueue = Queue()
		self.dispatcher = Dispatcher(self.bot, self.updateQueue)
		self.dispatcherThread = Thread(target = self.dispatcher.start,
									   name = 'dispatcher',
									   daemon= True)
		log.debug('Dispatcher spawned')
		self.registerHandlers()
		log.debug('Handlers registered')
		self.dispatcherThread.start()
		log.info('Bot started')

	def setWebhook(self):
		self.bot.set_webhook(self.webhookURL)
		log.info('Telegram webhook set')

	# Commands Handlers
	def registerHandlers(self):
		self.dispatcher.add_handler(
			CommandHandler('life', self.life))

	# Commands methods
	def life(self, bot, update):
		bot.send_message(chat_id=update.message.chat_id, text='42')