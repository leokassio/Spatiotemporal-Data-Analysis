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

weatherConfig = json.load(open('weather-app.json', 'r'))

CITIES  = weatherConfig['cities']


def loadCityAlias(city):
    '''
        Converts the label (pretty name) of city to
        the correct name or folders (without spaces)
    '''
    cityAlias = city.lower().replace(' ', '_')
    return cityAlias

def loadWeather(city):
    '''
        Loads and prepare the original data (JSON file) of weather.
        Returns a dict indexed by date with mean, min and max temperatures.
    '''
    print INFO + 'Loading Weather: ' + city + RESET
    cityAlias = loadCityAlias(city)
    inputfilename = 'data/' + cityAlias + '/weather.json' # TODO move it to weather-app.json
    inputfile = open(inputfilename, 'r')
    dataObjs = json.load(inputfile)
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

def loadTemperatureSpectrum(data, step=None):
    temperatures = [roundMetric(data[t]['temp'], step) for t in data]
    spectrum = sorted(set(temperatures))
    return spectrum

def buildDropDownCities(default=0):
    # data.append({'label': 'New York', 'value': 'New York'})
    # data.append({'label': 'Chicago', 'value': 'Chicago'})
    # data.append({'label': 'London', 'value': 'London'})
    # data.append({'label': 'Paris', 'value': 'Paris'})
    # data.append({'label': 'Sydney', 'value': 'Sydney'})
    # data.append({'label': 'Tokyo', 'value': 'Tokyo'})
    # data.append({'label': 'Istanbul', 'value': 'Istanbul'})
    # data.append({'label': 'Sao Paulo', 'value': 'Sao Paulo'})
    data = list()
    for c in CITIES:
        data.append({'label': c, 'value': c})
    return dcc.Dropdown(id='dropDownCities', options=data, value=data[default]['value'])

def buildDropDownWeekdays(default=4):
    data = list()
    data.append({'label': 'Monday', 'value': 'Monday'})
    data.append({'label': 'Tuesday', 'value': 'Tuesday'})
    data.append({'label': 'Wednesday', 'value': 'Wednesday'})
    data.append({'label': 'Thursday', 'value': 'Thursday'})
    data.append({'label': 'Friday', 'value': 'Friday'})
    data.append({'label': 'Saturday', 'value': 'Saturday'})
    data.append({'label': 'Sunday', 'value': 'Sunday'})
    return dcc.Dropdown(id='dropDownWeekdays', options=data, value=data[default]['value'])

def buildDropDownTippingPoint(spectrum=None, tipping=None):
    if spectrum == None:
        spectrum = range(-30, 35, 5)
    if tipping == None:
        tipping = str(int(spectrum[int(len(spectrum)/2.0)-1]))
    data = [{'label': str(int(n)), 'value': str(int(n))} for n in spectrum]
    return dcc.Dropdown(id='dropDownTippingPoints', options=data, value=tipping)

def plotSamplesTimeline(city):
    print INFO + 'Loading Samples Timeline: ' + city + RESET
    colors = ['#003399', '#006600', '#cc3300', '#990099', '#cc9900']
    color = numpy.random.choice(colors)
    cityAlias = city.lower().replace(' ', '_')
    inputfilename = 'data/' + cityAlias + '/samples-timeline.json' # TODO move it to weather-app.json
    inputfile = open(inputfilename, 'r')
    dataJSON = json.load(inputfile)
    timeline = sorted(dataJSON.keys())
    samples = [int(dataJSON[t]) for t in timeline]
    traces = list()
    m = numpy.mean(samples)
    sampleMean = [m for i in range(len(samples))]
    data = go.Scatter(  x=timeline,
                        y=sampleMean,
                        name='Mean',
                        mode='line', opacity=0.5,
                        marker={'color': 'black'}
                        )
    traces.append(data)
    data = go.Scatter(  x=timeline,
                        y=samples,
                        text=city,
                        name='Samples',
                        mode='markers', opacity=0.5,
                        marker={'size': 10, 'color': color,
                                'line': {'width': 0.5, 'color': color}},
                        )
    traces.append(data)
    layout = go.Layout( xaxis={'title': 'Timeline'},
                        yaxis={'title': '# of Samples'},
                        hovermode='closest')
    g = {'data':traces, 'layout':layout}
    return g

