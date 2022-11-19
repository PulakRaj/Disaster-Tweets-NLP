import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import numpy as np
import dash_bootstrap_components as dbc
import sqlite3
import pickle
import plotly.graph_objects as go
from datetime import date
import datetime as dt
import base64
import dash_table

"""SINGLE PAGE CHANGE: comment out next line if running as single page"""
from app import app

"""SINGLE PAGE CHANGE: uncomment next line if running as single page"""
# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Mappings to go back and forth between numerical and non-numerical data
cause_mapping =  {'Arson': 0, 'Campfire': 1, 'Children': 2, 'Debris Burning': 3, 
                  'Equipment Use': 4, 'Fireworks': 5, 'Lightning': 6, 
                  'Powerline': 7, 'Railroad': 8, 'Smoking': 9, 'Structure': 10}
cause_mapping_reverse = {v: k for k,v in cause_mapping.items()}
category_mapping_reverse = {1: "Natural", 2: "Accidental", 3: "Malicious"}
arson_mapping_reverse = {0: "Non-Malicious", 1: "Malicious"}
state_mapping =  {"AK": 0, "AL": 1, "AR": 2, "AZ": 3, "CA": 4, "CO": 5, "CT": 6, "DC": 7, "DE": 8, 
                "FL": 9, "GA": 10, "HI": 11, "IA": 12, "ID": 13, "IL": 14, "IN": 15, "KS": 16, 
                "KY": 17, "LA": 18, "MA": 19, "MD": 20, "ME": 21, "MI": 22, "MN": 23, "MO": 24, 
                "MS": 25, "MT": 26, "NC": 27, "ND": 28, "NE": 29, "NH": 30, "NJ": 31, "NM": 32, 
                "NV": 33, "NY": 34, "OH": 35, "OK": 36, "OR": 37, "PA": 38, "PR": 39, "RI": 40, 
                "SC": 41, "SD": 42, "TN": 43, "TX": 44, "UT": 45, "VA": 46, "VT": 47, "WA": 48, 
                "WI": 49, "WV": 50, "WY": 51}
state_mapping_reverse = {v: k for k,v in state_mapping.items()}
size_class_mapping = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6}
size_class_mapping_reverse = {v: k for k,v in size_class_mapping.items()}
dow_mapping = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}
dow_mapping_reverse = {v: k for k,v in dow_mapping.items()}

# Fire prediction models
specific_all_rf = pickle.load(open("classifiers/specific_all_rf.sav", "rb"))
specific_all_knn = pickle.load(open("classifiers/specific_all_knn.sav", "rb"))
specific_all_dt = pickle.load(open("classifiers/specific_all_dt.sav", "rb"))
specific_all_nb = pickle.load(open("classifiers/specific_all_nb.sav", "rb"))
specific_models = [specific_all_rf, specific_all_knn, specific_all_dt, specific_all_nb]

group_all_rf = pickle.load(open("classifiers/group_all_rf.sav", "rb"))
group_all_knn = pickle.load(open("classifiers/group_all_knn.sav", "rb"))
group_all_dt = pickle.load(open("classifiers/group_all_dt.sav", "rb"))
group_all_nb = pickle.load(open("classifiers/group_all_nb.sav", "rb"))
group_models = [group_all_rf, group_all_knn, group_all_dt, group_all_nb]

arson_all_rf = pickle.load(open("classifiers/arson_all_rf.sav", "rb"))
arson_all_knn = pickle.load(open("classifiers/arson_all_knn.sav", "rb"))
arson_all_dt = pickle.load(open("classifiers/arson_all_dt.sav", "rb"))
arson_all_nb = pickle.load(open("classifiers/arson_all_nb.sav", "rb"))
arson_models = [arson_all_rf, arson_all_knn, arson_all_dt, arson_all_nb]

all_models = [specific_models, group_models, arson_models]

specific_images = ['assets/specific_all_rf.png', 'assets/specific_all_knn.png', 
                   'assets/specific_all_dt.png', 'assets/specific_all_nb.png']
group_images = ['assets/group_all_rf.png', 'assets/group_all_knn.png', 
                'assets/group_all_dt.png', 'assets/group_all_nb.png']
arson_images = ['assets/arson_all_rf.png', 'assets/arson_all_knn.png',
                'assets/arson_all_dt.png', 'assets/arson_all_nb.png']
