# -*- coding: utf-8 -*-
# ============================================================================================
# Kassio Machado - GNU License - 2016-02-12
# PhD candidate on Science Computing - UFMG/Brazil
# Crawler to visit Instagram urls and get venues registered on dataset of check-ins
# the data if provided in an CSV file and exported in other CSV file.
# The crawler used selenium to perform the HTML/JavaScript parsing
# ============================================================================================

import sys
reload(sys)
sys.setdefaultencoding('utf8')
import time
import Queue
import random
import httplib
import colorama
import selenium
import datetime
import urllib2
from tqdm import tqdm
from threading import Thread
from selenium.webdriver import PhantomJS


def createDriver(driverPath='libs/phantomjs'):
	try:
		driver = PhantomJS(driverPath) # currently implemented only using phantomjs
	except:
		driver = PhantomJS()
	return driver

def resolveCheckin(driver, id_data, url, idThread):
	try:
		driver.get(url)
		placetag = driver.find_element_by_class_name('_kul9p')
		placeurl = placetag.get_attribute('href').encode('utf-8')
		placename = placetag.get_attribute('title').encode('utf-8')
		placename = placename.replace(',', ';')

		usernametag = driver.find_element_by_class_name('_4zhc5')
		username = usernametag.get_attribute('title').encode('utf-8')
		data = id_data + ',' + url + ',' + placeurl + ',' + placename + ',' +  username
		return data
	except selenium.common.exceptions.NoSuchElementException:
		try:
			error = driver.find_element_by_class_name('error-container')
			return id_data + ',' + url + ',not-available,not-available,not-available'
		except selenium.common.exceptions.NoSuchElementException:
			pass
	except AttributeError:
		print 'AttributeError Exception'
		pass
	except httplib.BadStatusLine, e:
		print url, str(e), '#' + str(idThread)
		pass
	except urllib2.URLError, e:
		print url, str(e), '#' + str(idThread)
		return 1
	except Exception, e:
		print 'generic exception', str(e)
	return None

def resolveCheckinRun(urlBuffer, saveBuffer, idThread, driverPath):
	driver = createDriver(driverPath)
	emptyStreak = 0
	invalidStreak = 0
	invalidStreakURL = 0
	while True:
		try:
			item = urlBuffer.get(timeout=60)
		except Queue.Empty:
			if emptyStreak < 3:
				emptyStreak += 1
			else:
				print colorama.Fore.RED, 'Empty Streak Limit at #', idThread, colorama.Fore.RESET
				break
		try:
			id_data, url = item
		except ValueError:
			if item == 'finish':
				urlBuffer.task_done()
				break
		line = resolveCheckin(driver, id_data, url, idThread)
		if type(line) == str:
			saveBuffer.put_nowait(line)
			invalidStreak = 0
			invalidStreakURL = 0
		elif line == 1:
			invalidStreak += 1
			invalidStreakURL += 1
			if invalidStreakURL >= 20:
				invalidStreak = 100
				invalidStreakURL = 0
		elif line == None:
			invalidStreak += 1
		urlBuffer.task_done()
		time.sleep(random.random())
		if invalidStreak >= 100:
			t = 60 + random.randint(1,31)
			print colorama.Fore.RED, 'Restarting Web-Drive at #', idThread, '(' + str(t) + ')', colorama.Fore.RESET
			driver.quit()
			invalidStreak = 0
			time.sleep(t)
			driver = createDriver(driverPath)
	driver.quit()
	print colorama.Fore.RED + colorama.BACK.WHITE, 'Finishing Crawler-Thread', idThread, colorama.Fore.RESET, colorama.Back.RESET
	return

def saveCheckinRun(outputFilename, saveBuffer):
	f = open(outputFilename, 'a', 0)
	while True:
		try:
			r = saveBuffer.get(timeout=120)
			if r == 'finish':
				saveBuffer.task_done()
				break
			f.write(r + '\n')
			saveBuffer.task_done()
		except Queue.Empty:
			print colorama.Fore.RED + colorama.BACK.WHITE, 'Save-Thread Timeout!', colorama.Fore.RED + colorama.Back.RESET
	print colorama.Fore.BLUE + colorama.Back.WHITE, 'Finishing Save-Thread...',  colorama.Fore.RESET + colorama.BACK.RESET

