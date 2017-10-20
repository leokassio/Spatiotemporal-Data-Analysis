# -*- coding: utf-8 -*-
# ==============================================================================
# Kassio Machado - 2017-09-15
# PhD candidate on Science Computing - uOttawa/Canada and UFMG/Brazil
# Crawler to visit request Instagram API looking for places according to the
# placeid provided by Facebook.
# The goal is consolidate the datasets of places from Instagram and Facebook.
# This code was created for scientific research purpose only.
# ==============================================================================

import sys
import time
import json
import numpy
import argparse
import requests
import colorama
from tqdm import tqdm

ERROR = colorama.Fore.RED + '[ERROR] '
RESET = colorama.Fore.RESET
INFO = colorama.Fore.GREEN + '[INFO] '
WRNG = colorama.Fore.YELLOW + '[WARNING] '

def loadJSONFile(filename):
    inputfile = open(filename, 'r')
    data = json.load(inputfile)
    return data

def loadOAuthCredentials(filename='InstagramConfig.json'):
    datajson = loadJSONFile(filename)
    credentials = list()
    for app in datajson['instagram_apps']:
        for accounts in app['credentials']:
            c = (app['client_id'], accounts['access_token'], app['name'], accounts['login'])
            credentials.append(c)
    return credentials

def loadPlacesDefined(filename):
    invalidLines = 0
    facebookPlacesDefined = set() # places already defined
    instagramPlacesDefined = set() # places with match
    try:
        outputfile = open(filename, 'r')
        for line in outputfile:
            try:
                objson = json.loads(line)
                facebookPlacesDefined.add(objson['id_facebook'])
                instagramPlacesDefined.add(objson['instagram']['id_instagram'])
            except ValueError:
                invalidLines += 1
                pass
        print INFO + str(len(facebookPlacesDefined)) + ' places already defined!' + RESET
        if invalidLines:
            print WRNG + str(invalidLines) + ' invalid JSON objects (lines).' + RESET
    except IOError:
        print WRNG + 'No file previously stablished!' + RESET
    return facebookPlacesDefined, instagramPlacesDefined

def loadFacebookPlaces(filename, facebookPlacesDefined, instagramPlacesDefined):
    noCandidates = 0
    placesUniverse = set()
    placesList = list()
    inputfile = open(filename, 'r')
    for line in tqdm(inputfile, desc='Loading Inputfile', disable=False):
        data = json.loads(line)
        try:
            candidates = data['facebook']['data']
        except KeyError:
            noCandidates += 1
            continue
        for c in candidates:
            placeidInstagram = data['instagram'].split('/locations/')[1].split('/')[0]
            if placeidInstagram not in instagramPlacesDefined and c['id'] not in facebookPlacesDefined:
                c['id_facebook'] = c['id']
                del c['id']
                c['country'] = data['country']
                c['instagram_candidate'] = {'coords':data['coords'],
                                            'name':data['name'],
                                            'link':data['instagram'],
                                            'id_instagram':placeidInstagram}
                for categ in c['category_list']:
                    categ['id_category'] = categ['id']
                    del categ['id']
                placesUniverse.add(c['id_facebook'])
                placesList.append(c)
    if noCandidates:
        print WRNG + str(noCandidates) + ' Instagram places without Facebook candidates.' + RESET
    print INFO + str(len(placesUniverse)) + ' Facebook places to check!' + RESET
    return placesUniverse, placesList

