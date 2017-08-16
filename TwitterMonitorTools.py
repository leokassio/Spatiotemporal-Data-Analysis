# -*- coding: utf-8 -*-
# ============================================================================================
# Kassio Machado - GNU Public License - 2017-07-01 Happy Canada Day
# PhD candidate on Science Computing - UFMG/Brazil
# ============================================================================================

import csv
import sys
import colorama
import datetime
from tqdm import tqdm
import TwitterMonitor

def exportStatsCountryPlaces(inputfiles):
	"""
	Count the samples and group them according to the places indicated by
	Twitter sample (not dependent of app - like Instagram of Foursquare). The
	method exports two CSV files for each input file containing the places and
	countries.
	"""
	for filename in inputfiles:
		dataPlaces, dataCountries = TwitterMonitor.loadPlaceStats(filename)
		outputfilename = filename.replace('.csv', '-countries.csv')
		print colorama.Fore.RED, 'Saving CSV countries\' file', filename, colorama.Fore.RESET
		writer = csv.writer(open(outputfilename, 'w'))
		writer.writerow(['country','samples'])
		for c in sorted(dataCountries.keys(), key=lambda k:dataCountries[k], reverse=True):
			writer.writerow([c, dataCountries[c]])

		outputfilename = filename.replace('.csv', '-places.csv')
		print colorama.Fore.RED, 'Saving CSV places\' file', outputfilename, colorama.Fore.RESET
		writer = csv.writer(open(outputfilename, 'w'))
		writer.writerow(['url','place_class', 'country', 'place_name', 'samples'])
		for p in sorted(dataPlaces.keys(), key=lambda k:dataPlaces[k][4], reverse=True):
			writer.writerow(dataPlaces[p])

def exportPlaceURL(inputfiles):
	"""
	Export samples' places info and URL
	independently of city and country.
	"""
	for filename in inputfiles:
		print colorama.Fore.RED, filename, colorama.Fore.RESET
		inputfile = open(filename, 'r')
		outputfile = open(filename.replace('.csv', '-url.csv'), 'w', 0)
		lineBuffer = list()
		invalidSample = 0
		for line in tqdm(inputfile, desc='Exporting URL\'s', disable=False):
			try:
				sample = eval(line.replace('\n', ''))
				id_data = sample['id_data'].encode('utf-8')
				id_user = sample['userid'].encode('utf-8')
				country = sample['country'].encode('utf-8')
				url = sample['urls'][-1]['expanded_url'].encode('utf-8')
				place_url = sample['place_url'].encode('utf-8')
				place_name = sample['place_name'].encode('utf-8')
				date_local = sample['date_local']
				lat = sample['lng']
				lng = sample['lat']
				line = id_data
				line += ',' + id_user
				line += ',' + country
				line += ',' + url
				line += ',' + place_url
				line += ',' + place_name.replace(',', ';')
				line += ',' + date_local.strftime('%y-%m-%d %H:%M:%S')
				line += ',' + lat
				line += ',' + lng
				line += '\n'
				lineBuffer.append(line)
				if lineBuffer >= 100000:
					for l in lineBuffer:
						outputfile.write(l)
					lineBuffer = list()
			except KeyError:
				invalidSample += 1
				continue
			except SyntaxError:
				invalidSample += 1
				continue
		for l in lineBuffer:
			outputfile.write(l)
		print '#' + str(invalidSample),'Invalid Samples'

def exportPlaceURLByCountry(isoCodeCountry, inputfiles):
	"""
	Filters the fields and exports in CSV files the information related to the
	samples' venues, such as place name, place type, country, Twitter URL of place,
	and Instagram URL of the sample, according to the country code indicade
	according to the ISO Alpha-2
	"""
	print colorama.Fore.CYAN, 'Exporting files with URLs from', isoCodeCountry, colorama.Fore.RESET
	for filename in inputfiles:
		print colorama.Fore.RED, filename, colorama.Fore.RESET
		inputfile = open(filename, 'r')
		outputfile = open(filename.replace('.csv', '-url-' + isoCodeCountry.upper() + '.csv'), 'w')
		lineBuffer = list()
		invalidSample = 0
		for line in tqdm(inputfile, desc='Collecting URL\'s'):
			try:
				sample = eval(line.replace('\n', ''))
				country = sample['country'].upper()
				if country != isoCodeCountry:
					continue
				id_data = sample['id_data'].encode('utf-8')
				id_user = sample['userid'].encode('utf-8')
				country = sample['country'].encode('utf-8')
				url = sample['urls'][-1]['expanded_url'].encode('utf-8')
				place_url = sample['place_url'].encode('utf-8')
				place_name = sample['place_name'].encode('utf-8')
				date_local = sample['date_local']
				lat = sample['lng']
				lng = sample['lat']
				line = id_data
				line += ',' + id_user
				line += ',' + country
				line += ',' + url
				line += ',' + place_url
				line += ',' + place_name.replace(',', ';')
				line += ',' + date_local.strftime('%y-%m-%d %H:%M:%S')
				line += ',' + sample['lng']
				line += ',' + sample['lat']
				line += '\n'
				lineBuffer.append(line)
				if lineBuffer >= 25000:
					for l in lineBuffer:
						outputfile.write(l)
					lineBuffer = list()
			except KeyError:
				invalidSample += 1
				continue
			except SyntaxError:
				invalidSample += 1
				continue
		for l in lineBuffer:
			outputfile.write(l)

