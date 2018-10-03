from telegram.ext import Dispatcher, CommandHandler, Updater
from telegram import Bot, Update, ParseMode
from queue import Queue
from threading import Thread
import sqlite3

class misterBot():

	def __init__(self,
				 config,
				 log,
				 webhookURL=None):
		botToken = config["botToken"]
		if config["mode"] == "polling":
			self.pollingInit(botToken,
							 log)
		elif config["mode"] == "webhook":
			self.webhookInit(botToken,
							 log)
	
	def pollingInit(self,
					botToken,
					log):
		self.updater = Updater(token=botToken)
		self.dispatcher = self.updater.dispatcher
		self.registerHandlers()
		self.updater.start_polling()


	def webhookInit(self,
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
			CommandHandler('sub', self.sub, pass_args=True))
		self.dispatcher.add_handler(
			CommandHandler('unsub', self.unsub, pass_args=True))
		self.dispatcher.add_handler(
			CommandHandler('enable', self.enable, pass_args=True))
		self.dispatcher.add_handler(
			CommandHandler('disable', self.disable, pass_args=True))

	### Commands methods
	def life(self, bot, update):
		bot.send_message(chat_id=update.message.chat_id, text='42')

	## Sub method
	#  Add a subscription for current user given a twitch username
	def sub(self, bot, update, args):
		# Check if we received the correct, allowed, number of subscriptions
		# to subscribe to (1 atm)
		if len(args) > 1:
			message = 'Sorry, you can subscribe only to one streamer at a time'
			bot.send_message(chat_id=update.message.chat_id, text=message)
		elif len(args) < 1:
			message = 'Sorry, you must provide one valid twitch username '\
 					+ 'you want to subscribe to.\n\n'\
 					+ 'Please try again with something like\n'\
 					+ '_/sub streamerUsername_'
			bot.send_message(chat_id=update.message.chat_id,
							 text=message,
							 parse_mode=ParseMode.MARKDOWN)
		else:
			streamer = args[0]
			# Open db connection and create db cursor	
			dbConn = sqlite3.connect('./db.sqlite')
			c = dbConn.cursor()
			queryParams = (update.message.chat_id,streamer)
			# Check if requested subscription already exits in db
			sql = 'SELECT COUNT(*) FROM SUBSCRIPTIONS WHERE ChatID=? AND Sub=?'
			c.execute(sql,queryParams)
			found = c.fetchone()[0]
			# If it doesn't exit yet...
			if not found:
				# ... Add it to db and...
				sql = '''INSERT INTO SUBSCRIPTIONS (ChatID,Sub,Active)
						 VALUES (?,?,?)'''
				queryParams = (update.message.chat_id,streamer,1)
				c.execute(sql, queryParams)
				dbConn.commit()
				#... Notify the user
				bot.send_message(chat_id=update.message.chat_id,
								 text='Yeeey! you\'ve successfully subscribed to *{}*!'\
								 	.format(streamer),
								 parse_mode=ParseMode.MARKDOWN)
			else:
				# Otherwise warn the user that subscription is already existent
				bot.send_message(chat_id=update.message.chat_id,
								 text='Don\'t worry! You are already subscribed to '\
								 	+ '*{}*'.format(streamer),
								 parse_mode=ParseMode.MARKDOWN)
			dbConn.close()

	## Unsub method
	#  Delete a subscription for current user given a twitch username
	def unsub(self, bot, update, args):
		# Check if we received the correct, allowed, number of subscriptions
		# to unsubscribe from (1 atm)
		if len(args) > 1:
			message = 'Sorry, you can unsubscribe only from one streamer at a time'
			bot.send_message(chat_id=update.message.chat_id, text=message)
		elif len(args) < 1:
			message = 'Sorry, you must provide one valid twitch username '\
 					+ 'you want to unsubscribe from.\n\n'\
 					+ 'Please try again with something like\n'\
 					+ '_/unsub streamerUsername_'
			bot.send_message(chat_id=update.message.chat_id,
							 text=message,
							 parse_mode=ParseMode.MARKDOWN)
		else:
			streamer = args[0]
			# Open db connection and create db cursor	
			dbConn = sqlite3.connect('./db.sqlite')
			c = dbConn.cursor()
			queryParams = (update.message.chat_id,streamer)
			# Check if requested subscription already exits in db
			sql = 'SELECT COUNT(*) FROM SUBSCRIPTIONS WHERE ChatID=? AND Sub=?'
			c.execute(sql,queryParams)
			found = c.fetchone()[0]
			# If it exits...
			if found:
				# ... Delete it and...
				sql = 'DELETE FROM SUBSCRIPTIONS WHERE ChatID=? AND Sub=?'
				c.execute(sql, queryParams)
				dbConn.commit()
				#...Notify the user
				bot.send_message(chat_id=update.message.chat_id,
								 text='Yeeey! *{}* subscription successfully '\
								 	.format(streamer) + 'deleted!',
								 parse_mode=ParseMode.MARKDOWN)
			else:
				# Otherwise warn the user that subscription doesn't exist
				bot.send_message(chat_id=update.message.chat_id,
								 text='Sorry, it seems you\'re not subscribed '\
								 	+ 'to *{}*'.format(streamer),
								 parse_mode=ParseMode.MARKDOWN)
			dbConn.close()

	## Show method
	#  Retrieve a list of all subscriptions for current user
	def show(self, bot, update):
		# Open db connection and create db cursor
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
		# Check if we received the correct, allowed, number of subscriptions
		# to enable (1 atm)
		if len(args) > 1:
			message = 'Sorry, you can enable only one streamer at a time'
			bot.send_message(chat_id=update.message.chat_id, text=message)
		elif len(args) < 1:
			message = 'Sorry, you must provide one valid twitch username '\
 					+ 'to enable.\n\n'\
 					+ 'Please try again with something like\n'\
 					+ '_/enable streamerUsername_'
			bot.send_message(chat_id=update.message.chat_id,
							 text=message,
							 parse_mode=ParseMode.MARKDOWN)
		else:
			streamer = args[0]
			# Open db connection and create db cursor	
			dbConn = sqlite3.connect('./db.sqlite')
			c = dbConn.cursor()
			# Retrieve status for desired subscription (Active/Disabled)
			sql='SELECT Active FROM SUBSCRIPTIONS WHERE ChatID=? AND Sub=?'
			queryParams = (update.message.chat_id,streamer)
			c.execute(sql,queryParams)
			status = c.fetchone()[0]
			
			if status == 1:
				# If it's already activated simply notify the user
				dbConn.close()
				message = 'No worries! *{}* subscription is already *Active*'\
					.format(streamer)
				bot.send_message(
					chat_id=update.message.chat_id, 
					text=message,
					parse_mode=ParseMode.MARKDOWN)
			else:
				# Otherwise set its status to 1 (Active) and notify th user
				sql='UPDATE SUBSCRIPTIONS SET Active=? WHERE ChatID=? AND Sub=?'
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
		# Check if we received the correct, allowed, number of subscriptions
		# to disable (1 atm)
		if len(args) > 1:
			message = 'Sorry, you can disable only one streamer at a time'
			bot.send_message(chat_id=update.message.chat_id, text=message)
		elif len(args) < 1:
			message = 'Sorry, you must provide one valid twitch username '\
					+ 'to disable.\n\n'\
					+ 'Please try again with something like\n'\
					+ '_/disable streamerUsername_'
			bot.send_message(chat_id=update.message.chat_id,
							 text=message,
							 parse_mode=ParseMode.MARKDOWN)
		else:
			streamer = args[0]
			# Open db connection and create db cursor	
			dbConn = sqlite3.connect('./db.sqlite')
			c = dbConn.cursor()
			# Retrieve status for desired subscription (Active/Disabled)
			sql = 'SELECT Active FROM SUBSCRIPTIONS WHERE ChatID=? AND Sub=?'
			queryParams = (update.message.chat_id,streamer)
			c.execute(sql,queryParams)
			status = c.fetchone()[0]

			if status == 0:
				# If it's already disabled simply notify the user
				dbConn.close()
				message = 'No problem, {} subscription was '.format(streamer)\
						+ 'already _Disabled_'
				bot.send_message(
					chat_id=update.message.chat_id,
					text=message,
					parse_mode=ParseMode.MARKDOWN)
			else:
				# Otherwise set its status to 0 (disabled) and notify th user
				sql='UPDATE SUBSCRIPTIONS SET Active=? WHERE ChatID=? AND Sub=?'
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