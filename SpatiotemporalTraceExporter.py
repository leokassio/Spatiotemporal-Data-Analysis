# -*- coding: utf-8 -*-

import csv
import sys
import datetime
from tqdm import tqdm

def loadDatasetLegacy(inputfilenames):
	"""
		NOT IN USE YET
		Loads the dataset in memory in custom tuples.
		The method consider the registers formated CSV lines
		Need improvements to do not require too much memory
	"""
	dataset = list()
	print '[ATTENTION] lat and lng coords are inverted!'
	for n, inputfilename in enumerate(inputfilenames):
		n = str(n + 1)
		nrows = loadTotalLines(inputfilename)
		inputfile = open(inputfilename, 'r')
		for line in tqdm(inputfile, desc='Loading File #' + n, total=nrows):
			try:
				data = eval(line[:-1])
			except Exception:
				continue
			id_data = data['id_data']
			date_local = data['date_local']
			uid = data['userid']
			lat = data['lng']
			lng = data['lat']
			country = data['country']
			contents = ''
			for h in data['hashtags']:
				contents += h['text'].encode("utf-8").lower() + ' '
			dataset.append((date_local, uid, float(lat), float(lng), id_data, country, contents))
		inputfile.close()
	return dataset

def loadDataset(inputfilenames):
	"""
		Loads the dataset in memory in custom tuples.
		The method consider the registers formated as python dicts
		Need improvements to do not require too much memory
	"""
	dataset = list()
	print '[ATTENTION] lat and lng coords are inverted!'
	for n, inputfilename in enumerate(inputfilenames):
		n = str(n + 1)
		nrows = loadTotalLines(inputfilename)
		inputfile = open(inputfilename, 'r')
		for line in tqdm(inputfile, desc='Loading File #' + n, total=nrows):
			try:
				data = eval(line[:-1])
			except Exception:
				continue
			id_data = data['id_data']
			date_local = data['date_local']
			uid = data['userid']
			lat = data['lng']
			lng = data['lat']
			country = data['country']
			contents = ''
			for h in data['hashtags']:
				contents += h['text'].encode("utf-8").lower() + ' '
			dataset.append((date_local, uid, float(lat), float(lng), id_data, country, contents))
		inputfile.close()
	return dataset

def loadTotalLines(inputfilename):
	"""
		Counts the number of lines of file.
	"""
	inputfile = open(inputfilename, 'rb')
	for nrows, l in tqdm(enumerate(inputfile), desc='Counting Lines'):
		pass
	nrows += 1
	inputfile.close()
	return nrows

def loadTrace(dataset):
	"""
		Sort the trace registers chronologically
	"""
	print 'Sorting chronologically...   ',
	trace = sorted(dataset, key=lambda k:k[0])
	print '[ok]'
	return trace

def saveCSV(trace, filename):
	"""
		Exports the trace register to CSV files
	"""
	f = open(filename, 'w')
	w = csv.writer(f)
	for i in tqdm(trace, desc='Saving CSV'):
		w.writerow(i)
	f.close()

def

if __name__ == "__main__":
	args = sys.argv
	try:
		inputfiles = args[1:]
		if len(inputfiles) < 2:
			raise Exception
	except Exception:
		print '\n\n'
		print 'Please provide a valid cmd line: python SpatiotemporalTraceExporter.py inputfile1 inputfile 2 outputfile'
		print '\n\n'
		exit()

	outfile = inputfiles[-1]
	dataset = loadDataset(inputfiles[:-1])
	trace = loadTrace(dataset)
	saveCSV(trace, outfile)
