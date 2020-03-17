import json
import websocket
import pygame
import pyperclip
import requests
import settings


poe_filter = None


def on_message_2(ws, message):
    print(message)
    print(poe_filter)


def on_message(ws, message):
    newitems = json.loads(message)
    newitems = newitems["new"]
    newitem = newitems[len(newitems) - 1]

    req_url = settings.SEARCH_URL.format(newitem, poe_filter)
    r = requests.get(req_url)

    result_json = json.loads(r.text)
    result_json = result_json["result"]

    if result_json:
        copypaste = result_json[0]["listing"]["whisper"]

        pyperclip.copy(copypaste)
        
        pygame.mixer.init()
        pygame.mixer.music.load("beep.wav")
        pygame.mixer.music.set_volume(0.05)
        pygame.mixer.music.play()


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("closed")


if __name__ == "__main__":   
    f = open('dump.txt', 'r')
    poe_settings = json.loads(f.read())
    f.close()

    poesessid = input("Please enter your POESESSID [{}]: ".format(poe_settings['poesessid'])) or poe_settings['poesessid']
    poe_filter = input("Please enter your filter [{}] : ".format(poe_settings['poe_filter'])) or poe_settings['poe_filter']

    new_settings = {"poesessid": poesessid, "poe_filter": poe_filter}
    f = open('dump.txt', 'w+')
    f.write(json.dumps(new_settings))
    f.close()

    session = requests.Session()
    response = session.get('https://www.pathofexile.com')

    my_cookie = '__cfuid={}; POESESSID={}'.format(session.cookies.get_dict()['__cfduid'], poesessid)

    ws = websocket.WebSocketApp('ws://www.pathofexile.com/api/trade/live/{}/{}'.format(settings.LEAGUE, poe_filter),
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close,
                                cookie = my_cookie)
    ws.run_forever()