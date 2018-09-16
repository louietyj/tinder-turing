# Tinder Turing Bot

A Critical Dating bot to facilitate a USR4002A Critical Reflection (tm) activity. We all reflect on our poor life decisions, don't we?

## tl;dr
This allows you to run Turing tests using a Telegram bot.

## Usage
1. Clone the repository
1. Rename `config_template.py` to `config.py` and add your API tokens
1. `$ pip install -r requirements.txt`
1. Ensure that `mongod` is running; otherwise `$ sudo service mongod start`
    - The database name is `tinder_turing` by default
1. `$ python3 -i main.py` (we use Python 3.6)

You need to remain on the interpreter to [operate the bot](#initiate-a-round) and [view reports](#report-generation).

### What to tell participants
1. Talk to the bot (that the API token is tied to on Telegram, duh)
1. `/start`
1. `/name <your name here>`, e.g. `/name John Doe`
1. (admin only) [Initiate a round](#initiate-a-round)
1. Talk to your assigned partner and follow on-screen instructions!
1. You can register your confidence that your partner is a human or a bot using `/confidence <round-number> <confidence-value>` (you can register your confidence for any round at any time)
    - e.g. `/confidence 1 66` to vote human-ness for your round 1 partner
    - 0 - definitely a bot
    - 50 - can't tell at all
    - 100 - definitely a human
1. (admin only) [End the round](#initiate-a-round)
1. View your [reports](#report-generation) and reflect on what it means to be human.

### Initiate a Round
(while on the python interpreter)

```
>>> pair_all(1, 0)    # pair everyone with P(bot) = 0 for round number 1
>>> unpair_all()      # end the current active round (round 1)
>>> pair_all(2, 0.5)  # pair everyone with P(bot) = 0.5 for round number 2
>>> unpair_all()      # end the current active round (round 2)
>>> pair_all(3, 1)    # pair everyone with P(bot) = 1 for round number 3
>>> unpair_all()      # end the current active round (round 3)
```

It is your responsibility to increment the round numbers yourself! They must be integers >= 0.

### Report Generation
While on the intepreter, you can run the following methods:

| What to Type | Description |
|--------------|-------------|
| `report.users()` | Summarize all registered users and the rounds they were in |
| `report.pairs()` | Summarize all pairs |
| `report.pairs(True)` | Summarize all active pairs |
| `report.pairs(False)` | Summarize all inactive pairs |
| `report.rank()` | Summarize rankings for human-bot and human-human pairs |
| `report.convo(uuid, outfile)` | Dump a conversation for a pair with object ID `uuid` and write it to a text file `outfile` and to `STDOUT` |
| `report.confusion(threshold=50, round_num=None)` | Summarize the confusion matrix at a `threshold` of 50 for all rounds |