def plotUsersTimeline(city):
    print INFO + 'Loading Users Timeline: ' + city + RESET
    colors = ['#003399', '#006600', '#cc3300', '#990099', '#cc9900']
    color = numpy.random.choice(colors)
    cityAlias = city.lower().replace(' ', '_')
    inputfilename = 'data/' + cityAlias + '/users-timeline.json' # TODO move it to weather-app.json
    inputfile = open(inputfilename, 'r')
    dataJSON = json.load(inputfile)
    timeline = sorted(dataJSON.keys())
    samples = [int(dataJSON[t]) for t in timeline]
    traces = list()
    m = numpy.mean(samples)
    sampleMean = [m for i in range(len(samples))]
    data = go.Scatter(  x=timeline,
                        y=sampleMean,
                        name='Mean',
                        mode='line', opacity=0.5,
                        marker={'color': 'black'}
                        )
    traces.append(data)
    data = go.Scatter(  x=timeline,
                        y=samples,
                        text=city,
                        name='Samples',
                        mode='markers', opacity=0.5,
                        marker={'size': 10, 'color': color,
                                'line': {'width': 0.5, 'color': color}},
                        )
    traces.append(data)
    layout = go.Layout( xaxis={'title': 'Timeline'},
                        yaxis={'title': '# of Users'},
                        hovermode='closest')
    g = {'data':traces, 'layout':layout}
    return g

def plotSamplesMap(city):
    print 'Ploting Map', city
    maptoken = weatherConfig['mapbox_token']

    cityAlias = city.lower().replace(' ', '_')
    inputfilename = 'data/' + cityAlias + '/places-coords.json' # TODO move it to weather-app.json
    inputfile = open(inputfilename, 'r')
    dataJSON = json.load(inputfile)
    places = sorted(dataJSON.keys(), key=lambda k:sum(dataJSON[k].values()), reverse=True)[:5000]
    lats = list()
    lngs = list()
    labels = list()
    for p in places:
        coords = sorted(dataJSON[p].keys(), key=lambda k:dataJSON[p][k], reverse=True)
        lat, lng = coords[0].split(',')
        lats.append(float(lat))
        lngs.append(float(lng))
        labels.append(p + ': ' + str(sum(dataJSON[p].values())))
    traces = list()
    data = go.Scattermapbox(lat=lats,
                            lon=lngs,
                            mode='markers', opacity=0.1,
                            marker={'size':14},
                            text=labels)
    traces.append(data)
    layout = go.Layout( autosize=True,
                        height=650,
                        hovermode='closest',
                        mapbox=dict(
                            accesstoken=maptoken,
                            bearing=0, style='dark',
                            center=dict(lat=lats[0], lon=lngs[0]),
                            pitch=0, zoom=11)
                        )
    g = {'data':traces, 'layout':layout}
    return g

def plotPlacesPopularity(city):
    print 'Creating graph', city
    colors = ['#003399', '#006600', '#cc3300', '#990099', '#cc9900']
    color = numpy.random.choice(colors)
    cityAlias = city.lower().replace(' ', '_')
    inputfilename = 'data/' + cityAlias + '/places-timeline.json' # TODO move it to weather-app.json
    inputfile = open(inputfilename, 'r')
    dataJSON = json.load(inputfile)
    data = [sum(dataJSON[p].values()) for p in dataJSON]
    traces = list()
    pdf, edges = numpy.histogram(data, bins=len(set(data)))
    s = float(sum(pdf))
    probs = [i/s for i in pdf]
    cdf = numpy.cumsum(probs)
    ccdf = 1 - cdf
    data = go.Scatter(  x=edges,
                        y=ccdf,
                        name='Mean',
                        mode='line', opacity=0.75,
                        marker={'color': 'black'}
                        )
    traces.append(data)
    layout = go.Layout( xaxis={'title': 'Places', 'type': 'log'},
                        yaxis={'title': '# of Samples'},
                        hovermode='closest')
    g = {'data':traces, 'layout':layout}
    return g

