# -*- coding: utf-8 -*-

import csv
import sys
import json
import colorama
import datetime
from tqdm import tqdm

INFO = colorama.Fore.BLACK + colorama.Back.GREEN + '[INFO] '
WARNING = colorama.Fore.BLACK + colorama.Back.YELLOW + '[WRNG] '
ERROR = colorama.Fore.BLACK + colorama.Back.RED + '[ERROR] '
RESET = colorama.Fore.RESET + colorama.Back.RESET

def loadJSON(filename='SpatiotemporalTraceExporter.json'):
	inputfile = open(filename, 'r')
	data = json.load(inputfile)
	return data

def loadTotalLines(inputfilename):
	"""
		Counts the number of lines of file.
	"""
	inputfile = open(inputfilename, 'rb')
	for nrows, l in tqdm(enumerate(inputfile), desc='Counting Lines', leave=False):
		pass
	nrows += 1
	inputfile.close()
	return nrows

def loadCityInfo(city, filename='CityInfo.json'):
	"""
		Load the city boundingbox information from external file
	"""
	data = json.load(open(filename, 'r'))
	return data['data'][city]

def saveWeeklyFiles(inputfilenames, bbox):
	"""
		Exports datasets using one line for each sample
		defined as a JSON object.
		This method saves temporary files for each week according
		to the bbox indicated.
	"""
	countLines = False
	outputfilePattern = city + '-%Y-%U-%B.json'
	datePattern = '%Y-%m-%d %H:%M:%S'
	deleteKeys = ['lang', 'date_original', 'app', 'place_name', 'date_local']
	deleteKeys += ['app_url', 'place_url', 'dataset_curator']
	deleteKeys += ['place_type', 'weekday', 'passive_collect']

	lng0, lngn = sorted([bbox[0], bbox[2]])
	lat0, latn = sorted([bbox[1], bbox[3]])
	for inputfilename in inputfilenames:
		print WARNING + 'Save Weeks: ' + inputfilename + RESET
		# fixing the problem of latitude and longitude inverted
		latKey = 'lat'
		lngKey = 'lng'
		if 'instagram' in inputfilename or 'foursquare' in inputfilename:
			print WARNING + ' lat and lng coords are inverted!' + RESET
			latKey = 'lng'
			lngKey = 'lat'
		dataset = list()
		if countLines:
			nrows = loadTotalLines(inputfilename)
		else:
			nrows = None
		inputfile = open(inputfilename, 'r')
		firstLine = eval(inputfile.readline()[:-1])
		lastWeek = firstLine['date_original'].strftime('%U')
		outputfilename = firstLine['date_original'].strftime(outputfilePattern)
		inputfile.seek(0)
		for line in tqdm(inputfile, desc='Loading', total=nrows):
			try:
				data = eval(line[:-1])
			except Exception:
				continue
			# check if sample is inside the bbox
			lng = float(data[lngKey])
			lat = float(data[latKey])
			if lng < lng0 or lng > lngn or lat < lat0 or lat > latn:
				continue
			# prepare the sample
			data['agent'] = data['app_url']
			data['lat'] = lat
			data['lng'] = lng
			data['urls'] = [url['expanded_url'] for url in data['urls']]
			data['hashtags'] = [tag['text'] for tag in data['hashtags']]
			dateutc = data['date_local']
			currentWeek = dateutc.strftime('%U')
			data['date_utc'] = dateutc.strftime(datePattern)
			for k in deleteKeys:
				del data[k]
			# saving the samples in a new file
			if currentWeek != lastWeek:
				if countLines:
					print '' # small fix for exibition
				print INFO + 'Saving temp file ' + outputfilename, 'with', len(dataset), 'samples...' + RESET
				outputfile = open(outputfilename, 'a')
				for sample in dataset:
					json.dump(sample, outputfile)
					outputfile.write('\n')
				dataset = list()
				outputfile.close()
				outputfilename = dateutc.strftime(outputfilePattern)
				lastWeek = currentWeek
			dataset.append(data)
		inputfile.close()
	return dataset

