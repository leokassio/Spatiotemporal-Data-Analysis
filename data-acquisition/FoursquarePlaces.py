# -*- coding: utf-8 -*-

import sys
import json
import colorama
import requests
import datetime
from tqdm import tqdm

INFO = colorama.Fore.BLACK + colorama.Back.GREEN + '[INFO] '
WARNING = colorama.Fore.BLACK + colorama.Back.YELLOW + '[WRNG] '
ERROR = colorama.Fore.BLACK + colorama.Back.RED + '[ERROR] '
RESET = colorama.Fore.RESET + colorama.Back.RESET

url = 'https://api.foursquare.com/v2/venues/search'
payload = dict()
payload['ll'] = '41.88256075,-87.623115'
payload['client_id'] = ''
payload['client_secret'] = ''
payload['v'] = '20160616' #datetime.datetime.now().strftime('%Y%m%d')
payload['query'] = 'The Giant'
payload['intent'] = 'match'
resp = requests.get(url, params=payload)

print WARNING + resp.url + RESET

try:
    rate = int(resp.headers['X-RateLimit-Remaining'])
    print rate, 'reqs reamining'
    data = json.loads(resp.content)
    outputfile = open('response.json', 'w', 0)
    json.dump(data, outputfile, indent=4)
except KeyError:
    print resp.headers
    print resp.content