def plotWeatherWeeks(city):
    datekeyFormat = '%Y-%m-%d'
    cityAlias = loadCityAlias(city)
    inputfilename = 'data/' + cityAlias + '/weather.json' # TODO move it to weather-app.json
    inputfile = open(inputfilename, 'r')
    dataObjs = json.load(inputfile)
    weather = loadWeather(city)
    timeline = sorted(weather.keys())
    weatherWeeks = dict()
    for dk in weather:
        datekey = datetime.datetime.strptime(dk, datekeyFormat)
        weekIndex  = datekey.strftime('%Y:(%U)')
        try:
            weatherWeeks[weekIndex]['temp'].append(weather[dk]['temp'])
            weatherWeeks[weekIndex]['maxtemp'].append(weather[dk]['maxtemp'])
            weatherWeeks[weekIndex]['mintemp'].append(weather[dk]['mintemp'])
        except KeyError:
            weatherWeeks[weekIndex] = dict()
            weatherWeeks[weekIndex]['temp'] = [weather[dk]['temp']]
            weatherWeeks[weekIndex]['maxtemp'] = [weather[dk]['maxtemp']]
            weatherWeeks[weekIndex]['mintemp'] = [weather[dk]['mintemp']]
    for w in weatherWeeks:
        weatherWeeks[w]['temp'] = numpy.mean((weatherWeeks[w]['temp']))
        weatherWeeks[w]['maxtemp'] = numpy.mean((weatherWeeks[w]['maxtemp']))
        weatherWeeks[w]['mintemp'] = numpy.mean((weatherWeeks[w]['mintemp']))
    timeline = sorted(weatherWeeks.keys())
    traces = list()
    data = go.Scatter(  x=timeline,
                        y=[weatherWeeks[t]['temp'] for t in timeline],
                        name='Daily Mean',
                        mode='line', opacity=0.7,
                        marker={'color': 'grey'}
                        )
    traces.append(data)
    data = go.Scatter(  x=timeline,
                        y=[weatherWeeks[t]['maxtemp'] for t in timeline],
                        name='Daily Max',
                        mode='line', opacity=0.7,
                        marker={'color': 'red'}
                        )
    traces.append(data)
    data = go.Scatter(  x=timeline,
                        y=[weatherWeeks[t]['mintemp'] for t in timeline],
                        name='Daily Min',
                        mode='line', opacity=0.7,
                        marker={'color': 'blue'}
                        )
    traces.append(data)
    data = go.Scatter(  x=timeline,
                        y=[roundMetric(weatherWeeks[t]['temp'], 5.0) for t in timeline],
                        name='Rounded Mean',
                        mode='line', opacity=0.7,
                        marker={'color': 'black'}
                        )
    traces.append(data)
    layout = go.Layout( xaxis={'title': 'Timeline'},
                        yaxis={'title': 'Temperature (Celsius)'},
                        hovermode='closest')
    g = {'data':traces, 'layout':layout}
    return g

def plotWeatherTimeline(city):
    print 'Ploting weather timeline: ' + city
    colors = ['#003399', '#006600', '#cc3300', '#990099', '#cc9900']
    color = numpy.random.choice(colors)
    cityAlias = loadCityAlias(city)
    inputfilename = 'data/' + cityAlias + '/weather.json' # TODO move it to weather-app.json
    inputfile = open(inputfilename, 'r')
    dataObjs = json.load(inputfile)
    weather = loadWeather(city)
    timeline = sorted(weather.keys())
    meantemps = [weather[t]['temp'] for t in timeline]
    traces = list()
    data = go.Scatter(  x=timeline,
                        y=[weather[t]['temp'] for t in timeline],
                        name='Daily Mean',
                        mode='line', opacity=0.7,
                        marker={'color': 'grey'}
                        )
    traces.append(data)
    data = go.Scatter(  x=timeline,
                        y=[weather[t]['maxtemp'] for t in timeline],
                        name='Daily Max',
                        mode='line', opacity=0.7,
                        marker={'color': 'red'}
                        )
    traces.append(data)
    data = go.Scatter(  x=timeline,
                        y=[weather[t]['mintemp'] for t in timeline],
                        name='Daily Min',
                        mode='line', opacity=0.7,
                        marker={'color': 'blue'}
                        )
    traces.append(data)
    data = go.Scatter(  x=timeline,
                        y=[roundMetric(weather[t]['temp'], 5.0) for t in timeline],
                        name='Rounded Mean',
                        mode='line', opacity=0.7,
                        marker={'color': 'black'}
                        )
    traces.append(data)
    layout = go.Layout( xaxis={'title': 'Timeline'},
                        yaxis={'title': 'Temperature (Celsius)'},
                        hovermode='closest')
    g = {'data':traces, 'layout':layout}
    return g

