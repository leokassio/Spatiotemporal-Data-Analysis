import csv
import sys
import datetime
from tqdm import tqdm

def validateSamples(args, maxInterval=1800, maxDistance=150):
    print '>> Samples Validation'
    inputfilename = args[0]
    inputfile = open(inputfilename, 'r')
    reader = csv.reader(inputfile)
    for line in tqdm(reader, desc='Validating Samples'):
        utc_date, u1, u2, interval, distance, lat, lng, id_data1, id_data2, country = line
        if u1 != u2:
            if int(interval) <= maxInterval:
                if int(distance) <= maxDistance:
                    if id_data1 != id_data2:
                        continue
        print line
        break

def compareTraces(args):
    print '>> Trace Comparation!'
    inputfilename1, inputfilename2 = args
    inputfile1 = open(inputfilename1, 'r')
    reader1 = csv.reader(inputfile1)
    inputfile2 = open(inputfilename2, 'r')
    reader2 = csv.reader(inputfile2)

    index = 0
	pbar = tqdm(desc='Comparing Files')
    while True:
        index += 1
        pbar.update(1)
        try:
            l1 = next(reader1)
            l2 = next(reader2)
            if l1 != l2:
                print 'Inconsistency Found at line', index
                print l1
                print l2
                break
        except StopIteration:
            break
        print 'End of file!'

if __name__ == "__main__":
    args = sys.argv
    func = args[1]
    if func == 'vs':
        validateSamples(args[2:])
    elif func == 'ct':
        compareTraces(args[2:])
