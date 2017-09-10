# -*- coding: utf-8 -*-
import sys
import cities
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

app = dash.Dash()
app.css.append_css({'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})

placesConfig = json.load(open('places-app.json', 'r'))
maptoken = placesConfig['mapbox_token']

cityOptions = cities.loadCities()
defaultCityIndex = 3
defaultCity = cityOptions[defaultCityIndex]

layout = list()
header = [html.H1(id='h-title', children='Places App', className='eight columns')]
header.append(html.H3(id='h-city', children=defaultCity, className='four columns'))
layout.append(html.Div(header, className='row'))
layout.append(html.Hr())

data = cities.buildDropCities()
elements = [html.Label('City')]
elements.append(dcc.Dropdown(id='drop-cities', options=data, clearable=False,
                value=data[defaultCityIndex]['value'], searchable=False))
divCity = html.Div(elements, className='six columns')

data = cities.buildDropPlaces(defaultCity)
elements = [html.Label('Instagram Place')] #[dcc.Input(id='input-link', type='text', list='leokassio', autocomplete='leokassio')]
elements.append(dcc.Dropdown(id='drop-places', options=data, value=data[0]['value'], searchable=True))
divPlaces = html.Div(elements, className='six columns')

elements = [divCity, divPlaces]
dualPanel = html.Div(elements, className='row')
layout.append(dualPanel)

elements = [html.Div(dcc.Graph(id='graph-timeline', animate=True), className='six columns')]
elements.append(html.Div([dcc.Graph(id='map-place', animate=True)], className='six columns'))
dualPanel = html.Div(elements, className='row')
layout.append(dualPanel)

elements = [html.Div(dcc.Graph(id='graph-weather-histogram', animate=True), className='six columns')]
dualPanel = html.Div(elements, className='row')
layout.append(dualPanel)

layout.append(html.Div([dcc.Markdown(id='markdown-info', children=cities.buildPlaceInfo())]))

app.layout = html.Div(children=layout) # style={'textAlign': 'center'}

# delegated methods
@app.callback(
Output(component_id='h-city', component_property='children'),
[Input(component_id='drop-cities', component_property='value')])
def callHeaderCity(city):
    return html.H3(id='h-city', children=city, className='four columns')

@app.callback(
Output(component_id='drop-places', component_property='options'),
[Input(component_id='drop-cities', component_property='value')])
def callDropPlaces(city):
    return cities.buildDropPlaces(city)

@app.callback(
Output(component_id='map-place', component_property='figure'),
[Input(component_id='drop-cities', component_property='value'),
Input(component_id='drop-places', component_property='value')])
def callMapPlace(city, place):
    print INFO + 'Maps' + RESET
    return cities.buildMapPlace(city, place, n=10, maptoken=maptoken)

@app.callback(
Output(component_id='graph-timeline', component_property='figure'),
[Input(component_id='drop-cities', component_property='value'),
Input(component_id='drop-places', component_property='value')])
def callMapPlace(city, place):
    return cities.buildPlaceTimeline(city, place)

@app.callback(
Output(component_id='graph-weather-histogram', component_property='figure'),
[Input(component_id='drop-cities', component_property='value'),
Input(component_id='drop-places', component_property='value')])
def callMapPlace(city, place):
    return cities.buildWeatherPlaceHistogram(city, place)

@app.callback(
Output(component_id='markdown-info', component_property='children'),
[Input(component_id='drop-cities', component_property='value'),
Input(component_id='drop-places', component_property='value')])
def callPlaceInfoMarkdown(city, place):
    print INFO + 'Markdown' + RESET
    return cities.buildPlaceInfo(city, place)

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8888, debug=True)














#