def loadDefinedPlaces(outputFilename):
	urlsDefined = set()
	try:
		outputfile = open(outputFilename, 'r')
		for line in outputfile:
			linesplited = line.replace('\n', '').split(',')
			urlsDefined.add(linesplited[0])
		outputfile.close()
	except IOError:
		print colorama.Fore.RED+colorama.Back.WHITE, '   ¯\_(ツ)_/¯ NO OUTPUT FILE FOUND', colorama.Fore.RESET+colorama.Back.RESET
	return urlsDefined

def main():
	printHeader()
	urlBufferSize = 100
	args = sys.argv[1:]
	if len(args) == 0:
		print colorama.Fore.RED, 'CLI example: python InstagramPlaceCrawler.py inputfile [n_threads, ISO-Alpha 2 Country, libs/phantomjs]'
	input_file_path = args[0]
	try:
		threadBufferSize = int(args[1])
	except:
		threadBufferSize = 1
		print colorama.Fore.RED, 'Default Thread Pool:', threadBufferSize, colorama.Fore.RESET
	try:
		driverPath = args[2]
	except IndexError:
		driverPath = 'libs/phantomjs'

	outputFilename = input_file_path.replace('.csv', '-resolved.csv')

	urlsDefined = loadDefinedPlaces(outputFilename)
	print colorama.Back.RED+colorama.Fore.YELLOW, len(urlsDefined), ' URLs already defined! Lets Rock more now...', colorama.Back.RESET+colorama.Fore.RESET

	try:
		input_file = open(input_file_path, 'r')						# file with url checkins  to be resolved
		numLines = sum(1 for line in input_file)		# counting lines on file
		input_file.seek(0) 								# restarting the cursor of file
	except IOError:
		print colorama.Fore.RED+colorama.Back.WHITE+'   NO PLACE DATASET (⊙_☉) IMPOSSIBLE TO PROCEED...  '+colorama.Fore.RESET+colorama.Back.RESET
		exit()

	urlBuffer = Queue.Queue(maxsize=urlBufferSize)
	saveBuffer = Queue.Queue()

	t = Thread(target=saveCheckinRun, args=[outputFilename, saveBuffer])
	t.daemon = True
	t.start()
	for i in range(threadBufferSize):
		t = Thread(target=resolveCheckinRun, args=[urlBuffer, saveBuffer, i, driverPath])
		t.daemon = True
		t.start()

	for line in tqdm(input_file, desc='Defining URLs', disable=False, total=numLines, leave=True, dynamic_ncols=True):
		linesplited = line.replace('\n', '').split(',')
		try:
			id_data = linesplited[0].encode('utf-8')
			if id_data in urlsDefined:
				urlsDefined.remove(id_data)
				continue
			url = linesplited[3].encode('utf-8')
			if 'http://' not in url and 'https://' not in url:
				url = 'http://' + url
			urlBuffer.put((id_data, url))
		except IndexError:
			continue
	for i in range(threadBufferSize):
		urlBuffer.put('finish')
	saveBuffer.put('finish')
	saveBuffer.join()
	print colorama.Fore.GREEN, 'GG bro ;)', colorama.Fore.RESET

def printHeader():
	print '▀█▀ █▀▀▄ █▀▀ ▀▀█▀▀ █▀▀█ █▀▀▀ █▀▀█ █▀▀█ █▀▄▀█ '
	print '▒█░ █░░█ ▀▀█ ░░█░░ █▄▄█ █░▀█ █▄▄▀ █▄▄█ █░▀░█ '
	print '▄█▄ ▀░░▀ ▀▀▀ ░░▀░░ ▀░░▀ ▀▀▀▀ ▀░▀▀ ▀░░▀ ▀░░░▀ '
	print ''
	print '█▀▀ █▀▀█ █▀▀█ █░░░█ █░░ █▀▀ █▀▀█ '
	print '█░░ █▄▄▀ █▄▄█ █▄█▄█ █░░ █▀▀ █▄▄▀ '
	print '▀▀▀ ▀░▀▀ ▀░░▀ ░▀░▀░ ▀▀▀ ▀▀▀ ▀░▀▀ '

if __name__ == "__main__":
	main()
