# -*- coding: utf-8 -*-
import os
import sys
import csv
import json
import colorama
from tqdm import tqdm

RESET = colorama.Fore.RESET + colorama.Back.RESET
ERROR = colorama.Fore.YELLOW + colorama.Back.RED + '[ERROR] '
INFO = colorama.Fore.BLUE + colorama.Back.YELLOW + '[INFO] '
DATA = colorama.Fore.GREEN

def loadFileNames(filepath):
    filenames = [f for f in os.listdir(datapath)]
    return filenames

def exportPlaceTimeline(inputfilenames, outputfilename):
    '''
        Exports individually the timeline of places.
        The output is a JSON file where the keys are the places URL.
        The values are key-values date=>(# of samples).
    '''
    print INFO + 'Exporting places\' timeline' + RESET
    unavailable = 'not-available'
    dataPlaces = dict()
    for filename in inputfilenames:
        print colorama.Fore.GREEN + filename.split('/')[-1] + colorama.Fore.RESET
        inputfile = open(filename, 'r')
        for line in tqdm(inputfile, desc='grouping samples', leave=False):
            data = line.split(',')
            # id_data, id_user, country, url, place_url, place_name,
            # date_local.strftime('%y-%m-%d %H:%M:%S'), lat, lng,
            # instagram_place, name_place, user_name
            instagram_place = data[9]
            if instagram_place != unavailable:
                datekey = data[6].split(' ')[0]
                try:
                    dataPlaces[instagram_place][datekey] += 1
                except KeyError:
                    if instagram_place not in dataPlaces:
                        dataPlaces[instagram_place] = {datekey:1}
                    else:
                        dataPlaces[instagram_place][datekey] = 1
    outputfile = open(outputfilename, 'w')
    print INFO + 'Saving JSON file: ' + outputfilename + RESET
    json.dump(dataPlaces, outputfile, sort_keys=True, indent=4)
    return

def exportPlaceCoords(inputfilenames, outputfilename):
    '''
        Exports individually the coords of places.
        The output is a JSON file where the keys are the places URL.
        The values are key-values (string coords)=>(# of samples).
    '''
    print INFO + 'Exporting places\'s coords' + RESET
    unavailable = 'not-available'
    dataPlaces = dict()
    for filename in inputfilenames:
        print colorama.Fore.GREEN + filename.split('/')[-1] + colorama.Fore.RESET
        inputfile = open(filename, 'r')
        for line in tqdm(inputfile, desc='grouping coords', leave=False):
            # id_data, id_user, country, url, place_url, place_name,
            # date_local.strftime('%y-%m-%d %H:%M:%S'), lat, lng,
            # instagram_place, name_place, user_name
            data = line.split(',')
            instagram_place = data[9]
            if instagram_place != unavailable:
                coords = data[7] + ',' + data[8]
                try:
                    dataPlaces[instagram_place][coords] += 1
                except KeyError:
                    if instagram_place not in dataPlaces:
                        dataPlaces[instagram_place] = {coords:1}
                    else:
                        dataPlaces[instagram_place][coords] = 1
    print INFO + 'Saving JSON file: ' + outputfilename + RESET
    outputfile = open(outputfilename, 'w')
    json.dump(dataPlaces, outputfile, sort_keys=True, indent=4)
    return