def main():
    desc = 'Facebook & Instagram Place Crawler - Explores the Facebook Places \
    API. It requires an input file formated as JSON with name to query the \
    Facebook ID of places in Instagram location API.\
    In addition a second file with Facebook OAuth credentials.'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('inputfilename',
                        help='Lines formated in JSON. Must provide the facebook\
                        place ID to query.')
    parser.add_argument('--output', metavar='filename',
                        default='places-database.json',
                        help='File for output.')
    parser.add_argument('--config', metavar='filename',
                        default='InstagramConfig.json',
                        help='File with OAuth credentials of Instagram API.')
    parser.add_argument('--rate', metavar='limit',
                        default=500,
                        help='Rate limit of app in Instagram API.')
    if len(sys.argv) == 1:
        parser.print_help()
        exit()
    else:
        args = parser.parse_args()

    config = args.config # 'InstagramConfig.json'
    rateLimitReamining = args.rate # 500
    inputfilename = args.inputfilename # '../data/places-database/paris-places-database-facebook.json'
    outputfilename = args.output # '../data/places-database/paris-places-instagram-facebook.json'

    verbose = True
    credentialIndex = 0
    placesMatch = set()
    facebookPlacesDefined, instagramPlacesDefined = loadPlacesDefined(outputfilename)
    placesUniverse, placesList = loadFacebookPlaces(inputfilename, facebookPlacesDefined, instagramPlacesDefined)

    credentials = loadOAuthCredentials(config)
    client_id = credentials[credentialIndex][0]
    access_token = credentials[credentialIndex][0]
    url = 'https://api.instagram.com/v1/locations/search'

    outputfile = open(outputfilename, 'a', 0)

    # Requesting Instagram API.
    for facebookCandidate in tqdm(placesList, desc='Loading', disable=False):
        if rateLimitReamining <= 1:
            print WRNG + 'Rate Limit Reached!' + RESET
            if credentialIndex < (len(credentials) - 1):
                credentialIndex += 1
            else:
                credentials = loadOAuthCredentials(config) # reloading credentials
                credentialIndex = 0
                for t in tqdm(range(0, 5), desc='Waiting', leave=False):
                    time.sleep(60)
            client_id = credentials[credentialIndex][0]
            access_token = credentials[credentialIndex][1]
            rateLimitReamining = 500
            print INFO + 'Using credentials: ' + str(credentials[credentialIndex]) + RESET

        if facebookCandidate['instagram_candidate']['id_instagram'] in instagramPlacesDefined:
            print WRNG + 'Jumping Facebook candidate ' + facebookCandidate['instagram_candidate']['id_instagram'] + RESET
            continue
        if facebookCandidate['id_facebook'] in facebookPlacesDefined:
            print INFO + 'Done ' + facebookCandidate['id_facebook'] + RESET
            continue
        reqs = '[' + str(rateLimitReamining) + ']'
        print reqs + 'Requesting', facebookCandidate['id_facebook'], 'for',\
              facebookCandidate['instagram_candidate']['link']
        payload = dict()
        payload['access_token'] = access_token
        payload['facebook_places_id'] = facebookCandidate['id_facebook']
        try:
            resp = requests.get(url, params=payload)
        except requests.exceptions.ConnectionError, e:
            print 'Connection error!'
            print e
            for i in range(300, desc='Waiting', dynamic_ncols=True):
                time.sleep(1)
        try:
            rateLimitReamining = int(resp.headers['x-ratelimit-remaining'])
            rjson = json.loads(resp.content)
            placeFetched = rjson['data']
        except ValueError: # invalid JSON
            print ERROR + 'Invalid JSON.' + RESET
            continue
        except KeyError:
            print ERROR + 'Error reading header of request.' + RESET
            rateLimitReamining = 0
            continue

        if len(placeFetched) == 0:
            print WRNG + 'No Instagram candidate for ' + \
            facebookCandidate['id_facebook'] + RESET
            facebookCandidate['instagram'] = None
            del facebookCandidate['instagram_candidate']
            print ERROR + 'Miss: ' + facebookCandidate['link'] + RESET
        elif len(placeFetched) > 1:
            print ERROR + 'More than one candidate!' + RESET
            exit()
        else:
            placeFetched = placeFetched[0]
            placeFetched['id_instagram'] = placeFetched['id']
            del placeFetched['id']
            placeFetched['link'] = 'https://www.instagram.com/explore/locations/' +\
            placeFetched['id_instagram']
            facebookCandidate['instagram'] = placeFetched
            if placeFetched['id_instagram'] == facebookCandidate['instagram_candidate']['id_instagram']:
                print INFO + 'Match: ' + placeFetched['link'] + ' & ' + facebookCandidate['link'] + RESET
            else:
                print 'Fetch: ' + placeFetched['link'] + ' & ' + facebookCandidate['link']
            instagramPlacesDefined.add(placeFetched['id_instagram'])
            del facebookCandidate['instagram_candidate']
        json.dump(facebookCandidate, outputfile, sort_keys=True)
        outputfile.write('\n')
        time.sleep(0.25) # numpy.random.random()

if __name__ == "__main__":
	main()
































# END
