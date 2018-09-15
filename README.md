# Tinder Turing Bot

A Critical Dating bot to facilitate a USR4002A Critical Reflection (tm) activity. We all reflect on our poor life decisions, don't we?

Usage:

```
pip install -r requirements.txt
python3 -i main.py
```

## Report Generation
While on the intepreter, you can run the following methods:

| What to Type | Description |
|--------------|-------------|
| `report.users()` | Summarize all registered users and the rounds they were in |
| `report.pairs()` | Summarize all pairs |
| `report.pairs(True)` | Summarize all active pairs |
| `report.pairs(False)` | Summarize all inactive pairs |
| `report.rank()` | Summarize rankings for human-bot and human-human pairs |
| `report.convo(uuid, outfile)` | Dump a conversation for a pair with object ID `uuid` and write it to a text file `outfile` and to `STDOUT` |
