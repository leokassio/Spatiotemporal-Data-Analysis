# -*- coding: utf-8 -*-
# ============================================================================================
# Kassio Machado - GNU Public License - 2017-07-01 Happy Canada Day
# PhD candidate on Science Computing - UFMG/Brazil
# ============================================================================================

import csv
import sys
import colorama
import CrawlerToolBox

def groupPlaces(args):
	inputfiles = [args] if type(args) != list else args
	for filename in inputfiles:
		dataPlaces, dataCountries = CrawlerToolBox.loadPlaceStats(filename)
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


if __name__ == "__main__":
	args = sys.argv[1:]
	groupPlaces(args)
	# CrawlerToolBox.loadPlaceStats(inputfile, csvfile=True)