all_images = [specific_images, group_images, arson_images]

df_browse = pd.read_excel('evaluation.xlsx')

df = pd.read_pickle("wildfire_df.p")

# Go back and forth between abbreviations and state names
us_state_abbrev = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "Puerto Rico": "PR"
}
abbrev_us_state = dict(map(reversed, us_state_abbrev.items()))

month_dict = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 
              7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}

colors = {
    'background': '#1F2630',
    'text': '#7FDBFF'
}


def get_sunburst():
  my_sunburst = px.sunburst(
                  data_frame=df,
                  path=['Arson', 'category', 'STAT_CAUSE_DESCR'],
                  color = 'category',
                  maxdepth=-1
                )
  my_sunburst.update_layout(plot_bgcolor=colors['background'],
                      paper_bgcolor=colors['background'])
  my_sunburst.update_traces(textinfo='label+percent entry')
  return my_sunburst

"""
LAYOUT
"""
def get_layout():
  return(dbc.Container([
            dbc.Row([
              dbc.Col([
                html.H3("Fire Cause Evaluation for Advanced Users", style = {"color": "white"}
                )
              ], width={"offset":1})
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            #! Specificity Selection
                            html.P(
                              "Select Specificity:", style = {"color": "white", "margin-bottom": "0px"}
                            ),
                            dcc.Dropdown(
                              id="slct_spec",
                              multi = False,
                              clearable = False,
                              style = {"display": True, 'color': '#212121'},
                              value = 0,
                              options = [
                                  {"label": "Specific Cause", "value": 0},
                                  {"label": "Categorized Cause", "value": 1},
                                  {"label": "Malicious Y/N", "value": 2}
                              ]),
                            html.Br(),
                            
                            #! Model Selection
                            html.P(
                              "Select Model:", style = {"color": "white", "margin-bottom": "0px"}
                            ),
                            dcc.Dropdown(
                              id="slct_model",
                              multi = False,
                              clearable = False,
                              style = {"display": True, 'color': '#212121'},
                              value = 0,
                              options = [
                                  {"label": "Random Forest", "value": 0},
                                  {"label": "K-Nearest Neighbors", "value": 1},
                                  {"label": "Decision Tree", "value": 2},
                                  {"label": "Naive Bayes", "value": 3}
                              ]),
                            html.Br(),
                            
                            #! State Selection
                            html.P(
                              "State:",  style = {"color": "white", "margin-bottom": "0px"}
                            ),
                            dcc.Dropdown(
                                id="slct_state",
                                multi = False,
                                clearable = False,
                                style = {"display": True, 'color': '#212121'},
                                value = 31,
                                options = [{"label": abbrev_us_state[label], "value": value} for label, value in state_mapping.items()],
                                className="dcc_compon"
                            ),
                            html.Br(),
                            
                            #! Date Selection
                            html.P(
                              "Date:",  style = {"color": "white", "margin-bottom": "0px"}
                            ),
                            dcc.DatePickerSingle(
                                id = 'slct_date',
                                date = date.today(),
                                initial_visible_month=date.today(),
                                display_format='MMM Do, YY'
                            ),
                            html.Br(),
                            html.Br(),
                            html.Div("Predicted cause for fire:", style={'fontsize': 16}),
                            html.Div(id="result", children = [], style={'color':'#ffa500', 'fontSize': 30})
                        ])
                    ], color="dark", style={"height": "42.7rem", "width": "16rem"})
                ], width = {"size":2, "offset":1}),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            #! Latitude Selection
                            html.P(
                              "Latitude:",  style = {"color": "white", "margin-bottom": "0px"}
                            ),
                            dcc.Input(
                                id='slct_lat',
                                type='number',
                                value=40.7416,
                                debounce=True
                            ),
                            html.Br(),
                            html.Br(),
                            
                            #! Longitude Selection
                            html.P(
                              "Longitude:",  style = {"color": "white", "margin-bottom": "0px"}
                            ),
                            dcc.Input(
                                id='slct_long',
                                type='number',
                                value=-74.1749,
                                debounce=True
                            ),
                            html.Br(),
                            html.Br(),
                            
                            #! Fire Size Selection
                            html.P(
                              "Fire Size:",  style = {"color": "white", "margin-bottom": "0px"}
                            ),
                            dcc.Input(
                                id='slct_size',
                                type='number',
                                value=130,
                                debounce=True
                            ),
                            html.Br(),
                            html.Br(),
                            
                            #! Fire Size Classification Selection
                            html.P(
                              "Fire Size Classification:",  style = {"color": "white", "margin-bottom": "0px"}
                            ),
                            dcc.Dropdown(
                                id="slct_class",
                                multi = False,
                                clearable = False,
                                style = {"display": True, 'color': '#212121'},
                                value = 3,
                                options = [{"label": label, "value": value} for label, value in size_class_mapping.items()],
                                className="dcc_compon"
                            ),
                            html.Br(),
                            
                            #! Burn Time Selection
                            html.P(
                              "Burn Time:",  style = {"color": "white", "margin-bottom": "0px"}
                            ),
                            dcc.Input(
                                id='slct_time',
                                type='number',
                                value=30,
                                debounce=True
                            ),
                            html.Br(),
                            html.Br()
                        ])
                    ], style={"height": "42.7rem"})
                ], width={"size":2, "offset":0}),
                dbc.Col([
                  dbc.Card([
                    html.Img(id='image')
                  ])
                ], width=6)
           ]),
            html.Br(),
            dbc.Row([
              dbc.Col([
                dbc.Card([
                  dbc.CardBody([
                    dash_table.DataTable(
                      id='datatable-interactivity',
                      columns=[
                        {"name": i, "id": i, "deletable": False, "selectable": False, "hideable": False}
                        for i in df_browse.columns
                      ],
                      data=df_browse.to_dict('records'),
                      editable=False,
                      filter_action="none",
                      sort_action="native",
                      sort_mode="single",
                      column_selectable="single",
                      row_selectable="single",
                      page_current=0,
                      page_size=6,
                      style_cell={'color': 'black'},
                      style_header={'fontWeight': 'bold'},
                      style_cell_conditional=[{'if': {'column_id': 'Predicted | Data'},
                                              'textAlign': 'left'}]
                    )
                  ])
                ])
              ], {"size":7, "offset":0.5}),
              dbc.Col([
                dbc.Card([
                  dbc.CardBody([
                    dcc.Graph(id='sunburst',
                              config={'displayModeBar': False},
                              figure=get_sunburst()
                    )
                  ])
                ])
              ], width=4)
            ])
         ], fluid=True)
  )
  
