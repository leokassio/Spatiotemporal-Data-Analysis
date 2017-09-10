# -*- coding: utf-8 -*-
import sys
import dash
import math
import json
import numpy
import datetime
import colorama
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

RESET = colorama.Fore.RESET + colorama.Back.RESET
ERROR = colorama.Fore.YELLOW + colorama.Back.RED + '[ERROR] '
INFO = colorama.Fore.BLUE + colorama.Back.YELLOW + '[INFO] '
DATA = colorama.Fore.GREEN

def loadCities():
    # TODO load cities from config file (JSON format)
    cities  = ['New York', 'Chicago', 'London', 'Paris']
    cities += ['Sydney', 'Tokyo','Istanbul', 'Sao Paulo']
    return cities

def loadCityAlias(city):
    '''
        Converts the label (pretty name) of city to
        the correct name or folders (without spaces)
    '''
    cityAlias = city.lower().replace(' ', '_')
    return cityAlias

def loadCityData(inputfilename, city):
    cityAlias = loadCityAlias(city)
    inputfilename = 'data/' + cityAlias + '/' + inputfilename
    inputfile = open(inputfilename, 'r')
    data = json.load(inputfile)
    return data

def loadWeather(city):
    '''
        Loads and prepare the original data (JSON file) of weather.
        Returns a dict indexed by date with mean, min and max temperatures.
    '''
    print INFO + 'Loading Weather: ' + city + RESET
    dataObjs = loadCityData('weather.json', city)
    weather = dict()
    for data in dataObjs:
        datekey = data['date']
        datekey = datekey['year'] + '-' + datekey['mon'] + '-' + datekey['mday']
        try:
            temp = float(data['meantempm'])
            maxtemp = float(data['maxtempm'])
            mintemp = float(data['mintempm'])
        except ValueError:
            print ERROR + 'Invalid Temperature Value' + RESET
            continue
        weather[datekey] = dict(temp=temp, maxtemp=maxtemp, mintemp=mintemp)
    return weather

def loadWeatherSpectrum(city, metric='meantempm'):
    print INFO + 'Loading Weather Spectrum: ' + city + RESET
    dataObjs = loadCityData('weather.json', city)
    weather = dict()
    for data in dataObjs:
        datekey = data['date']
        datekey = datekey['year'] + '-' + datekey['mon'] + '-' + datekey['mday']
        temp = data['meantempm']
        if len(temp):
            weather[datekey] = temp
    weather = sorted([int(i) for i in set(weather)])
    return weather

# Basic Components
def buildDropCities():
    cities = loadCities()
    data = list()
    for c in cities:
        data.append({'label': c, 'value': c})
    return data

def buildDropDownWeekdays(default=4, component_id='drop-weekdays'):
    data = list()
    data.append({'label': 'Monday', 'value': 'Monday'})
    data.append({'label': 'Tuesday', 'value': 'Tuesday'})
    data.append({'label': 'Wednesday', 'value': 'Wednesday'})
    data.append({'label': 'Thursday', 'value': 'Thursday'})
    data.append({'label': 'Friday', 'value': 'Friday'})
    data.append({'label': 'Saturday', 'value': 'Saturday'})
    data.append({'label': 'Sunday', 'value': 'Sunday'})
    comp = dcc.Dropdown(id=component_id, options=data, value=data[default]['value'])
    return comp

def buildSliderTemperature(city, default=None, component_id='slider-temperature'):
    comp = dcc.Slider(id='bin-slider', min=1, max=60,
                        step=1, value=20, updatemode='drag')
    return comp

def buildDropPlaces(city, component_id='drop-places'):
    details = loadCityData('places-details.json', city)
    sortPlaces = sorted(details, key=lambda k:details[k]['samples'], reverse=True)
    data = list()
    for i, p in enumerate(sortPlaces):
        x = details[p]
        data.append({'label': '[' + str(i) + '] ' + x['name'] + ' (' + str(x['samples']) + ')', 'value':p})
    return data

