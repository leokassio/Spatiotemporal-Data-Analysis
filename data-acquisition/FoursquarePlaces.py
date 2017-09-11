# -*- coding: utf-8 -*-

import sys
import json
import colorama
import requests
from tqdm import tqdm

INFO = colorama.Fore.BLACK + colorama.Back.GREEN + '[INFO] '
WARNING = colorama.Fore.BLACK + colorama.Back.YELLOW + '[WRNG] '
ERROR = colorama.Fore.BLACK + colorama.Back.RED + '[ERROR] '
RESET = colorama.Fore.RESET + colorama.Back.RESET

url = 'https://api.foursquare.com/v2/venues/search?'
url += 'oauth_token=VKE2KCEVOAHRFRTEFR15I2V5KLBRYWUKF0LEK2YVMMXJKZQP'
url += '&v=20131016&ll=40.7142%2C-74.0064'
url += '&query=New%20York%2C%20New%20York'
url += '&intent=checkin'
resp = requests.get(url)

rate = int(r.headers['X-RateLimit-Remaining'])
data = json.loads(resp.content)
