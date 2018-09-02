import telegram
import telegram.ext
import telegram.error
from dal import *

class TuringBot():
    def __init__(self, token):
        self.updater = telegram.ext.Updater(token=token)
        self.dispatcher = self.updater.dispatcher
        self.bot = self.dispatcher.bot

        # Add handlers
        self.dispatcher.add_handler(telegram.ext.CommandHandler('start', self.start_handler))
        self.dispatcher.add_handler(telegram.ext.CommandHandler('name', self.name_handler))
        self.dispatcher.add_handler(telegram.ext.CommandHandler('id', self.id_handler))
        self.dispatcher.add_error_handler(self.error_handler)
        self.updater.start_polling()

    @staticmethod
    def _format_bot(text):
        '''Format text that is sent from the bot and not from the other party'''
        return f'[Bot] {text}'

    def start_handler(self, bot, update):
        chat_id = update.message.chat.id
        msg = 'Hi! Please register by typing /name {name}.'
        bot.sendMessage(chat_id=chat_id, text=self._format_bot(msg))

    def name_handler(self, bot, update):
        chat_id = update.message.chat.id
        try:
            name = update.message.text.split(maxsplit=1)[1]
            name = name.strip()
            assert name.encode('ascii').decode() == name
        except Exception:
            msg = 'Please enter your name with only letters and numbers, e.g. no emojis.'
            bot.sendMessage(chat_id=chat_id, text=self._format_bot(msg))
            return
        try:
            db.users.replace_one({'tid': chat_id}, {'tid': chat_id, 'name': name}, True)
        except Exception as e:
            bot.sendMessage(chat_id=chat_id, text=self._format_bot(f'Error: {e}'))
            return
        msg = f'You have successfully registered as: {name}.'
        bot.sendMessage(chat_id=chat_id, text=self._format_bot(msg))

    def id_handler(self, bot, update):
        chat_id = update.message.chat.id
        bot.sendMessage(chat_id=chat_id, text=self._format_bot(str(chat_id)))

    def error_handler(self, bot, update, error):
        if isinstance(error, TimedOut):
            return
        print(update)
        print(error)