def exportPlaceURLByBoundBox(locationName, inputfiles, configFilename='TwitterMonitor.cfg'):
	"""
	Exports the files containing the URLs from samples locations according
	to Instagram. The function requires the pre-defined bounding box on
	TwitterMonitor.cfg.
	"""

	configparser = TwitterMonitor.loadConfigParser(configFilename)
	coords = TwitterMonitor.loadBoundBox(configparser, locationName)
	lng0, lngn = sorted([coords[0], coords[2]])
	lat0, latn = sorted([coords[1], coords[3]])
	print lat0, latn, lng0, lngn
	print colorama.Fore.CYAN, 'Exporting files with URLs from', locationName, colorama.Fore.RESET
	for filename in inputfiles:
		print colorama.Fore.RED, filename, colorama.Fore.RESET
		inputfile = open(filename, 'r')
		outputfile = open(filename.replace('.csv', '-url-' + locationName.upper() + '.csv'), 'w')
		lineBuffer = list()
		invalidSample = 0
		for line in tqdm(inputfile, desc='Exporting URL\'s', disable=False):
			try:
				sample = eval(line.replace('\n', ''))
				lng = float(sample['lat'])
				lat = float(sample['lng'])
				if lat >= lat0 and lat <= latn and lng >= lng0 and lng <= lngn:
					id_data = sample['id_data'].encode('utf-8')
					id_user = sample['userid'].encode('utf-8')
					country = sample['country'].encode('utf-8')
					url = sample['urls'][-1]['expanded_url'].encode('utf-8')
					place_url = sample['place_url'].encode('utf-8')
					place_name = sample['place_name'].encode('utf-8')
					date_local = sample['date_local']
					lat = sample['lng']
					lng = sample['lat']
					line = id_data
					line += ',' + id_user
					line += ',' + country
					line += ',' + url
					line += ',' + place_url
					line += ',' + place_name.replace(',', ';')
					line += ',' + date_local.strftime('%y-%m-%d %H:%M:%S')
					line += ',' + sample['lng']
					line += ',' + sample['lat']
					line += '\n'
					lineBuffer.append(line)
					if lineBuffer >= 1000:
						for l in lineBuffer:
							outputfile.write(l)
						lineBuffer = list()
			except KeyError:
				invalidSample += 1
				continue
			except SyntaxError:
				invalidSample += 1
				continue
		for l in lineBuffer:
			outputfile.write(l)
		print '#' + str(invalidSample),'Invalid Samples'

def exportPlaceURLByBoundBoxLegacy(locationName, inputfiles,
									configFilename='TwitterMonitor.cfg',
									datePattern='%Y-%m-%d %H:%M:%S'):
	"""
	Exports the files containing the URLs from samples locations according
	to Instagram legacy datasets.
	The function requires the pre-defined bounding box on
	TwitterMonitor.cfg.
	"""

	configparser = TwitterMonitor.loadConfigParser(configFilename)
	coords = TwitterMonitor.loadBoundBox(configparser, locationName)
	lng0, lngn = sorted([coords[0], coords[2]])
	lat0, latn = sorted([coords[1], coords[3]])
	print lat0, latn, lng0, lngn
	print colorama.Fore.CYAN, 'Exporting files with URLs from', locationName, colorama.Fore.RESET
	for filename in inputfiles:
		print colorama.Fore.RED, filename, colorama.Fore.RESET
		inputfile = open(filename, 'r')
		if '.dat' not in filename:
			print 'Please check the extesion of input file (require .dat)'
			exit()
		outputfile = open(filename.replace('.dat', '-url-' + locationName.upper() + '.csv'), 'w')
		lineBuffer = list()
		invalidSample = 0
		for line in tqdm(inputfile, desc='Exporting URL\'s', disable=False):
			try:
				# sample = eval(line.replace('\n', ''))
				sample = line.split(', ')
				if len(sample) != 8:
					invalidSample += 1
					continue
				lng = float(sample[2])
				lat = float(sample[3])
				if lat >= lat0 and lat <= latn and lng >= lng0 and lng <= lngn:
					id_data = sample[0].encode('utf-8')
					id_user = sample[1].encode('utf-8')
					country = 'None'
					place_url = 'None'
					place_name = sample[5].encode('utf-8')
					date_local = datetime.datetime.strptime(sample[4], datePattern)
					tweet = sample[6].encode('utf-8').split(' ')
					url = None
					for x in tweet[::-1]:
						if 'https://t.co' in x:
							url = x
							break
					if url == None:
						invalidSample += 1
						continue
					line = id_data
					line += ',' + id_user
					line += ',' + country
					line += ',' + url
					line += ',' + place_url
					line += ',' + place_name.replace('  ', '; ')
					line += ',' + date_local.strftime('%y-%m-%d %H:%M:%S')
					line += ',' + sample['lng']
					line += ',' + sample['lat']
					line += '\n'
					lineBuffer.append(line)
					if lineBuffer >= 1000:
						for l in lineBuffer:
							outputfile.write(l)
						lineBuffer = list()
			except KeyError:
				invalidSample += 1
				continue
			except SyntaxError:
				invalidSample += 1
				continue
		for l in tqdm(lineBuffer, desc='Saving CSV'):
			outputfile.write(l)
		print '#' + str(invalidSample),'Invalid Samples'

if __name__ == "__main__":
	args = sys.argv[1:]
	f = args.pop(0)
	if f == 'stats':
		exportStatsCountryPlaces(args)
	elif f == 'url':
		inputfiles = args
		exportPlaceURL(inputfiles)
	elif f == 'url-country':
		isoCodeCountry = args.pop(0)
		inputfiles = args
		exportPlaceURLByCountry(isoCodeCountry, inputfiles)
	elif f == 'url-bbox':
		locationName = args.pop(0)
		inputfiles = args
		exportPlaceURLByBoundBox(locationName, inputfiles)
	elif f == 'url-bbox-legacy':
		locationName = args.pop(0)
		inputfiles = args
		exportPlaceURLByBoundBoxLegacy(locationName, inputfiles)
	else:
		print 'look in the code to know the CLI haha :)'
