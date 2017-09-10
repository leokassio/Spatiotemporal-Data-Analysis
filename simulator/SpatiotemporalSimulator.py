# -*- coding: utf-8 -*-

import csv
import sys
import math
import json
import datetime
import colorama
import pandas as pd
from tqdm import tqdm

INFO = colorama.Fore.BLACK + colorama.Back.GREEN + '[INFO] '
WARNING = colorama.Fore.BLACK + colorama.Back.YELLOW + '[WRNG] '
ERROR = colorama.Fore.BLACK + colorama.Back.RED + '[ERROR] '
RESET = colorama.Fore.RESET + colorama.Back.RESET

def loadConfig(filename='SpatiotemporalSimulator.json'):
	try:
		inputfile = open(filename, 'r')
	except Exception, e:
		print ERROR + 'Exception on config file loading' + RESET
		print str(e)
		exit()
	config = json.load(inputfile)
	return config

def distanceCoords(lat1, long1, lat2, long2):
	"""
		Calculates the distance among two points defined by GPS coord
	"""
	try:
		# Convert latitude and longitude to
		# spherical coordinates in radians.
		degrees_to_radians = math.pi/180.0
		phi1 = (90.0 - lat1)*degrees_to_radians
		phi2 = (90.0 - lat2)*degrees_to_radians
		theta1 = long1*degrees_to_radians
		theta2 = long2*degrees_to_radians
		cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) +
			   math.cos(phi1)*math.cos(phi2))
		arc = math.acos( cos )
		return arc * 6373000.0 # return in meters
	except ValueError:
		return 0.01 # in case of very very very close

def loadTotalRows(inputfilename):
	"""
		Count the number of lines of inputfile
	"""
	# print INFO + 'Counting rows' + RESET
	inputfile = open(inputfilename, 'rb')
	for nrows, l in tqdm(enumerate(inputfile), desc='Counting Lines', leave=False):
		pass
	nrows += 1
	inputfile.close()
	return nrows

def createOutputfile(outputfilename):
	'''
		Preparation of outputfile
	'''
	fileHeader = {'date_utc':'UTC Date and Time @Twitter',
			'userid1':'ID user (int) @Twitter',
			'userid2':'ID user (int) @Twitter',
			'interval':'Interval among samples',
			'distance':'Distance among GPS coords',
			'lat':'GPS latitude', 'lng':'GPS longitude',
			'id_data1':'ID of tweet', 'id_data2':'ID of tweet',
			'country':'Country @Twitter',
			'content':'Intersection of meta on tweet (URL and hashtags)'}
	outputfile = open(outputfilename, 'w')
	json.dump(fileHeader, outputfile)
	outputfile.write('\n')
	return outputfile

def saveEdges(edges, currentOut, outputfile=None):
	for data in edges:
		out = data.pop('out')
		if out != currentOut or outputfile == None:
			currentOut = out
			tempname = outputfilename.replace('.json', '-' + out + '.json')
			print WARNING +  'Saving file ' + tempname + RESET
			if outputfile:
				outputfile.close()
			outputfile = createOutputfile(tempname)
		json.dump(data, outputfile)
		outputfile.write('\n')
	outputfile.flush()
	return currentOut, outputfile