def buildPlaceInfo(city=None, place=None):
    if place == None:
        return ''
    details = loadCityData('places-details.json', city)
    try:
        data = details[place]
    except KeyError:
        return '###### Place Not Found!'

    place = str(place)
    text = '''  Place Info  '''
    text += '''  Place Name: ''' + place + '''  '''
    text += '''  URL: ''' + place + ''' [''' + place + '''](''' + place + ''')  '''
    return text

def buildWeatherPlaceHistogram(city, place):
    weather = loadWeather(city)
    placesTimeline = loadCityData('places-timeline.json', city)
    try:
        data = placesTimeline[place]
    except KeyError:
        return {'data':[], 'layout':go.Layout()}
    placeWeather = list()
    for datekey in data:
        try:
            datekey = '20' + datekey
            placeWeather.append(float(weather[datekey]['temp']))
        except KeyError:
            pass
    print set(placeWeather)
    placeWeather = roundMetric(placeWeather, 5.0)
    pdf, edges = numpy.histogram(placeWeather, bins=numpy.arange(min(placeWeather)-5, max(placeWeather)+10, 5))
    s = float(sum(pdf))
    probs = [i/s for i in pdf]
    data = go.Scatter(x=edges,
                        y=pdf,
                        name='Weather Distribution',
                        mode='line', opacity=0.5,
                        marker={'color': 'red'}
                        )
    traces = [data]
    layout = go.Layout( xaxis={'title': 'Temperature'},
                        yaxis={'title': 'P[x=X]'},
                        hovermode='closest')
    g = {'data':traces, 'layout':layout}
    return g


def buildPlaceTimeline(city, place):
    placesTimeline = loadCityData('places-timeline.json', city)
    try:
        data = placesTimeline[place]
        timeline = sorted(data.keys())
        samples = [int(data[t]) for t in timeline]
        timeline = ['20' + t for t in timeline]
    except KeyError:
        timeline = []
        samples = []
    data = go.Scatter(  x=timeline,
                        y=samples,
                        name='Samples',
                        mode='markers', opacity=0.5,
                        marker={'color': 'red'}
                        )
    traces = [data]
    layout = go.Layout( xaxis={'title': 'Timeline'},
                        yaxis={'title': '# of Samples'},
                        hovermode='closest')
    g = {'data':traces, 'layout':layout}
    return g

def buildMapPlace(city, place, n=200, maptoken=None):
    place = str(place)
    print INFO + 'Loading Place: ' + place + RESET
    placesCoords = loadCityData('places-coords.json', city)
    try:
        coords = placesCoords[place]
        zoom = 11
    except KeyError:
        print ERROR + 'Place Not Found: ' + place + RESET
        coords = {'0,0':-1}
        zoom = 0
    sortCoords = sorted(coords, key=lambda k:coords[k], reverse=True)[:n]
    lats = list()
    lngs = list()
    samples = list()
    for c in sortCoords:
        lat, lng = c.split(',')
        lats.append(float(lat))
        lngs.append(float(lng))
        samples = int(coords[c])

    data = go.Scattermapbox(lat=lats,
                            lon=lngs,
                            mode='markers', opacity=0.7,
                            text=samples,
                            marker={'size':14, 'color':'red'})
    layout = go.Layout( autosize=True,
                        hovermode='closest',
                        mapbox=dict(
                            accesstoken=maptoken,
                            bearing=0, style='dark',
                            center=dict(lat=lats[0], lon=lngs[0]),
                            pitch=0, zoom=zoom)
                        )
    # height=650
    g = {'data':[data], 'layout':layout}
    return g


def roundMetric(metric, offset):
    if type(metric) == list:
        metric = [int(math.ceil(i/offset)*offset) for i in metric]
    else:
        metric = int(math.ceil(metric/offset)*offset)
    return metric


#
