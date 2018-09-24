from telegram.ext import Dispatcher, CommandHandler
from telegram import Bot, Update, ParseMode
from queue import Queue
from threading import Thread
import sqlite3

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
		self.dispatcher.add_handler(
			CommandHandler('show', self.show))
		self.dispatcher.add_handler(
			CommandHandler('enable', self.enable, pass_args=True))
		self.dispatcher.add_handler(
			CommandHandler('disable', self.disable, pass_args=True))

	## Commands methods
	def life(self, bot, update):
		bot.send_message(chat_id=update.message.chat_id, text='42')

	## Show method
	#  Retrieve a list of all subscriptions for current user
	def show(self, bot, update):
		# Open db connection and crate db cursor
		dbConn = sqlite3.connect('./db.sqlite')
		c = dbConn.cursor()

		# Execute a count of wantend rows
		sql = 'SELECT COUNT(*) FROM SUBSCRIPTIONS WHERE ChatID = ?'
		queryParams = (str(update.message.chat_id),)
		c.execute(sql,queryParams)

		# If we have at least one sub for current user...
		if c.fetchone()[0] > 0:
			# ...extract subscriptions from db and collect them
			# in subs variable...
			sql = 'SELECT * FROM SUBSCRIPTIONS WHERE ChatID = ?'
			c.execute(sql, queryParams)
			subs = c.fetchall()

			# Build up the message for the user with retrieved subscriptions
			message = "Here's a list of all of your subscriptions:\n"
			for sub in subs:
				streamer = sub[2]
				status = "*Active*" if sub[3] else "_Disabled_"
				message += '\n' + streamer + ': ' + status + '\n---'
		else:
			# ...otherwise warn the user he has no subscriptions yet
			message = "Sorry, it seems you have no subscriptions yet"

		# Close db connection
		dbConn.close()
		# Respond to the user with "message"
		bot.send_message(
			chat_id=update.message.chat_id, 
			text=message,
			parse_mode=ParseMode.MARKDOWN)

	## Enable method
	#  Activate a previously disabled subscription
	def enable(self, bot, update, args):
		if len(args) > 1:
			message = 'Sorry, you can enable only one streamer at a time'
			bot.send_message(chat_id=update.message.chat_id, text=message)
		else:
			streamer = args[0]

			dbConn = sqlite3.connect('./db.sqlite')
			c = dbConn.cursor()

			sql = 'SELECT Active FROM SUBSCRIPTIONS WHERE ChatID = ? AND Sub = ?'
			queryParams = (update.message.chat_id,streamer)
			c.execute(sql,queryParams)

			status = c.fetchone()[0]

			if status == 1:
				dbConn.close()
				message = 'No worries! *{}* subscription is already *Active*'\
				.format(streamer)
				bot.send_message(
					chat_id=update.message.chat_id, 
					text=message,
					parse_mode=ParseMode.MARKDOWN)
			else:
				sql = 'UPDATE SUBSCRIPTIONS SET Active = ? WHERE ChatID = ? AND Sub = ?'
				queryParams = (1,update.message.chat_id,streamer)
				c.execute(sql,queryParams)
				dbConn.commit()
				dbConn.close()

				message = "Yeeeey! *{}* subscription has been *Activated*"\
				.format(streamer)
				bot.send_message(
					chat_id=update.message.chat_id, 
					text=message,
					parse_mode=ParseMode.MARKDOWN)

	## Disable method
	#  Disable a subscription
	def disable(self, bot, update, args):
		if len(args) > 1:
			message = 'Sorry, you can disable only one streamer at a time'
			bot.send_message(chat_id=update.message.chat_id, text=message)
		else:
			streamer = args[0]

			dbConn = sqlite3.connect('./db.sqlite')
			c = dbConn.cursor()

			sql = 'SELECT Active FROM SUBSCRIPTIONS WHERE ChatID = ? AND Sub = ?'
			queryParams = (update.message.chat_id,streamer)
			c.execute(sql,queryParams)

			status = c.fetchone()[0]

			if status == 0:
				dbConn.close()
				message = 'No problem, *{}* subscription was already _Disabled_'\
				.format(streamer)
				bot.send_message(
					chat_id=update.message.chat_id,
					text=message,
					parse_mode=ParseMode.MARKDOWN)
			else:
				sql = 'UPDATE SUBSCRIPTIONS SET Active = ? WHERE ChatID = ? AND Sub = ?'
				queryParams = (0,update.message.chat_id,streamer)
				c.execute(sql,queryParams)
				dbConn.commit()
				dbConn.close()

				message = "Ok! *{}* subscription has been _Disabled_"\
				.format(streamer)
				bot.send_message(
					chat_id=update.message.chat_id,
					text=message,
					parse_mode=ParseMode.MARKDOWN)