"""SINGLE PAGE CHANGE: change layout = ... to app.layout = ... if running as single page"""
layout = get_layout()

"""
CALLBACK
"""
@app.callback(
    Output("result", "children"),
    [Input("slct_spec", "value"),
    Input("slct_model", "value"),
    Input("slct_state", "value"),
    Input("slct_date", "date"),
    Input("slct_class", "value"),
    Input("slct_size", "value"),
    Input("slct_lat", "value"),
    Input("slct_long", "value"),
    Input("slct_time", "value")]
)
def update_advanced_graph(slct_spec, slct_model, slct_state, slct_date, slct_class, slct_size, slct_lat, slct_long, slct_time):
    date_obj = dt.datetime.strptime(slct_date, "%Y-%m-%d")
    slct_month = int(date_obj.month)
    slct_year = int(date_obj.year)
    slct_day = int(dow_mapping[date_obj.strftime('%A')])
    spec = all_models[slct_spec]
    classifier = spec[slct_model]
    result = int(classifier.predict([[slct_state, slct_year, slct_class, slct_size, 
                                      slct_lat, slct_long, slct_month, slct_day, slct_time]]))
    if slct_spec == 0:
        result = cause_mapping_reverse[result]
    elif slct_spec == 1:
        result = category_mapping_reverse[result]
    else:
        result = arson_mapping_reverse[result]
    # result = "Predicted cause for fire: " + result
    return result

@app.callback(
  Output("image", 'src'),
  [Input("slct_spec", "value"),
   Input("slct_model", "value")]
)
def update_img(slct_spec, slct_model):
  spec = all_images[slct_spec]
  img_path = spec[slct_model]
  encoded_image = base64.b64encode(open(img_path, 'rb').read())
  return 'data:image/png;base64,{}'.format(encoded_image.decode())

'''SINGLE PAGE CHANGE: uncomment next line if running as single page'''
# if __name__ == "__main__":
#     app.run_server(debug=True)