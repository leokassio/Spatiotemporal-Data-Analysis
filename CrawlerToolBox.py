# -*- coding: utf-8 -*-
# ============================================================================================
# Kassio Machado - GNU Public License - 2017-07-01 Happy Canada Day
# PhD candidate on Science Computing - UFMG/Brazil
# ============================================================================================

import sys
reload(sys)
sys.setdefaultencoding('utf8')
import datetime
import colorama
import numpy
from ConfigParser import SafeConfigParser

def loadConfigParser(fname):
    try:
        configparser = SafeConfigParser()
        configparser.read(fname)
        return configparser
    except IOError:
        print 'FILE', fname, 'NOT FOUND'
        exit()

def loadAppOAuth(configparser):
	ckey = configparser.get('twitter_oauth', 'ckey')
	csecret = configparser.get('twitter_oauth', 'csecret')
	yield ckey
	yield csecret

def loadHashtags(configparser, configName):
	tags = configparser.get(configName, 'hashtags')
	return tags.split(',')

def loadUserOAuth(configparser, profile):
	atoken = configparser.get('twitter_oauth', 'atoken'+profile) 	# loading the file with section and the propertie name
	asecret = configparser.get('twitter_oauth', 'asecret'+profile)
	yield atoken
	yield asecret

def loadFilenameAlias(configparser, configName):
	fa = configparser.get(configName, 'filename_alias')
	return fa

def loadBoundBox(configparser, locationName):
	configSection = 'cities_bbox'
	locationLabel = configparser.get(configSection, locationName+'_label')
	print colorama.Fore.YELLOW + 'Loading', colorama.Fore.RED + locationLabel, colorama.Fore.YELLOW + 'coordinates...' + colorama.Fore.RESET
	lng0 = configparser.getfloat(configSection, locationName+'_lng0')
	lngn = configparser.getfloat(configSection, locationName+'_lngn')
	lat0 = configparser.getfloat(configSection, locationName+'_lat0')
	latn = configparser.getfloat(configSection, locationName+'_latn')
	coordinates = [lng0, lat0, lngn, latn]
	print colorama.Fore.RED + locationLabel , colorama.Fore.YELLOW + 'Bounding Box', coordinates, colorama.Fore.GREEN + '[OK]' + colorama.Fore.RESET
	return locationLabel, coordinates

def plotBanner():
	colors = [colorama.Fore.RED, colorama.Fore.YELLOW, colorama.Fore.CYAN, colorama.Fore.GREEN,
	colorama.Fore.WHITE, colorama.Fore.MAGENTA]
	i = numpy.random.randint(0,len(colors))
	print colors[i]
	# source: http://fsymbols.com/generators/tarty/
	print '▒█▀▀█ █░░█ ▀▀█▀▀ █░░█ █▀▀█ █▀▀▄ 		'
	print '▒█▄▄█ █▄▄█ ░░█░░ █▀▀█ █░░█ █░░█ 		'
	print '▒█░░░ ▄▄▄█ ░░▀░░ ▀░░▀ ▀▀▀▀ ▀░░▀ 		'
	print ''
	print '▀▀█▀▀ █░░░█ ░▀░ ▀▀█▀▀ ▀▀█▀▀ █▀▀ █▀▀█	'
	print '░▒█░░ █▄█▄█ ▀█▀ ░░█░░ ░░█░░ █▀▀ █▄▄▀ '
	print '░▒█░░ ░▀░▀░ ▀▀▀ ░░▀░░ ░░▀░░ ▀▀▀ ▀░▀▀ ', colorama.Fore.RESET
