# -*- coding: utf-8 -*-
import csv
import math
import time
import numpy
from tqdm import tqdm

# This is a simple modification.
def normalizeMax(dataList, maxValue):
	values = []
	maxValue = float(maxValue)
	for x in dataList:
		try:
			v = x/maxValue
		except ZeroDivisionError:
			v = 0
		values.append(v)
	return values


def roundMetric(metric, offset):
	metric = int(math.ceil(metric/offset)*offset)
	return metric

def loadInstagramPlaces(inputfiles, completeName=True, allSamples=True, verbose=False):
	"""
		Loads the files of resolved urls which indicate the place
		where the photos were taken. It returns a dict where the keys
		are the id of tweet and items are the urls of places,
		without the url base.
	"""
	urlBase = 'https://www.instagram.com/explore/locations/'
	dictSamples = dict()
	for filename in inputfiles:
		if completeName:
			filename = filename.replace('.csv', '-resolved.csv')
		f = open(filename, 'r')
		nlines = 0
		for i in f:
			nlines += 1
		f.seek(0)
		reader = csv.reader(f)
		for data in tqdm(reader, total=nlines, disable=True):
			if allSamples or data[2] != 'not-available':
				urlPlace = data[2].replace(urlBase, '')
				placeName = data[3]
				dictSamples[data[0]] = (urlPlace, placeName)
		alias = filename.split('/')[-1]
		if verbose:
			print 'Load:', alias, len(dictSamples), 'Samples'
	if verbose:
		print 'Done! Total Samples:', len(dictSamples)
	return dictSamples

def loadDataInstagram(inputfiles, dataInstagramURL):
    """
        Loads the original files of URLs and combine the data
        with resolved URLs. Requires the preloaded data from resolved
        URLS.
    """
    dataInstagram = dict()
    for filename in inputfiles:
        alias = filename.split('/')[-1]
        print BLUE, 'Load:', alias, RESET
        f = open(filename, 'r')
        nlines = 0
        for i in f:
            nlines += 1
        f.seek(0)
        reader = csv.reader(f)
        for data in tqdm(reader, total=nlines, disable=True):
            try:
                urlPlace, placeName = dataInstagramURL[data[0]]
            except KeyError:
                # KeyError in case of sample not available or not resolved
                continue
            except ValueError:
                # ValueError in case of duplicated sample lines
                continue
            try:
                dataInstagram[data[0]] = (data[6], urlPlace, placeName, data[1])
                # (dateTime, urlPlace, placeName, idUser)
            except IndexError:
                print RED, 'CORRUPTED LINE!', RESET
                print data
                return
    print GREEN, 'Done!', RESET
    return dataInstagram

def getInstagramFilenames():


def getInstagramFilenames():
	instagramFiles = {
		'New-York':['data/2016-06-16-tweets-instagram-url-NEW_YORK.csv',
		'data/2016-07-11-tweets-instagram-url-NEW_YORK.csv',
		'data/2016-08-05-tweets-instagram-url-NEW_YORK.csv',
		'data/2016-08-18-tweets-instagram-url-NEW_YORK.csv',
		'data/2016-09-12-tweets-instagram-url-NEW_YORK.csv',
		'data/2016-10-05-tweets-instagram-url-NEW_YORK.csv',
		'data/2016-11-07-tweets-instagram-url-NEW_YORK.csv',
		'data/2016-12-04-tweets-instagram-url-NEW_YORK.csv',
		'data/2016-12-14-tweets-instagram-url-NEW_YORK.csv',
		'data/2017-01-09-tweets-instagram-url-NEW_YORK.csv',
		'data/2017-02-15-tweets-instagram-url-NEW_YORK.csv',
		'data/2017-03-17-tweets-instagram-url-NEW_YORK.csv',
		'data/2017-03-19-tweets-instagram-url-NEW_YORK.csv',
		'data/2017-04-17-tweets-instagram-url-NEW_YORK.csv',
		'data/2017-05-15-tweets-instagram-url-NEW_YORK.csv'],
		'London':['data/2016-06-16-tweets-instagram-url-LONDON.csv',
		'data/2016-07-11-tweets-instagram-url-LONDON.csv',
		'data/2016-08-05-tweets-instagram-url-LONDON.csv',
		'data/2016-08-18-tweets-instagram-url-LONDON.csv',
		'data/2016-09-12-tweets-instagram-url-LONDON.csv',
		'data/2016-10-05-tweets-instagram-url-LONDON.csv',
		'data/2016-11-07-tweets-instagram-url-LONDON.csv',
		'data/2016-12-04-tweets-instagram-url-LONDON.csv',
		'data/2016-12-14-tweets-instagram-url-LONDON.csv',
		'data/2017-01-09-tweets-instagram-url-LONDON.csv',
		'data/2017-02-15-tweets-instagram-url-LONDON.csv',
		'data/2017-03-17-tweets-instagram-url-LONDON.csv',
		'data/2017-03-19-tweets-instagram-url-LONDON.csv',
		'data/2017-04-17-tweets-instagram-url-LONDON.csv',
		'data/2017-05-15-tweets-instagram-url-LONDON.csv']}
	return instagramFiles


if __name__ == "__main__":
	city = 'London'
	instagramFilenames = getInstagramFilenames()
	dataURL = loadFetchedURL(instagramFilenames[city])
	dataSamples = mergeSamplesURL(instagramFiles[city], dataURL)