def runSimulation(inputfilenames, outputfilename, maxInterval=900,
					maxDistance=150, name=None, desc=None, bufferOutSize=10000):
	"""
		Computes the encounters among samples according to thethresholds of
		distance  and interval
	"""
	currentOut = '' # keep the last week saved
	outputfile = None
	dateFormat = '%Y-%m-%d %H:%M:%S'
	bufferOut = list()
	nfiles = len(inputfilenames)
	trace = list()
	for inputfileindex, inputfilename in enumerate(inputfilenames):
		inputfileindex += 1
		filesCounter = '(' + str(inputfileindex) + '/' + str(nfiles) + ')'
		print INFO + 'Loading file ' + inputfilename + ' ' + filesCounter  + RESET
		lastFile = False if inputfileindex != nfiles else True
		nrows = loadTotalRows(inputfilename)
		try:
			inputfile = open(inputfilename, 'r')
		except IOError:
			print ERROR + 'File not found!' + RESET
			continue
		for line in tqdm(inputfile, desc='Loading', total=nrows, leave=False):
			# TODO insert a limit of rows (page limit) for buffering
			sample = json.loads(line)
			sample['datetime'] = datetime.datetime.strptime(sample['date_utc'], dateFormat)
			sample['contents'] = set(sample['urls'] + [t.lower() for t in sample['hashtags']])
			try:
				app = sample['agent'].split('>')[1].split('<')[0]
				sample['contents'].add(app)
			except IndexError:
				pass
			trace.append(sample)
		pbar = tqdm(desc='Simulating', leave=True, total=len(trace), dynamic_ncols=True)
		for i, s1 in enumerate(trace): # tqdm(enumerate(trace), total=len(trace), desc='Simulating', leave=False, disable=True):
			# Preparing the data from current sample
			pbar.update(1)
			uid = s1['userid']
			datejson = s1['date_utc']
			date_utc = s1['datetime']
			out = date_utc.strftime('%Y-%U')
			lat = s1['lat']
			lng = s1['lng']
			country = s1['country']
			id_data = s1['id_data']
			contents = s1['contents']
			s2 = trace[-1]
			# Testing if the last sample of page comparable to 1st sample
			interval = (s2['datetime'] - date_utc).total_seconds()
			if interval <= maxInterval and not lastFile:
				pbar.close()
				# print WARNING + 'Fetching data in the next file' + RESET
				sliceTrace = i
				break
			sliceTrace = i + 1
			for j in xrange(i + 1, len(trace)):
				s2 = trace[j]
				if uid != s2['userid']:
					interval = (s2['datetime'] - date_utc).total_seconds()
					if interval <= maxInterval:
						dist = distanceCoords(lat, lng, s2['lat'], s2['lng'])
						if dist <= maxDistance:
							intersec = list(contents.intersection(s2['contents']))
							edge = {'date_utc':datejson, 'userid1':uid,
									'userid2':s2['userid'], 'interval':int(interval),
									'distance':int(dist), 'lat':lat, 'lng':lng,
									'id_data1':id_data, 'id_data2':s2['id_data'],
									'country':country, 'content':intersec,
									'out':out}
							bufferOut.append(edge)
					else:
						break
				else:
					continue
			if len(bufferOut) >= bufferOutSize:
				currentOut, outputfile = saveEdges(bufferOut, currentOut, outputfile)
				bufferOut = list() # restart buffer
		trace = trace[sliceTrace:]
	saveEdges(bufferOut, currentOut, outputfile) # flush of buffer

def logo():
	color = colorama.Fore.RED
	print color + ''
	print '_______  _____  _______ _______ _____  _____  _______ _______ _______  _____ '
	print '|______ |_____] |_____|    |      |   |     |    |    |______ |  |  | |_____]'
	print '______| |       |     |    |    __|__ |_____|    |    |______ |  |  | |      '
	print ''
	print '_______ _____ _______ _     _        _______ _______  _____   ______'
	print '|______   |   |  |  | |     | |      |_____|    |    |     | |_____/'
	print '______| __|__ |  |  | |_____| |_____ |     |    |    |_____| |    \\_'
	print '' + RESET
	return

if __name__ == "__main__":
	logo()
	args = sys.argv
	try: # new version
		config = args[1]
		configs = loadConfig(filename='SpatiotemporalSimulator.json')
		scenarioConfig = configs[config]
		name = scenarioConfig['name']
		desc = scenarioConfig['description']
		maxInterval = scenarioConfig['max_interval']
		maxDistance = scenarioConfig['max_distance']
		inputfilenames = scenarioConfig['traces']
		outputfilename = scenarioConfig['outputfile']
	except IndexError:
		print ERROR + 'Please provide a valid cmd line' + RESET
		print ERROR + 'ex: python EncounterSimulatorTwitter.py scenario-name' + RESET
		exit()
	except KeyError, e:
		print e
		print ERROR + 'Invalid scenario, please check SpatiotemporalSimulator.json' + RESET
		exit()
	runSimulation(inputfilenames, outputfilename, maxInterval, maxDistance, name, desc)













	# END