def exportPlaceDetails(inputfilenames, outputfilename):
    '''
        Exports individually the details of places.
        The output is a JSON file where the keys are the places URL.
        The values has # of samples, # of users, date of 1st register,
        date of last register.
    '''
    print INFO + 'Exporting places\'s details' + RESET
    unavailable = 'not-available'
    dataPlaces = dict()
    for filename in inputfilenames:
        print colorama.Fore.GREEN + filename.split('/')[-1] + colorama.Fore.RESET
        inputfile = open(filename, 'r')
        for line in tqdm(inputfile, desc='grouping coords', leave=False):
            # id_data, id_user, country, url, place_url, place_name,
            # date_local.strftime('%y-%m-%d %H:%M:%S'), lat, lng,
            # instagram_place, name_place, user_name
            data = line.split(',')
            instagram_place = data[9]
            if instagram_place != unavailable:
                id_user = data[1]
                name_place = data[10]
                datekey = data[6].split(' ')[0]
                try:
                    dp = dataPlaces[instagram_place]
                    dp['samples'] += 1
                    dp['users'].add(id_user)
                    dp['dates'].add(datekey)
                except KeyError:
                    dp = dict()
                    dp['name'] = name_place
                    dp['samples'] = 1
                    dp['users'] = set([id_user])
                    dp['dates'] = set([datekey])
                    dataPlaces[instagram_place] = dp
    for p in dataPlaces:
        dataPlaces[p]['users'] = len(dataPlaces[p]['users'])
        x = sorted(dataPlaces[p].pop('dates'))
        dataPlaces[p]['date-start'] = x[0]
        dataPlaces[p]['date-end'] = x[-1]

    print INFO + 'Saving JSON file: ' + outputfilename + RESET
    outputfile = open(outputfilename, 'w')
    json.dump(dataPlaces, outputfile, sort_keys=True, indent=4)
    return

def exportSamplesTimeline(inputfilenames, outputfilename):
    '''
        Exports individually the coords of places.
        The output is a JSON file where the keys are the dates
        and the values are the correspondent total of samples
    '''
    print INFO + 'Exporting timeline of samples' + RESET
    unavailable = 'not-available'
    dataSamples = dict()
    for filename in inputfilenames:
        print colorama.Fore.GREEN + filename.split('/')[-1] + colorama.Fore.RESET
        inputfile = open(filename, 'r')
        for line in tqdm(inputfile, desc='grouping coords', leave=False):
            # id_data, id_user, country, url, place_url, place_name,
            # date_local.strftime('%y-%m-%d %H:%M:%S'), lat, lng,
            # instagram_place, name_place, user_name
            data = line.split(',')
            datekey = data[6].split(' ')
            datekey = '20' + datekey[0]
            try:
                dataSamples[datekey] += 1
            except KeyError:
                dataSamples[datekey] = 1
    print INFO + 'Saving JSON file: ' + outputfilename + RESET
    outputfile = open(outputfilename, 'w')
    json.dump(dataSamples, outputfile, sort_keys=True, indent=4)
    return

def exportUsersTimeline(inputfilenames, outputfilename):
    '''
        Exports individually the coords of places.
        The output is a JSON file where the keys are the dates
        and the total of users
    '''
    print INFO + 'Exporting timeline of samples' + RESET
    unavailable = 'not-available'
    dataSamples = dict()
    for filename in inputfilenames:
        print colorama.Fore.GREEN + filename.split('/')[-1] + colorama.Fore.RESET
        inputfile = open(filename, 'r')
        for line in tqdm(inputfile, desc='grouping coords', leave=False):
            # id_data, id_user, country, url, place_url, place_name,
            # date_local.strftime('%y-%m-%d %H:%M:%S'), lat, lng,
            # instagram_place, name_place, user_name
            data = line.split(',')
            datekey = data[6].split(' ')
            datekey = '20' + datekey[0]
            try:
                dataSamples[datekey].add(data[1])
            except KeyError:
                dataSamples[datekey] = set(data[1])
    for dt in dataSamples:
        dataSamples[dt] = len(dataSamples[dt])
    print INFO + 'Saving JSON file: ' + outputfilename + RESET
    outputfile = open(outputfilename, 'w')
    json.dump(dataSamples, outputfile, sort_keys=True, indent=4)
    return

