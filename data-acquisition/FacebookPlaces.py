# FacebookPlaces.py
# Author: Kassio Machado - uOttawa/Canada and UFMG/Brazil | Sept. 2017
# This code by myself with strictly purpose of research.
# =============================================================================
# Code to seach the Instagram places indicated on photos on Facebook Graph API.
# The requests provide the name and gps coords of places and get (if available)
# a list of candidates/related correspondent places with the following fields:
# id, name, category, location, category_list, description, link

import sys
import time
import json
import numpy
import argparse
import colorama
import requests
import datetime
from tqdm import tqdm

INFO = colorama.Fore.BLACK + colorama.Back.GREEN + '[INFO] '
WARNING = colorama.Fore.BLACK + colorama.Back.YELLOW + '[WRNG] '
ERROR = colorama.Fore.BLACK + colorama.Back.RED + '[ERROR] '
RESET = colorama.Fore.RESET + colorama.Back.RESET

if __name__ == "__main__":

    appIndex, inputfilename, interval = sys.argv[1:]
    appIndex = int(appIndex)
    interval = float(interval)

    filename = 'FacebookPlaces.json'
    inputfile = open(filename, 'r')
    appConfigs = json.load(inputfile)
    inputfile.close()

    defined = set()
    outputfilename = inputfilename.replace('.json', '-facebook.json')
    try:
        outputfile = open(outputfilename, 'r')
        for line in outputfile:
            if len(line) > 1:
                data = json.loads(line)
                defined.add(data['instagram'])
        outputfile.close()
        print INFO + str(len(defined)) + ' Places Defined Previously!' + RESET
    except IOError:
        print WARNING + 'File Previously Not Created!' + RESET
        pass
    outputfile = open(outputfilename, 'a', 0)

    inputfile = open(inputfilename, 'r')
    for nrows, l in tqdm(enumerate(inputfile), desc='Counting', leave=False):
        pass
    nrows += 1
    inputfile.seek(0)

    url =  'https://graph.facebook.com/search'
    tokens = appConfigs['apps'][appIndex]['app_id']
    tokens += "|" + appConfigs['apps'][appIndex]['app_secret']
    fields = 'id,name,category,location,category_list,description,link'

    for line in tqdm(inputfile, desc='Downloading',
                    total=nrows, dynamic_ncols=True):
        data = json.loads(line)
        if data['instagram'] in defined:
            continue
        payload = dict()
        payload['q'] = data['name']
        payload['type'] = 'place'
        payload['center'] = data['coords']
        payload['access_token'] = tokens
        payload['fields'] = fields
        resp = requests.get(url, params=payload)
        rjson = json.loads(resp.content)
        try:
            del rjson['paging']
        except KeyError:
            pass
        data['facebook'] = rjson
        json.dump(data, outputfile)
        outputfile.write('\n')
        time.sleep(interval + numpy.random.rand()
    outputfile.close()
    inputfile.close()