def plotWeatherWeekdays(city, weekday):
    datekeyFormat = '%Y-%m-%d'
    cityAlias = loadCityAlias(city)
    weather = loadWeather(city)
    timeline = sorted(weather.keys())
    weatherWeekdays = dict()
    for dk in weather:
        datekey = datetime.datetime.strptime(dk, datekeyFormat)
        if datekey.strftime('%A') != weekday:
            continue
        weekdayIndex  = datekey.strftime('%Y:%U-%A')
        try:
            weatherWeekdays[weekdayIndex]['temp'] = weather[dk]['temp']
            weatherWeekdays[weekdayIndex]['maxtemp'] = weather[dk]['maxtemp']
            weatherWeekdays[weekdayIndex]['mintemp'] = weather[dk]['mintemp']
        except KeyError:
            weatherWeekdays[weekdayIndex] = dict()
            weatherWeekdays[weekdayIndex]['temp'] = weather[dk]['temp']
            weatherWeekdays[weekdayIndex]['maxtemp'] = weather[dk]['maxtemp']
            weatherWeekdays[weekdayIndex]['mintemp'] = weather[dk]['mintemp']
    timeline = sorted(weatherWeekdays.keys())
    traces = list()
    data = go.Scatter(  x=[t.split('-')[0] for t in timeline],
                        y=[weatherWeekdays[t]['temp'] for t in timeline],
                        name='Daily Mean',
                        mode='line', opacity=0.7,
                        marker={'color': 'gray'}
                        )
    traces.append(data)
    data = go.Scatter(  x=[t.split('-')[0] for t in timeline],
                        y=[weatherWeekdays[t]['maxtemp'] for t in timeline],
                        name='Daily Max',
                        mode='line', opacity=0.7,
                        marker={'color': 'red'}
                        )
    traces.append(data)
    data = go.Scatter(  x=[t.split('-')[0] for t in timeline],
                        y=[weatherWeekdays[t]['mintemp'] for t in timeline],
                        name='Daily Min',
                        mode='line', opacity=0.7,
                        marker={'color': 'blue'}
                        )
    traces.append(data)
    data = go.Scatter(  x=[t.split('-')[0] for t in timeline],
                        y=[roundMetric(weatherWeekdays[t]['temp'], 5.0) for t in timeline],
                        name='Rounded Mean',
                        mode='line', opacity=0.7,
                        marker={'color': 'black'}
                        )
    traces.append(data)
    layout = go.Layout( xaxis={'title': 'Timeline'},
                        yaxis={'title': 'Temperature (Celsius)'},
                        hovermode='closest')
    g = {'data':traces, 'layout':layout}
    return g

def plotWeatherTippingPoints(city, tippingPoint=None):
    step = 5
    cityAlias = loadCityAlias(city)
    weather = loadWeather(city)
    timeline = sorted(weather.keys())

    spectrum = loadTemperatureSpectrum(weather, step)
    dictWeatherPlaces = dict()
    for t in spectrum:
        dictWeatherPlaces[t] = dict()

    inputfilename = 'data/' + cityAlias + '/places-timeline.json' # TODO move it to weather-app.json
    inputfile = open(inputfilename, 'r')
    dataJSON = json.load(inputfile)
    for p in dataJSON:
        data = dataJSON[p]
        for datekey in data:
            try: # loading the correspondent the day's temperature
                temp = weather['20' + datekey]['temp']
                temp = roundMetric(temp, step)
            except KeyError:
                continue
            try:
                dictWeatherPlaces[temp][p] += data[datekey]
            except KeyError:
                dictWeatherPlaces[temp][p] = data[datekey]
    if tippingPoint == None:
        tippingPoint = spectrum[int(len(spectrum)/2.0) - 1]
    else:
        tippingPoint = int(tippingPoint)
    print INFO + city + ' Tipping Point: ' + str(tippingPoint) + RESET
    alpha = set()
    beta = set()
    for t in dictWeatherPlaces:
        if t <= tippingPoint:
            alpha.update(dictWeatherPlaces[t].keys())
        else:
            beta.update(dictWeatherPlaces[t].keys())
    intersec = alpha.intersection(beta)
    randIntersec = numpy.random.choice(list(intersec), int(len(intersec)/20.0))
    alpha.difference_update(intersec)
    alpha.update(randIntersec)
    beta.difference_update(intersec)
    beta.update(randIntersec)

    y = list()
    for t in spectrum:
        x = 0
        for p in alpha:
            try:
                x += dictWeatherPlaces[t][p]
            except KeyError:
                continue
        y.append(x)
    y = normalizeMax(y, float(max(y)))
    data = go.Scatter(  x=spectrum,
                        y=y,
                        name='Phase 1',
                        mode='line', opacity=0.7,
                        marker={'color': 'blue'}
                        )
    traces = list()
    traces.append(data)
    y = list()
    for t in spectrum:
        x = 0
        for p in beta:
            try:
                x += dictWeatherPlaces[t][p]
            except KeyError:
                continue
        y.append(x)
    y = normalizeMax(y, float(max(y)))
    data = go.Scatter(  x=spectrum,
                        y=y,
                        name='Phase 2',
                        mode='line', opacity=0.7,
                        marker={'color': 'red'}
                        )
    traces.append(data)
    layout = go.Layout( xaxis={'title': 'Temperature'},
                        yaxis={'title': 'Temperature (Celsius)'},
                        hovermode='closest')
    g = {'data':traces, 'layout':layout}
    return g

