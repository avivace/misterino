from telegram.ext import Dispatcher, CommandHandler, Updater
from telegram import Bot, Update, ParseMode
from queue import Queue
from threading import Thread
from twitch import twitch
import sqlite3
import logging


class misterBot():
    def __init__(self, config, log, dbConn, webhookURL=None):
        botToken = config["botToken"]

        self.dbConn = dbConn
        self.c = self.dbConn.cursor()
        self.twitch = twitch(config)

        if config["mode"] == "polling":
            self.pollingInit(botToken, log)
        elif config["mode"] == "webhook":
            self.webhookInit(botToken, log)

    def pollingInit(self, botToken, log):
        self.updater = Updater(token=botToken)
        self.bot = self.updater.bot
        self.dispatcher = self.updater.dispatcher
        self.registerHandlers()
        self.updater.start_polling()

    def webhookInit(self, botToken, log, webhookURL=None):

        self.bot = Bot(botToken)
        self.log = log
        self.updateQueue = Queue()
        self.dispatcher = Dispatcher(self.bot, self.updateQueue)
        self.dispatcherThread = Thread(
            target=self.dispatcher.start, name='dispatcher', daemon=True)
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
        self.dispatcher.add_handler(CommandHandler('life', self.life))
        self.dispatcher.add_handler(CommandHandler('help', self.help))
        self.dispatcher.add_handler(CommandHandler('info', self.info))
        self.dispatcher.add_handler(CommandHandler('show', self.show))
        self.dispatcher.add_handler(
            CommandHandler('sub', self.sub, pass_args=True))
        self.dispatcher.add_handler(
            CommandHandler('unsub', self.unsub, pass_args=True))
        self.dispatcher.add_handler(
            CommandHandler('enable', self.enable, pass_args=True))
        self.dispatcher.add_handler(
            CommandHandler('disable', self.disable, pass_args=True))

    ### Help
    def help(self, bot, update):
        text = """ `/sub channelName` subscribes the current chat to the specified Twitch channel. The chat will be notified when that channel goes live. \n
`/unsub channelName` removes the subscribtion to the specified Twitch channel from the current chat. \n 
`/show channelName` lists the subscriptions for the current chat. \n
`/info` gives you more information on this bot. \n
You can have different subscriptions for each chat the bot is in. E.g. you can subscribe to channel A and B privately, while being subscribed to C and D in a group you add the bot."""
        bot.send_message(
            chat_id=update.message.chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN)

    ### Info
    def info(self, bot, update):
        text = """ This bot is was developed by @avivace and @dennib and it's open source, licensed under the GPL terms. You can find the source (or even contribute yourself!) at https://github.com/avivace/misterino """
        bot.send_message(
            chat_id=update.message.chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN)

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
            bot.send_message(
                chat_id=update.message.chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN)
        else:
            streamer = args[0]
            # Check if ANYONE already subscribed to that streamer
            queryParams = (streamer, )
            sql = 'SELECT COUNT(*) FROM SUBSCRIPTIONS WHERE Sub=?'
            self.c.execute(sql, queryParams)
            found = self.c.fetchone()[0]

            if not found:
                logging.warning("Adding a webhook and user subscription")
                userID = self.twitch.getUserID(streamer)
                self.twitch.updateWh('subscribe', userID)
                # Add to webhook list
                sql = ''' INSERT INTO WEBHOOKS (Sub) VALUES (?) '''

                logging.warning("Sending a webhook subscription")
                # ... Add it to db and...
                sql = '''INSERT INTO SUBSCRIPTIONS (ChatID,Sub,Active)
                         VALUES (?,?,?)'''
                queryParams = (update.message.chat_id, streamer, 1)
                self.c.execute(sql, queryParams)
                self.dbConn.commit()

                #... Notify the user
                bot.send_message(chat_id=update.message.chat_id,
                     text='Yeeey! you\'ve successfully subscribed to *{}*!'\
                     .format(streamer),
                     parse_mode=ParseMode.MARKDOWN)
            else:

                # Check if that particular user has that subscription
                queryParams = (update.message.chat_id, streamer)
                sql = 'SELECT COUNT(*) FROM SUBSCRIPTIONS WHERE ChatID=? AND Sub=?'
                self.c.execute(sql, queryParams)
                found = self.c.fetchone()[0]

                # If it doesn't exist yet...
                if not found:
                    logging.warning("Adding a user subscription")
                    userID = self.twitch.getUserID(streamer)
                    # ... Add it to db and...
                    sql = '''INSERT INTO SUBSCRIPTIONS (ChatID,Sub,Active)
                             VALUES (?,?,?)'''
                    queryParams = (update.message.chat_id, streamer, 1)
                    self.c.execute(sql, queryParams)
                    self.dbConn.commit()

                    #... Notify the user
                    bot.send_message(chat_id=update.message.chat_id,
                         text='Yeeey! you\'ve successfully subscribed to *{}*!'\
                         .format(streamer),
                         parse_mode=ParseMode.MARKDOWN)

                else:
                    logging.warning("User were already subbed")
                    # Otherwise warn the user that subscription is already existent
                    bot.send_message(chat_id=update.message.chat_id,
                         text='Don\'t worry! You are already subscribed to '\
                         + '*{}*'.format(streamer),
                         parse_mode=ParseMode.MARKDOWN)

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
            bot.send_message(
                chat_id=update.message.chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN)
        else:
            streamer = args[0]
            queryParams = (update.message.chat_id, streamer)
            # Check if requested subscription already exits in db
            sql = 'SELECT COUNT(*) FROM SUBSCRIPTIONS WHERE ChatID=? AND Sub=?'
            self.c.execute(sql, queryParams)
            found = self.c.fetchone()[0]
            # If it exits...
            if found:
                # ... Delete it and...
                sql = 'DELETE FROM SUBSCRIPTIONS WHERE ChatID=? AND Sub=?'
                self.c.execute(sql, queryParams)
                self.dbConn.commit()
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

    ## Show method
    #  Retrieve a list of all subscriptions for current user
    def show(self, bot, update):

        # Execute a count of wantend rows
        sql = 'SELECT COUNT(*) FROM SUBSCRIPTIONS WHERE ChatID = ?'
        queryParams = (str(update.message.chat_id), )
        self.c.execute(sql, queryParams)

        # If we have at least one sub for current user...
        if self.c.fetchone()[0] > 0:
            # ...extract subscriptions from db and collect them
            # in subs variable...
            sql = 'SELECT * FROM SUBSCRIPTIONS WHERE ChatID = ?'
            self.c.execute(sql, queryParams)
            subs = self.c.fetchall()

            # Build up the message for the user with retrieved subscriptions
            message = "Here's a list of all of your subscriptions:\n"
            for sub in subs:
                streamer = sub[1]
                status = "*Active*" if sub[2] else "_Disabled_"
                message += '\n' + streamer + ': ' + status + '\n---'
        else:
            # ...otherwise warn the user he has no subscriptions yet
            message = "Sorry, it seems you have no subscriptions yet"

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
            bot.send_message(
                chat_id=update.message.chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN)
        else:
            streamer = args[0]
            # Execute a count of wantend rows
            sql = 'SELECT COUNT(*) FROM SUBSCRIPTIONS WHERE ChatID = ? AND Sub = ?'
            queryParams = (str(update.message.chat_id), streamer)
            self.c.execute(sql, queryParams)
            found = self.c.fetchone()[0]
            # If the steamer we want to enable exists for current user...
            if found:
                # ... Retrieve status for desired subscription (Active/Disabled)
                sql = 'SELECT Active FROM SUBSCRIPTIONS WHERE ChatID=? AND Sub=?'
                queryParams = (update.message.chat_id, streamer)
                self.c.execute(sql, queryParams)
                status = self.c.fetchone()[0]

                if status == 1:
                    # If it's already activated simply notify the user
                    message = 'No worries! *{}* subscription is already *Active*'\
                     .format(streamer)
                    bot.send_message(
                        chat_id=update.message.chat_id,
                        text=message,
                        parse_mode=ParseMode.MARKDOWN)
                else:
                    # Otherwise set its status to 1 (Active)...
                    sql = 'UPDATE SUBSCRIPTIONS SET Active=? WHERE ChatID=? AND Sub=?'
                    queryParams = (1, update.message.chat_id, streamer)
                    self.c.execute(sql, queryParams)
                    self.dbConn.commit()
                    # ... and notify th user
                    message = "Yeeeey! *{}* subscription has been *Activated*"\
                    .format(streamer)
                    bot.send_message(
                        chat_id=update.message.chat_id,
                        text=message,
                        parse_mode=ParseMode.MARKDOWN)
            else:
                # ... Otherwise warn the user
                message = 'Sorry, it\' seems like you\'re not subscribed to *{}*'\
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
            bot.send_message(
                chat_id=update.message.chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN)
        else:
            streamer = args[0]
            # Execute a count of wantend rows
            sql = 'SELECT COUNT(*) FROM SUBSCRIPTIONS WHERE ChatID = ? AND Sub = ?'
            queryParams = (str(update.message.chat_id), streamer)
            self.c.execute(sql, queryParams)
            found = self.c.fetchone()[0]
            # If the steamer we want to disable exists for current user...
            if found:
                # ... Retrieve status for desired subscription (Active/Disabled)
                sql = 'SELECT Active FROM SUBSCRIPTIONS WHERE ChatID=? AND Sub=?'
                queryParams = (update.message.chat_id, streamer)
                self.c.execute(sql, queryParams)
                status = self.c.fetchone()[0]

                if status == 0:
                    # If it's already disabled simply notify the user
                    message = 'No problem, {} subscription was '.format(streamer)\
                      + 'already _Disabled_'
                    bot.send_message(
                        chat_id=update.message.chat_id,
                        text=message,
                        parse_mode=ParseMode.MARKDOWN)
                else:
                    # Otherwise set its status to 0 (disabled)...
                    sql = 'UPDATE SUBSCRIPTIONS SET Active=? WHERE ChatID=? AND Sub=?'
                    queryParams = (0, update.message.chat_id, streamer)
                    self.c.execute(sql, queryParams)
                    self.dbConn.commit()
                    # ... and notify th user
                    message = "Ok! *{}* subscription has been _Disabled_"\
                    .format(streamer)
                    bot.send_message(
                        chat_id=update.message.chat_id,
                        text=message,
                        parse_mode=ParseMode.MARKDOWN)
            else:
                # ... Otherwise warn the user
                message = 'Sorry, it\' seems like you\'re not subscribed to *{}*'\
                .format(streamer)
                bot.send_message(
                    chat_id=update.message.chat_id,
                    text=message,
                    parse_mode=ParseMode.MARKDOWN)

    def updateWebhooksTable():
        webhooks = twitch.listWebhooks()
        sql = '''INSERT INTO WEBHOOKS (Topic, Expires) VALUES (?, ?)'''
        queryParams = (st)
        self.c.execute(sql, queryParams)
