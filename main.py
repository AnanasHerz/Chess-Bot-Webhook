from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime
import pytz
import requests
import time

w = open("webhook.txt", "r")
webhook_url = w.read()

while True:
    #Webhook and timezone
    webhook = DiscordWebhook(url=webhook_url)
    tz = pytz.timezone('US/Pacific')
    #Def year
    year = str(datetime.now(tz=tz).year)
    if datetime.now(tz=tz).month < 10:
        month = '0' + str(datetime.now(tz=tz).month)
    else:
        month = datetime.now(tz=tz).month
    #Player, try response 1st time and message boolean
    player = 'ananasherz1' #Players username
    check = requests.get(f'https://api.chess.com/pub/player/{player}')
    fail = False
    if check.status_code == 200:
        response = requests.get(f'https://api.chess.com/pub/player/{player}/games/{year}/{month}').json()
        message = False
        #Modified year and month if no game has been played this month
        if response['games'] == '[]' and datetime.now(tz=tz).month == 1:
            year = str(datetime.now(tz=tz).year - 1)
            month = '12'
            response = requests.get(f'https://api.chess.com/pub/player/{player}/games/{year}/{month}').json()
        countm = 1
        county = 1
        while response['games'] == '[]' and datetime.now(tz=tz).month > 1:
            if int(month) > 9:
                try_month = month.split()
                month = '0' + int(try_month[1])-countm
                countm += 1
            countm = 1
            if int(month) < 10:
                month = int(month)-countm
                countm += 1
            if month == '01':
                year = int(year)-county
                month = '12'
                county += 1
            if response['games'] == '[]' and year == '2007' and month == '05':
                time.sleep(5)
            if fail == False:
                response = requests.get(f'https://api.chess.com/pub/player/{player}/games/{year}/{month}').json()
                countm = 1
                county = 1
                        
                if response['games'] == '[]' and datetime.now(tz=tz).month > 1:
                    month = '0' + str(int(datetime.now(tz=tz).month)-1)
                else:
                    pass
                response = requests.get(f'https://api.chess.com/pub/player/{player}/games/{year}/{month}').json()
                if response['games'] == '[]':
                    time.sleep(5)
                if response['games'] != '[]':
                    #Def the most recent game
                    newest = int(len(response['games']))-1
                    #Def the suspected last game
                    suspected_last_game = response['games'][newest]['url']
                    f = open("last-game.txt", "r")
                    last_game = f.read()
                    if suspected_last_game != last_game:
                        f.close()
                        f = open("last-game.txt", "w")
                        f.write(suspected_last_game)
                        f.close()
                        print('Url changed')
                        message = True
                    if suspected_last_game == last_game:
                        time.sleep(5)
                    #Empty variables
                    rated = ''
                    time_class = ''
                    result = ''
                    reason = ''
                    side = ''
                    opponent = ''
                    endboard = ''
                    #Url var
                    url = response['games'][newest]['url']
                    #Rated or unrated
                    if response['games'][newest]['rated'] is True:
                        rated = 'a rated'
                    if response['games'][newest]['rated'] is False:
                        rated = 'an unrated'
                    #Time class of game (Blitz, Bullet...) and url friendly endboard image adress
                    time_class = response['games'][newest]['time_class']
                    fen = response['games'][newest]['fen'].replace(" ", "%20")
                    #Defines the sides
                    if response['games'][newest]['white']['username'] == player:
                        side = response['games'][newest]['white']
                        opponent = response['games'][newest]['black']
                    if response['games'][newest]['black']['username'] == player:
                        side = response['games'][newest]['black']
                        opponent = response['games'][newest]['white']
                    if response['games'][newest]['white']['username'] != player and response['games'][newest]['black']['username'] != player:
                        side = 'invalid colors'
                        opponent = 'invalid colors'
                    #Result codes
                    if side['result'] == 'win':
                        result = 'won'
                    if opponent['result'] == 'win':
                        result = 'lost'
                    if side['result'] == 'agreed' or side['result'] == 'repetition' or side['result'] == 'stalemate' or side['result'] == 'insufficient' or side['result'] == '50move' or side['result'] == 'timevsinsufficient':
                        result = 'drawed'
                    else:
                        pass
                    #Reason of endpoint
                    if side['result'] == 'checkmated' or opponent['result'] == 'checkmated':
                        reason = 'checkmate'
                    if side['result'] == 'agreed' or opponent['result'] == 'agreed':
                        reason = 'an agreemend'
                    if side['result'] == 'repetition' or opponent['result'] == 'repetition':
                        reason = 'repetition'
                    if side['result'] == 'timeout' or opponent['result'] == 'timeout':
                        reason = 'timeout'
                    if side['result'] == 'resigned' or opponent['result'] == 'resigned':
                        reason = 'resignation'
                    if side['result'] == 'stalemate' or opponent['result'] == 'stalemate':
                        reason = 'a stalemate'
                    if side['result'] == 'insufficient' or opponent['result'] == 'insufficient':
                        reason = 'insufficient material'
                    if side['result'] == '50move' or opponent['result'] == '50move':
                        reason = 'the 50-move rule'
                    if side['result'] == 'abandoned' or opponent['result'] == 'abandoned':
                        reason = 'abandonment'
                    if side['result'] == 'kingofthehill' or opponent['result'] == 'kingofthehill':
                        reason = 'the opponent king who reached the hill'
                    if side['result'] == 'threecheck' or opponent['result'] == 'threecheck':
                        reason = 'three check'
                    if side['result'] == 'timevsinsufficient' or opponent['result'] == 'timevsinsufficient':
                        reason = 'the timeout vs insufficient material rule'
                    if side['result'] == 'bughousepartnerlose' or opponent['result'] == 'bughousepartnerlose':
                        reason = 'Bughouse partner lost'
                    else:
                        pass
                    #Endboard image adress
                    endboard = f'https://www.chess.com/dynboard?fen={fen}&board=brown&piece=neo&size=3'
                    #Alert                
                    alert = DiscordEmbed(
                        title = f'{player} just played a game of chess!',
                        description = f'{player} played {rated} {time_class} game and {result} by {reason}.',
                        color = '769656'
                    )
                    alert.set_author(name='Chess Bot', icon_url='https://play-lh.googleusercontent.com/a7R5nyeaX8lIEWdBOxjlvbyq9LcFwh3XMvNtBPEKR3LPGgdvgGrec4sJwn8tUaaSkw')
                    alert.add_embed_field(name='Url', value=url)
                    alert.set_image(url=endboard)
                    alert.set_footer(text='Made by AnanasHerz#5480')
                    webhook.add_embed(alert)
                    #Sending the message or not
                    if message == True:
                        webhook.execute()
                        print('Webhook send!')
                        message = False
                        time.sleep(5)
                    if message == False:
                        pass
    if check.status_code != 200:
        print('Status code: ', check.status_code())
        break