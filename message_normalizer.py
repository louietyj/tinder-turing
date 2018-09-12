import inspect
import nltk

END_PUNCS = '.?!'

nltk.download('punkt')

class MessageNormalizer:
    def __init__(self, message):
        self.original_message = message
        self.message = message
        self.fatal_errors = []
        self.warn_errors = []
        self._enforce()

    def _enforce(self):
        # Some magic to retrieve all enforce methods
        for attrib in dir(self):
            if not attrib.startswith('enforce_') or not callable(getattr(self, attrib)):
                continue
            try:
                getattr(self, attrib)()
            except Exception as e:
                print(f'Enforce error ({attrib}): {self.original_message}, {e}')

    def enforce_has_content(self):
        if any(char.isalnum() for char in self.message):
            return
        self.fatal_errors.append('Message contains no words.')

    def enforce_single_whitespace(self):
        if '  ' not in self.message:
            return
        while '  ' in self.message:
            self.message = self.message.replace('  ', ' ')
        self.warn_errors.append('Replaced double-spaces with single-spaces.')

    def enforce_punctuation(self):
        if self.message and self.message[-1] in END_PUNCS:
            return
        self.message = self.message + '.'
        self.warn_errors.append('Ending period added.')

    def enforce_capitalization(self):
        sentences = nltk.tokenize.sent_tokenize(self.message)
        fixed = False
        for i, sentence in enumerate(sentences):
            if not sentence[0].isalpha():
                continue
            if sentence[0].isupper():
                continue
            fixed = True
            sentence = sentence[0].upper() + sentence[1:]
            sentences[i] = sentence
        if fixed:
            self.warn_errors.append('Enforced capitalization on first word of sentences.')
        self.message = ' '.join(sentences)
