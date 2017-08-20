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
import signal
import random
import httplib
import colorama
import selenium
import datetime
import urllib2
from tqdm import tqdm
from threading import Thread
from selenium import webdriver


def createDriver(driverPath='libs/phantomjs'):
	try:
		driver = webdriver.PhantomJS(driverPath) # currently implemented only using phantomjs
	except:
		driver = webdriver.PhantomJS()
	return driver

def resolveCheckin(driver, id_data, url, idThread):
	try:
		driver.get(url)
	except Exception, e:
		msg = str(e)
		if 'Connection refused' in msg:
			t = random.randint(1,10)
			print 'Connection Refused - sleeping ' + str(t)
			time.sleep(t)
		else:
			print e
		return 0
	try:
		usernametag = driver.find_element_by_class_name('_iadoq')  # original: _4zhc5, new: _iadoq
		username = usernametag.get_attribute('title').encode('utf-8')
	except selenium.common.exceptions.NoSuchElementException:
		username = 'not-available'
	except Exception, e:
		print e
		username = 'not-available'

	try:
		placetag = driver.find_element_by_class_name('_6y8ij') # original: _kul9p, new: _6y8ij
		placeurl = placetag.get_attribute('href').encode('utf-8')
		placename = placetag.get_attribute('title').encode('utf-8')
		placename = placename.replace(',', ';')
	except selenium.common.exceptions.NoSuchElementException:
		placeurl = 'not-available'
		placename = 'not-available'
	except Exception, e:
		print e
		placeurl = 'not-available'
		placename = 'not-available'
	data = id_data + ',' + url + ',' + placeurl + ',' + placename + ',' +  username
	return data

def resolveCheckinRun(urlBuffer, saveBuffer, idThread, driverPath):
	driver = createDriver(driverPath)
	invalidStreak = 0
	while True:
		try:
			item = urlBuffer.get(timeout=60)
		except Queue.Empty:
			print colorama.Fore.RED + 'Empty Buffer Timeout #' + str(idThread) + colorama.Fore.RESET
			break
		try:
			id_data, url = item
		except (ValueError, TypeError):
			if item == 0:
				urlBuffer.task_done()
				continue
			elif item == 'finish':
				urlBuffer.task_done()
				break
		resolved = resolveCheckin(driver, id_data, url, idThread)
		try:
			saveBuffer.put(resolved, timeout=60)
		except Queue.Full:
			print 'Save Thread is dead bro'
			exit()
		urlBuffer.task_done()
		time.sleep(random.random())
		if resolved == 0:
			invalidStreak += 1
		if invalidStreak >= 100:
			invalidStreak = 0
			t = 30 + random.randint(1,31)
			print colorama.Fore.RED + 'Pausing Web-Driver at #' + str(idThread) + '(' + str(t) + ')' + colorama.Fore.RESET
			time.sleep(t)
	try: # scp wonderland.ddns.me:/media/leokassio/SANDMAN/Spatiotemporal-Data-Analysis/InstagramPlaceCrawler.py .
		driver.service.process.send_signal(signal.SIGTERM)
		driver.quit()
	except Exception, e:
		print colorama.Fore.RED + 'Error Quiting Driver!' + colorama.Fore.RESET
	print colorama.Fore.RED + colorama.Back.WHITE, 'Finishing Crawler-Thread', idThread, colorama.Fore.RESET, colorama.Back.RESET
	return

def saveCheckinRun(outputFilename, saveBuffer):
	f = open(outputFilename, 'a', 0)
	while True:
		try:
			resolved = saveBuffer.get(timeout=300)
			if type(resolved) ==  str:   # str are important but int are ping
				if resolved == 'finish':
					saveBuffer.task_done()
					break
				f.write(resolved + '\n') # str contains the info required
			saveBuffer.task_done()
		except Queue.Empty:
			print colorama.Fore.RED + 'Save Buffer Timeout' + colorama.Fore.RESET
			break
	print colorama.Fore.BLUE + colorama.Back.WHITE + 'Finishing Save-Thread' +  colorama.Fore.RESET + colorama.Back.RESET

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
	urlBufferSize = 1000 # all the threads must have a ref to this buffer
	args = sys.argv[1:]
	if len(args) == 0:
		print colorama.Fore.RED, 'CLI example: python InstagramPlaceCrawler.py inputfile [n_threads, ISO-Alpha 2 Country, libs/phantomjs]'
		return
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
				try:
					urlBuffer.put(0, timeout=60) 	# keeping thread alive
					saveBuffer.put(0, timeout=60) 	# keeping thread alive
				except Queue.Full:
					print 'Threads are dead bro :('
					exit()
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
