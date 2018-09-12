import telegram
import telegram.ext
import telegram.error
from dal import *
from message_normalizer import *

class TuringBot():
    def __init__(self, token, bot_reply):
        self.bot_reply = bot_reply
        self.updater = telegram.ext.Updater(token=token)
        self.dispatcher = self.updater.dispatcher
        self.bot = self.dispatcher.bot

        # Add handlers
        self.dispatcher.add_handler(telegram.ext.CommandHandler('start', self.start_handler))
        self.dispatcher.add_handler(telegram.ext.CommandHandler('name', self.name_handler))
        self.dispatcher.add_handler(telegram.ext.CommandHandler('id', self.id_handler))
        self.dispatcher.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.text, self.message_handler))
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

        # Validate name
        try:
            name = update.message.text.split(maxsplit=1)[1]
            name = name.strip()
            assert name.encode('ascii').decode() == name
        except Exception:
            msg = 'Please enter your name with only letters and numbers, e.g. no emojis.'
            bot.sendMessage(chat_id=chat_id, text=self._format_bot(msg))
            return

        # Update name
        user = User.objects(tid=str(chat_id)).first() or User(tid=str(chat_id))
        user.name = name
        try:
            user.save()
        except Exception as e:
            bot.sendMessage(chat_id=chat_id, text=self._format_bot(f'Error: {e}'))
            return
        msg = f'You have successfully registered as: {name}.'
        bot.sendMessage(chat_id=chat_id, text=self._format_bot(msg))

    def id_handler(self, bot, update):
        chat_id = update.message.chat.id
        bot.sendMessage(chat_id=chat_id, text=self._format_bot(str(chat_id)))

    def message_handler(self, bot, update):
        chat_id = update.message.chat.id
        message = update.message.text
        message_id = update.message.message_id
        pair = get_pair_by_tid(chat_id)

        if len(pair) > 1:
            msg = 'Whoa there! Something\'s wrong - you\'re in multiple active pairs!'
            bot.sendMessage(chat_id=chat_id, text=self._format_bot(msg))

        if not pair:
            msg = 'You are not connected to anyone yet. Keep swiping, one day you\'ll meet someone!'
            bot.sendMessage(chat_id=chat_id, text=self._format_bot(msg))

        pair = pair[0]
        partner = list({pair['tid1'], pair['tid2']} - {str(chat_id)})[0]
        is_turn = pair[f'tid{pair.turn}'] == str(chat_id)

        # Enforce turn-taking
        if not is_turn:
            msg = 'Message *not* sent. It\'s not your turn!'
            bot.sendMessage(chat_id=chat_id, text=self._format_bot(msg), reply_to_message_id=message_id)
            return

        # Message normalization
        nm = MessageNormalizer(message)
        if nm.fatal_errors:
            msg = 'Message *not* sent due to the following violations:\n' + \
                    '\n'.join(f'- {error}' for error in nm.fatal_errors)
            bot.sendMessage(chat_id=chat_id, text=self._format_bot(msg), reply_to_message_id=message_id)
            return
        elif nm.warn_errors:
            msg = 'Message auto-corrected and sent with the following fixes:\n' + \
                    '\n'.join(f'- {error}' for error in nm.warn_errors) + \
                    f'\n\nCorrected message: {nm.message}'
            bot.sendMessage(chat_id=chat_id, text=self._format_bot(msg), reply_to_message_id=message_id)
        message = nm.message

        # TODO: Log message to DB

        if partner:
            bot.sendMessage(chat_id=partner, text=message)
            pair.turn = 1 if pair.turn == 2 else 2
            pair.save()
        else:
            pair.turn = 2
            pair.save()
            try:
                # TODO: Make this asynchronous
                reply = self.bot_reply.get_reply(chat_id, message)
                # Send the normalized message whether or not there are fatal violations
                reply = MessageNormalizer(reply).message
                bot.sendMessage(chat_id=chat_id, text=reply)
            finally:
                pair.turn = 1
                pair.save()

    def error_handler(self, bot, update, error):
        if isinstance(error, TimedOut):
            return
        print(update)
        print(error)
