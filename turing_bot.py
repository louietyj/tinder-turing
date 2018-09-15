import telegram
import telegram.ext
import telegram.error
from dal import *
from message_normalizer import *
from utils import *
from utils_tgbot import *


class TuringBot():
    def __init__(self, token, bot_reply):
        self.bot_reply = bot_reply
        self.updater = telegram.ext.Updater(token=token)
        self.dispatcher = self.updater.dispatcher
        self.bot = BotWrapper(self.dispatcher.bot)

        # Add handlers
        self.dispatcher.add_handler(telegram.ext.CommandHandler('start', self.start_handler))
        self.dispatcher.add_handler(telegram.ext.CommandHandler('name', self.name_handler))
        self.dispatcher.add_handler(telegram.ext.CommandHandler('id', self.id_handler))
        self.dispatcher.add_handler(telegram.ext.CommandHandler('confidence', self.confidence_handler))
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
        run_async(self.bot.sendMessage, chat_id=chat_id, text=self._format_bot(msg))

    def name_handler(self, bot, update):
        chat_id = update.message.chat.id

        # Validate name
        try:
            name = update.message.text.split(maxsplit=1)[1]
            name = name.strip()
            assert name.encode('ascii').decode() == name
        except Exception:
            msg = 'Please enter your name with only letters and numbers, e.g. no emojis.'
            run_async(self.bot.sendMessage, chat_id=chat_id, text=self._format_bot(msg))
            return

        # Update name
        user = User.objects(tid=str(chat_id)).first() or User(tid=str(chat_id))
        user.name = name
        try:
            user.save()
        except Exception as e:
            run_async(self.bot.sendMessage, chat_id=chat_id, text=self._format_bot(f'Error: {e}'))
            return
        msg = f'You have successfully registered as: {name}.'
        run_async(self.bot.sendMessage, chat_id=chat_id, text=self._format_bot(msg))

    def id_handler(self, bot, update):
        chat_id = update.message.chat.id
        run_async(self.bot.sendMessage, chat_id=chat_id, text=self._format_bot(str(chat_id)))

    def message_handler(self, bot, update):
        chat_id = update.message.chat.id
        message = update.message.text
        message_id = update.message.message_id
        pair = get_pair_by_tid(chat_id)

        if len(pair) > 1:
            msg = 'Whoa there! Something\'s wrong - you\'re in multiple active pairs!'
            run_async(self.bot.sendMessage, chat_id=chat_id, text=self._format_bot(msg))

        if not pair:
            msg = 'You are not connected to anyone yet. Keep swiping, one day you\'ll meet someone!'
            run_async(self.bot.sendMessage, chat_id=chat_id, text=self._format_bot(msg))

        pair = pair[0]
        partner = list({pair['tid1'], pair['tid2']} - {str(chat_id)})[0]
        is_turn = pair[f'tid{pair.turn}'] == str(chat_id)

        # Enforce turn-taking
        if not is_turn:
            msg = 'Message *not* sent. It\'s not your turn!'
            run_async(self.bot.sendMessage, chat_id=chat_id, text=self._format_bot(msg), reply_to_message_id=message_id)
            return

        # Message normalization
        nm = MessageNormalizer(message)
        if nm.fatal_errors:
            msg = 'Message *not* sent due to the following violations:\n' + \
                    '\n'.join(f'- {error}' for error in nm.fatal_errors)
            run_async(self.bot.sendMessage, chat_id=chat_id, text=self._format_bot(msg), reply_to_message_id=message_id)
            return
        elif nm.warn_errors:
            msg = 'Message auto-corrected and sent with the following fixes:\n' + \
                    '\n'.join(f'- {error}' for error in nm.warn_errors) + \
                    f'\n\nCorrected message: {nm.message}'
            run_async(self.bot.sendMessage, chat_id=chat_id, text=self._format_bot(msg), reply_to_message_id=message_id)
        message = nm.message

        # Flip turn
        pair.update(set__turn=(1 if pair.turn == 2 else 2))
        pair.reload()

        # log message to DB
        Message(pair=pair, sender=get_name_by_tid(chat_id), message=message, timestamp=datetime.datetime.now()).save()

        # Forward or trigger bot reply
        if partner:
            run_async(self.bot.sendMessage, chat_id=partner, text=message)
        else:
            run_async(self._await_bot_reply, pair, chat_id, message)

    def _await_bot_reply(self, pair, chat_id, message):
        reply = self.bot_reply.get_reply(chat_id, message)
        # Send the normalized message whether or not there are fatal violations
        reply = MessageNormalizer(reply).message
        run_async(self.bot.sendMessage, chat_id=chat_id, text=reply)
        pair.update(set__turn=1)    # Supposedly atomic, so no need for lock

    def confidence_handler(self, bot, update):
        confidence_self_help = '/confidence <round> <confidence-level>\ne.g. /confidence 2 99\n\nPlease enter the round number and your confidence that you were talking to a human with a number from 0 to 100!\n\n 0 - definitely a robot\n50 - cannot tell at all\n100 - definitely a human'
        chat_id = update.message.chat.id
        message = update.message.text

        try:
            _, iteration, confidence = message.split(maxsplit=2)
            iteration, confidence = int(iteration.strip()), int(confidence.strip())
            assert iteration >= 0
            assert 0 <= confidence <= 100
        except Exception as e:
            print(e)
            run_async(self.bot.sendMessage, chat_id=chat_id, text=self._format_bot(confidence_self_help))
            return
        
        # confidence is sane and good to use
        # grab target iteration pair
        current_pair = get_pair_by_tid_in_round(chat_id, iteration)

        if len(current_pair) > 1:
            msg = 'Whoa there! Something\'s wrong - you were/are in multiple pairs in round {}!'.format(iteration)
            run_async(self.bot.sendMessage, chat_id=chat_id, text=self._format_bot(msg))
            return

        if not current_pair:
            msg = 'Couldn\'t find a pair with you in it in round {}!'.format(iteration)
            run_async(self.bot.sendMessage, chat_id=chat_id, text=self._format_bot(msg))
            return

        # update pair confidence
        current_pair = current_pair[0]

        try:
            if current_pair.tid1 == str(chat_id):
                current_pair.update(set__confidence1=confidence)
            elif current_pair.tid2 == str(chat_id):
                current_pair.update(set__confidence2=confidence)
            current_pair.reload()
        except ValidationError as e:
            run_async(self.bot.sendMessage, chat_id=chat_id, text=self._format_bot(confidence_self_help))
            return

        run_async(self.bot.sendMessage, chat_id=chat_id, text=self._format_bot('Thanks for voting for round {}!'.format(iteration)))
        return
        
    def error_handler(self, bot, update, error):
        if isinstance(error, TimedOut):
            return
        print(update)
        print(error)
