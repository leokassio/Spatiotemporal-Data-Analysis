# essentials
import csv
import sys
import math
import datetime
import pandas as pd
from tqdm import tqdm

def distanceCoords(lat1, long1, lat2, long2):
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

def loadDataset(inputfilename):
	dataset = list()
	inputfile = open(inputfilename, 'r')
	reader = csv.reader(inputfile)
	datePattern = '%Y-%m-%d %H:%M:%S'
	for line in tqdm(reader, desc='Loading CSV'):
		date_local, uid, lat, lng, id_data, country, content = line
		date_local = datetime.datetime.strptime(date_local, datePattern)
		dataset.append((date_local, uid, float(lat), float(lng), id_data, country))
	return dataset

def loadTrace(dataset):
	print 'Sorting chronologically...   ',
	trace = sorted(dataset, key=lambda k:k[0])
	print '[ok]'
	return trace

def loadTraceEncounters(trace, maxInterval=900, maxDistance=150):
	r_earth = 6378.0
	bufferOut = list()
	outf = open(inputfile.replace('.csv', '-edges.csv'), 'w')
	writer = csv.writer(outf)
	i = -1
	for s1 in tqdm(trace, desc='Estimating Edges'):
		i += 1
		date_local, uid, lat, lng, id_data, country = s1
		tmstmp = date_local.strftime('%y-%m-%d %H:%M:%S')
		j = 0
		while True:
		    j += 1
		    try:
				s2 = trace[i+j]
		    except IndexError:
		        break
		    if uid != s2[1]:
		        interval = (s2[0] - date_local).total_seconds()
		        if interval <= maxInterval:
					dist = distanceCoords(lat, lng, s2[2], s2[3])
					if dist <= maxDistance:
						line = (tmstmp, uid, s2[1], int(interval), int(dist),  lat, lng, id_data, s2[4], country)
						bufferOut.append(line)
		        else:
		            break
		    else:
		        break
		if len(bufferOut) >= 50000:
		    for row in bufferOut:
		        writer.writerow(row)
		    bufferOut = list()
	for row in bufferOut:
		writer.writerow(row)
	return

if __name__ == "__main__":
	args = sys.argv
	try:
		inputfile, maxInterval = args[1:]
		maxInterval = int(maxInterval)
	except Exception:
		print '\n\n'
		print 'Please provide a valid cmd line'
		print 'ex: python EncounterSimulatorTwitter.py inputfile [t>0 secs]'
		print '\n\n'
		exit()

	datasetConverted = loadDataset(inputfile)
	traceSorted = loadTrace(datasetConverted)
	loadTraceEncounters(traceSorted, maxInterval=maxInterval)
