import telegram
import telegram.ext
import telegram.error

class TuringBot():
    def __init__(self, token):
        self.updater = telegram.ext.Updater(token=token)
        self.dispatcher = self.updater.dispatcher
        self.bot = self.dispatcher.bot

        # Add handlers
        self.dispatcher.add_handler(telegram.ext.CommandHandler('start', self.start_handler))
        self.dispatcher.add_error_handler(self.error_handler)
        self.updater.start_polling()

    def start_handler(self, bot, update):
        chat_id = update.message.chat.id
        bot.sendMessage(chat_id=chat_id, text='Hello world!')

    def error_handler(self, bot, update, error):
        if isinstance(error, TimedOut):
            return
        print(update)
        print(error)