def exportWeatherData(inputfilename, outputfilename):
    '''
        Exports the original JSON data from weather underground
        in other lightweight JSON file - it exports just the daily summary
        provided in original JSON.
    '''
    print INFO + 'Exporting weather data: ' + outputfilename + RESET
    inputfile = open(inputfilename, 'r')
    outputfile = open(outputfilename, 'w')
    outputdata = list()
    for line in inputfile:
        data = json.loads(line)
        try:
            data = data['history']['dailysummary'][0]
            outputdata.append(data)
        except IndexError:
            print ERROR + 'Summary Index Error: ' + RESET + str(data['history']['dailysummary'])
            print ERROR + 'Date: ' + RESET + data['history']['date']['pretty']
            continue
    json.dump(outputdata, outputfile, sort_keys=True, indent=4)

def plotPlaceFolium(inputfilename):
    import folium
    print INFO + 'Ploting maps: ' + inputfilename + RESET
    unavailable = 'not-available'
    dataPlaces = dict()
    inputfile = open(inputfilename, 'r')
    jdata = json.load(inputfile)
    places = sorted(jdata.keys(), key=lambda k:sum(jdata[k].values()), reverse=True)
    top = places[0]
    print top
    print 'Coords:', len(jdata[top])
    print 'Samples:', sum(jdata[top].values())
    map_osm = folium.Map(location=[40.753198,-73.98365],
                        zoom_start=12,
                        tiles='CartoDB dark_matter')
    topCoords = sorted(jdata[top].keys(), key=lambda k:jdata[top][k], reverse=True)
    for coords in topCoords[:10]:
        lat, lng = coords.split(',')
        # folium.Marker([float(lat), float(lng)], popup=str(jdata[top][coords])).add_to(map_osm)
        folium.CircleMarker(location=[float(lat), float(lng)], radius=30,
                            color='#3186cc', fill_color='#3186cc',
                            popup=str(jdata[top][coords])).add_to(map_osm)
    map_osm.save('map.html')
    return

if __name__ == "__main__":
    # params come from args
    args = sys.argv[1:]
    try:
        func = args.pop(0)
    except IndexError:
        print ERROR + 'Please review the CLI!' + RESET
        print ERROR + 'Ex: python app.py function params...' + RESET

    if func == 'export-places-timeline':
        try:
            outputfilename = args.pop(0)
            inputfiles = args
        except IndexError:
            print ERROR + 'python app.py export-timeline outputfilename dir/*-merged.csv' + RESET
            exit()
        exportPlaceTimeline(inputfiles, outputfilename)
    elif func == 'export-places-coords':
        try:
            outputfilename = args.pop(0)
            inputfiles = args
        except IndexError:
            print ERROR + 'python app.py export-coords outputfilename dir/*-merged.csv' + RESET
            exit()
        exportPlaceCoords(inputfiles, outputfilename)
    elif func == 'export-places-details':
        try:
            outputfilename = args.pop(0)
            inputfiles = args
        except IndexError:
            print ERROR + 'python app.py export-details outputfilename dir/*-merged.csv' + RESET
            exit()
        exportPlaceDetails(inputfiles, outputfilename)
    elif func == 'export-samples-timeline':
        try:
            outputfilename = args.pop(0)
            inputfiles = args
        except IndexError:
            print ERROR + 'python app.py export-samples-timeline outputfilename dir/*-merged.csv' + RESET
            exit()
        exportSamplesTimeline(inputfiles, outputfilename)
    elif func == 'export-users-timeline':
        try:
            outputfilename = args.pop(0)
            inputfiles = args
        except IndexError:
            print ERROR + 'python app.py export-users-timeline outputfilename dir/*-merged.csv' + RESET
            exit()
        exportUsersTimeline(inputfiles, outputfilename)
    elif func == 'export-weather':
        try:
            outputfilename = args.pop(0)
            inputfilename = args.pop(0)
        except IndexError:
            print ERROR + 'python app.py export-weather outputfilename.json uweather-city.json' + RESET
            exit()
        exportWeatherData(inputfilename, outputfilename)
    elif func == 'map':
        try:
            inputfile = args.pop(0)
        except IndexError:
            print ERROR + 'python app.py map coords-file.json' + RESET
            exit()
        plotMap(inputfile)

    print INFO + 'Done!' + RESET
    exit()






#
