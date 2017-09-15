# -*- coding: utf-8 -*-

import csv
import sys
import json
import argparse
import colorama
import requests
import datetime
import botometer # https://github.com/IUNetSci/botometer-python ICWSM
import tweepy.error
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
    desc = INFO
    desc += 'TwitterMonitor tool to compute the bot scores of twitter accounts.\
     It requires (1) an additional configuration file with Twitter OAuth \
    credentials and (2) an external file with users data to sort them and \
    identify super users. OBS (Botometer computes the scores)' + RESET
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('token', default='0',
                        help='OAuth token index as provided in \
                        TwitterMonitorConfig.json to be used for \
                        Twitter API calls')
    parser.add_argument('inputfilename', metavar='filename',
                        help='Inputfile (JSON formated) with twitter user ids.')
    parser.add_argument('-s', '--samples', default=300,
                        metavar='value',
                        help='Min of samples per users to be checked - \
                        default 300.')
    parser.add_argument('-c', '--config', default='TwitterMonitorConfig.json',
                        metavar='filename',
                        help='Config file (formated as JSON) - default\
                        TwitterMonitorConfig.json.')
    if len(sys.argv) == 1: # if no arguments, then present the help
        parser.print_help()
        exit()
    else:
        args = parser.parse_args()

    token = int(args.token)
    inputfilename = args.inputfilename
    minSamples = int(args.samples)
    configfilename = args.config

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
        if sum(sample['coords'].values()) > minSamples:
            # print 'checking: https://twitter.com/intent/user?user_id=' + sample['userid']
            if sample['userid'] not in usersDefined:
                userids.append(sample['userid'])
    if invalidSamples:
        print ERROR + 'Invalid Samples: ' + str(invalidSamples)

    outputfile = open(outputfilename, 'a' , 0)
    print INFO + 'Checking ' + str(len(userids)) + ' Accounts' + RESET

    tokenCounter = 0
    for i in tqdm(range(len(userids)), desc='Botomering'):
        uid = userids[i]
        if tokenCounter >= 100:
            token += 1
            tokenCounter = 0
            print INFO + 'Using Token #' + str(token) + RESET
        if tokenCounter == 0:
            twitter_app_auth = {
            'consumer_key': consumer_key,
            'consumer_secret': consumer_secret,
            'access_token': tokens[token][0],
            'access_token_secret': tokens[token][1]
            }
            bom = botometer.Botometer(mashape_key=mashape_key, **twitter_app_auth)
        try:
            data = bom.check_account(uid)
            if 'user' not in data:
                print data
                data['user'] = {'id_str':uid}
            json.dump(data, outputfile)
            outputfile.write('\n')
        except requests.exceptions.HTTPError, e:
            print WARNING + 'Error Requesting ' + uid + RESET
            print ERROR + str(e) + RESET
        except tweepy.error.TweepError, e:
            # In case of user deleted or privacy settings changed
            msg = str(e)
            if 'Not authorized' in msg or 'that page does not exist' in msg:
                data = {'user': {'id_str': uid}, 'error':msg}
                json.dump(data, outputfile)
                outputfile.write('\n')
            else:
                print ERROR + str(e) + RESET
                print WARNING + 'https://twitter.com/intent/user?user_id=' + uid + RESET
        except botometer.NoTimelineError, e:
            data = {'user': {'id_str': uid}, 'error':str(e)}
            json.dump(data, outputfile)
            outputfile.write('\n')
        tokenCounter += 1







# END