def sortWeeklyFiles(inputfilenames):
	"""
		Sort the samples stored in the files and exported from saveWeeklyFiles.
	"""
	for inputfilename in inputfilenames:
		print INFO + 'Sort Samples: ' + inputfilename + RESET
		invalidSample = 0
		dataset = list()
		nrows = loadTotalLines(inputfilename)
		inputfile = open(inputfilename, 'r')
		for line in tqdm(inputfile, desc='Loading', total=nrows, leave=False):
			try:
				sample = json.loads(line)
			except Exception:
				invalidSample += 1
			dataset.append(sample)
		if invalidSample:
			print ERROR + str(invalidSample) + ' invalid samples.' + RESET
		keys = [sample['id_data'] for sample in dataset]
		s = set(keys)
		if len(keys) != len(s):
			print WARNING + str(len(keys) - len(s)) + ' duplicated samples.' + RESET
			temp = dict()
			for sample in dataset:
				temp[sample['id_data']] = sample
			sortedSamples = sorted(temp, key=lambda k:temp[k]['date_utc'])
			dataset = [temp[k] for k in sortedSamples]
		else:
			dataset = sorted(dataset, key=lambda k:k['date_utc'])
		filename = inputfilename.replace('.json', '-twitter.json')
		print INFO + 'Saving file: ' +  filename + RESET
		outputfile = open(filename, 'w')
		for sample in tqdm(dataset, desc='Saving'):
			json.dump(sample, outputfile)
			outputfile.write('\n')
		outputfile.close()
	return

def saveUserCoords(inputfilenames, city):
	'''
		Saves external files couting the coords visitiedfor each user.
		The files corresponds to JSON objects (each line) with userid and
		a dict of coords and its occurrences.
	'''
	dictUsers = dict()
	for inputfilename in inputfilenames:
		print INFO + 'Users Coords: ' + inputfilename + RESET
		inputfilename = 'data/' + inputfilename
		nrows = loadTotalLines(inputfilename)
		inputfile = open(inputfilename, 'r')
		for line in tqdm(inputfile, desc='Loading', total=nrows, leave=False):
			try:
				sample = json.loads(line)
			except Exception:
				invalidSample += 1
			userid = sample['userid']
			coords = str((sample['lat'], sample['lng']))
			try:
				dictUsers[userid][coords] += 1
			except KeyError:
				if userid not in dictUsers:
					dictUsers[userid] = {coords:1}
					continue
				dictUsers[userid][coords] = 1
	outputfilename = 'data/' + city + '-user-coords.json'
	outputfile = open(outputfilename, 'w')
	for u in tqdm(dictUsers, desc='Saving'):
		data = dictUsers[u]
		data = {'userid':u, 'coords':data}
		json.dump(data, outputfile)
		outputfile.write('\n')
	return

if __name__ == "__main__":
	# TODO add argparser
	# func is mandatory
	# city is mandatory when func = save
	# inputfiles are mandatory when func = sort

	configFilename = 'SpatiotemporalTraceExporter.json'
	try:
		args = sys.argv[1:]
		func = args.pop(0)
	except Exception:
		print ERROR + 'Please provide a valid cmd line: python SpatiotemporalTraceExporter.py func args' + RESET
		exit()

	if func == 'save':
		city = args.pop(0)
		config = loadJSON(filename=configFilename)
		inputfilenames = config['raw']['instagram'] + inputfiles['raw']['foursquare']
		try:
			inputfilenames = config['raw'][city] + inputfilenames
		except KeyError:
			print WARNING + city + ' has no specific inputfiles!' + RESET
		cityInfo = loadCityInfo(city, filename='CityInfo.json')
		saveWeeklyFiles(inputfilenames, cityInfo['bbox'])
	elif func == 'sort':
		inputfiles = args
		sortWeeklyFiles(inputfiles)
	elif func == 'coords':
		city = args.pop(0)
		config = loadJSON(filename=configFilename)
		inputfilenames = config['traces'][city]
		saveUserCoords(inputfilenames, city)
	else:
		print ERROR + 'No function to execute!' + RESET














	# END