def setLabelCity(city):
    return city + datetime.datetime.now().strftime(' %H:%M:%S')

def roundMetric(metric, offset):
    metric = int(math.ceil(metric/offset)*offset)
    return metric

def normalizeMax(dataList, maxValue):
    values = []
    for x in dataList:
        try:
            v = x/maxValue
        except ZeroDivisionError:
            v = 0
        values.append(v)
    return values

def dev():
    '''
        Function used only in developtment mode
    '''
    city = 'Chicago'
    temperature = '0'
    plotTippingPoints(city, temperature)
    return

try:
    devMode = bool(sys.argv[1])
except IndexError:
    devMode = False
    pass

if devMode == True:
    print INFO + 'Development Mode!' + RESET
    dev()
    exit()
else:
    print INFO + 'Live Mode!' + RESET

app = dash.Dash()
app.css.append_css({'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})

elements = list()
elements.append(html.Div([html.H1(id='labelTitle', children='Dataset Visualization', className='eight columns',), html.H3(id='labelCity', children='New York')], className='row'))
elements.append(html.Hr())
elements.append(buildDropDownCities())
elements.append(dcc.Graph(id='mapSamples', animate=True))

# Samples Timeline Panel
graphSamples = html.Div([dcc.Graph(id='graphSamples', animate=True)], className='six columns')
graphUsers =  html.Div([dcc.Graph(id='graphUsers', animate=True)],className='six columns')
dualPanel = html.Div([graphSamples, graphUsers], className='row')
elements.append(dualPanel)

# Weather Panels
graphWeather = html.Div(dcc.Graph(id='graphWeather', animate=True), className='six columns')
graphWeatherWeeks = html.Div(dcc.Graph(id='graphWeatherWeeks', animate=True), className='six columns')
dualPanel = html.Div([graphWeather, graphWeatherWeeks], className='row')
elements.append(dualPanel)

graphWeatherWeekdays = html.Div([buildDropDownWeekdays(), dcc.Graph(id='graphWeatherWeekdays', animate=True)], className='six columns')
graphWeatherTippings = html.Div([buildDropDownTippingPoint(), dcc.Graph(id='graphWeatherTippings', animate=True)], className='six columns')
dualPanel = html.Div([graphWeatherWeekdays,graphWeatherTippings], className='row')
elements.append(dualPanel)

# elements.append(dcc.Graph(id='placesPop', animate=True))

app.layout = html.Div(children=elements, style={'textAlign': 'center'})

@app.callback(
Output(component_id='graphSamples', component_property='figure'),
[Input(component_id='dropDownCities', component_property='value')])
def callSamplesTimeline(city):
    return plotSamplesTimeline(city)

@app.callback(
Output(component_id='graphUsers', component_property='figure'),
[Input(component_id='dropDownCities', component_property='value')])
def callUsersTimeline(city):
    return plotUsersTimeline(city)

@app.callback(
Output(component_id='mapSamples', component_property='figure'),
[Input(component_id='dropDownCities', component_property='value')])
def callSamplesMap(city):
    return plotSamplesMap(city)
#
# @app.callback(
# Output(component_id='placesPop', component_property='figure'),
# [Input(component_id='dropDownCities', component_property='value')])
# def callPlacesPopularityDistribution(city):
#     return plotPlacesPopularity(city)

@app.callback(
Output(component_id='graphWeather', component_property='figure'),
[Input(component_id='dropDownCities', component_property='value')])
def callWeatherTimeline(city):
    return plotWeatherTimeline(city)

@app.callback(
Output(component_id='graphWeatherWeeks', component_property='figure'),
[Input(component_id='dropDownCities', component_property='value')])
def callWeatherTimeline(city):
    return plotWeatherWeeks(city)

@app.callback(
Output(component_id='graphWeatherWeekdays', component_property='figure'),
[Input(component_id='dropDownCities', component_property='value'),
Input(component_id='dropDownWeekdays', component_property='value')])
def callWeatherTimeline(city, weekday):
    return plotWeatherWeekdays(city, weekday)

@app.callback(
Output(component_id='graphWeatherTippings', component_property='figure'),
[Input(component_id='dropDownCities', component_property='value'),
Input(component_id='dropDownTippingPoints', component_property='value')])
def callWeatherTippingPoints(city, tippingPoint):
    return plotWeatherTippingPoints(city, tippingPoint)

@app.callback(
Output(component_id='labelCity', component_property='children'),
[Input(component_id='dropDownCities', component_property='value')])
def callLabelCity(city):
    return setLabelCity(city)

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8888, debug=True)






#
