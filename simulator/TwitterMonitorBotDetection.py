# -*- coding: utf-8 -*-

import csv
import sys
import json
import colorama
import requests
import datetime
import botometer # https://github.com/IUNetSci/botometer-python ICWSM
from tqdm import tqdm


INFO = colorama.Fore.BLACK + colorama.Back.GREEN + '[INFO] '
WARNING = colorama.Fore.BLACK + colorama.Back.YELLOW + '[WRNG] '
ERROR = colorama.Fore.BLACK + colorama.Back.RED + '[ERROR] '
RESET = colorama.Fore.RESET + colorama.Back.RESET

def loadTotalRows(inputfilename):
    inputfile = open(inputfilename, 'rb')
    for nrows, l in tqdm(enumerate(inputfile), desc='Counting Lines', leave=False):
        pass
    nrows += 1
    inputfile.close()
    return nrows

if __name__ == "__main__":
    try:
        args = sys.argv[1:]
        currentToken = int(args.pop(0))
        sampleSize = int(args.pop(0))
        inputfilename = args.pop(0)
        if len(args) > 0:
            configfilename = args.pop(0)
        else:
            configfilename = 'TwitterAuthentication.json'
    except Exception:
        print ERROR + 'Please provide a valid cmd line' + RESET
        exit()

    usersDefined = set()
    outputfilename = inputfilename.replace('coords.json', 'bot-scores.json')
    try:
        outputfile = open(outputfilename, 'r')
        for sample in outputfile:
            sample = json.loads(sample)
            try:
                userid = sample['user']['id_str']
                usersDefined.add(userid)
            except KeyError:
                print 'Invalid Sample:', sample
        print INFO + str(len(usersDefined)) + ' users already defined' + RESET
    except IOError:
        print INFO + 'No data previously defined' + RESET
        pass

    twitterConfig = json.load(open(configfilename, 'r'))
    mashape_key = twitterConfig['mashape_key']
    consumer_key = twitterConfig['consumer_key']
    consumer_secret = twitterConfig['consumer_secret']
    tokens = twitterConfig['access_tokens']

    userids = list()
    invalidSamples = 0
    nrows = loadTotalRows(inputfilename)
    inputfile = open(inputfilename, 'r')
    for sample in tqdm(inputfile, desc='Loading', total=nrows, disable=False):
        try:
            sample = json.loads(sample)
        except:
            invalidSamples += 1
        if sum(sample['coords'].values()) > 300:
            # print 'checking: https://twitter.com/intent/user?user_id=' + sample['userid']
            if sample['userid'] not in usersDefined:
                userids.append(sample['userid'])
    if invalidSamples:
        print ERROR + 'Invalid Samples: ' + str(invalidSamples)

    outputfile = open(outputfilename, 'a' , 0)
    print INFO + 'Checking ' + str(len(userids)) + ' Accounts' + RESET

    indexes = range(0, len(userids), sampleSize) # 171
    indexes.append(None)
    for i, j in zip(indexes, indexes[1:]):
        sliceAccounts = userids[i:j]
        try:
            print INFO + 'Authenticating Token #' + str(currentToken) + RESET
            twitter_app_auth = {
            'consumer_key': consumer_key,
            'consumer_secret': consumer_secret,
            'access_token': tokens[currentToken][0],
            'access_token_secret': tokens[currentToken][1]
            }
        except IndexError:
            print ERROR + 'No Tokens Available Anymore' + RESET
            exit()
        currentToken += 1
        bom = botometer.Botometer(mashape_key=mashape_key, **twitter_app_auth)
        print INFO + 'Fetching ' + str(len(sliceAccounts)) + ' accounts' + RESET
        try:
            results = list(bom.check_accounts_in(sliceAccounts))
        except requests.exceptions.HTTPError, e:
            print ERROR + 'Error During Requests' + RESET
            print e
            exit()
        print INFO + 'Saving Scores' + RESET
        for r in results:
            data = r[1]
            if 'user' not in data:
                data['user'] = {'id_str':r[0]}
            json.dump(data, outputfile)
            outputfile.write('\n')






















# END
