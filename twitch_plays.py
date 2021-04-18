import time
from twitch_plays_hackru import TwitchPlaysOnline, TwitchPlaysOffline

potential_moves = ["a4e4","f3b5"]


twitch_options = {
    "PASS": "oauth:***",
    "BOT": "Chester",
    "CHANNEL": "psych_its_mike",
    "OWNER": "psych_its_mike",
    "OPTIONS": potential_moves,
    "VOTE_INTERVAL": 5
}
tPlays = TwitchPlaysOnline(**twitch_options)

time.sleep(30)
result = tPlays.vote_result()
print('And the winning move is: '+ str(result))