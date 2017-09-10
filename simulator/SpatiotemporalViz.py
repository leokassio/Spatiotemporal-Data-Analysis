# -*- coding: utf-8 -*-

import csv
import sys
import json
import folium
from folium.plugins import MarkerCluster
import datetime
import colorama
import pandas as pd
from tqdm import tqdm
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


def logo():
	color = colorama.Fore.RED
	print color + ''
	print '_______  _____  _______ _______ _____  _____  _______ _______ _______  _____ '
	print '|______ |_____] |_____|    |      |   |     |    |    |______ |  |  | |_____]'
	print '______| |       |     |    |    __|__ |_____|    |    |______ |  |  | |      '
	print ''
	print '_______ _____ _______ _     _        _______ _______  _____   ______'
	print '|______   |   |  |  | |     | |      |_____|    |    |     | |_____/'
	print '______| __|__ |  |  | |_____| |_____ |     |    |    |_____| |    \\_'
	print '' + colorama.Fore.RESET
	return

def loadEdges(inputfilename, n, maxInterval=1800, maxDistance=150):
    '''
        Loads the dataset of edges.
        The parameter n defines the total of rows to read
    '''
    dataset = list()
    inputfile = open(inputfilename, 'r')
    for line in tqdm(inputfile, desc='Loading Edges Dataset'):
        if n <= 0:
            break
        n -= 1
        dataset.append(json.loads(line))
    return dataset

def loadJSON(inputfilename):
    '''
        Loads the JSON/GeoJSON files.
        Return the data as dict
    '''
    inputfile = open(inputfilename, 'r')
    data = json.load(inputfile)
    return data

def loadPolygons(geodata):
    '''
        Adds the shapely Polygons object to the GeoJSON
        read from file.
    '''
    for p in geodata['features']:
        try:
            p['polygon'] = Polygon(p['geometry']['coordinates'][0][0])
        except Exception, e:
            print str(e)
            print p['properties']
            print p['geometry']['coordinates']
    return geodata

def loadNeighbourhood(dataset, geodata):
    '''
        Define the neighbourhood of each sample and add a
        new member to the JSON objects of dataset called 'neighbourhood'
    '''
    polygons = geodata['features']
    for sample in tqdm(dataset, 'Loading Neighbourhood', leave=False):
        pt = Point(sample['lng'], sample['lat'])
        sample['neighbourhood'] = None
        for pg in polygons:
            if pg['polygon'].contains(pt):
                sample['neighbourhood'] = pg['properties']['neighbourhood']
                break
    return dataset

def choroplethEncounters(dataset, geodata, geomapfilename):
    neighbs = dict()
    for p in geodata['features']:
        del p['polygon']
    for sample in dataset:
        try:
            neighbs[sample['neighbourhood']] += 1
        except KeyError:
            neighbs[sample['neighbourhood']] = 1
    n = float(sum(neighbs.values()))
    for nb in neighbs:
        neighbs[nb] = neighbs[nb]/n
        print nb, neighbs[nb]
    geomap = folium.Map([48.857903, 2.343864], zoom_start=11)
    geomap.choropleth(geo_str=geodata, data=neighbs[nb], fill_color='YlOrRd', highlight=True)
    geomap.save(geomapfilename)
    return

if __name__ == "__main__":
    logo()
    args = sys.argv
    n = 1000000
    edgefilename = 'data/paris-edges.json'
    geofilename = '../data/shapefiles/paris-neighbourhoods.geojson'
    geomapfilename = 'data/paris-neighbourhoods.html'

    dataset = loadEncounters(edgefilename, n)
    geobounds = loadGeoJSON(geofilename)
    geobounds = loadPolygons(geobounds)
    dataset = loadNeighbourhood(dataset, geobounds)
    # choroplethEncounters(dataset, geobounds, geomapfilename)
    df = pd.DataFrame(dataset)
    neighbourhoods = df['neighbourhood'].value_counts().astype(float)
    neighbourhoods.reset_index()
    neighbourhoods.columns = ['Neighbourhood', 'Number']

    geomap = folium.Map(location=[48.864716, 2.349014], zoom_start=12, tiles='CartoDB dark_matter')
    geomap.choropleth(geo_path=geofilename, data=neighbourhoods,
                    columns = ['Neighbourhood', 'Number'],
                    key_on = 'feature.properties.neighbourhood',
                    fill_color = 'YlOrRd', fill_opacity = 0.7,
                    line_opacity = 0.2, legend_name = 'Number of incidents per district')

    # coords = list()
    # for each in tqdm(df.iterrows(), desc='Loading Coords', leave=False):
    #     lat, lnng = each[1][7], each[1][8]
    #     coords.append([lat, lng])

    # encounters = folium.FeatureGroup(name='encounters')
    # encounters.add_child(MarkerCluster(locations = coords))
    # geomap.add_child(encounters)
    geomap.save('geomap.html')













    # END
