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

def exportLocations(args):
	""" Count the samples and group them according to the places indicated by
	Twitter sample (not dependent of app - like Instagram of Foursquare). The
	method exports two CSV files for each input file containing the places and
	countries. """
	inputfiles = [args] if type(args) != list else args
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


def exportPlaceURLByCountry(args):
	""" Filters the fields and exports in CSV files the information related to the
	samples' venues, such as place name, place type, country, Twitter URL of place,
	and Instagram URL of the sample. """

	isoCodeCountry = args[0]
	inputfiles = args[1:]
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
				id_data = sample['id_data']
				url = sample['urls'][-1]['expanded_url']
				place_url = sample['place_url']
				place_name = sample['place_name']
				place_type = sample['place_type']
				line = id_data + ',' + url + ',' + place_url + ','
				line += place_name.replace(',', ';') + ','
				line += country + '\n'
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

def exportPlaceURLByBoundBox(args):
	locationName = args[0]
	inputfiles = args[1:]
	configparser = TwitterMonitor.loadConfigParser('TwitterMonitor.cfg')
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
					id_data = sample['id_data']
					id_user = sample['userid']
					country = sample['country']
					url = sample['urls'][-1]['expanded_url']
					place_url = sample['place_url']
					place_name = sample['place_name']
					# dateutc = sample['date_original'].strftime('%y-%m-%d %H:%M:%S')
					# place_type = sample['place_type']

					line = id_data + ',' + id_user + ',' + country
					line += ',' + url + ',' + place_url
					line += ',' + place_name.replace(',', ';') + '\n'
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

if __name__ == "__main__":
	args = sys.argv[1:]
	# TODO add CLI for methods
	# exportPlaceURL(args)
	# exportLocations(args)
	exportPlaceURLByBoundBox(args)
