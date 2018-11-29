import base64
import io
import re
from textwrap import dedent as d

import dash
import dash_core_components as dcc
import dash_html_components as html
import matplotlib as mpl
from matplotlib import cm
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output

layout = go.Layout(xaxis={'title': 'Wavelength (nm)'},
                   yaxis={'title': 'test'},
                   margin={'l': 50, 'b': 40, 't': 20, 'r': 50},
                   hovermode='closest',
                   height=300,
                   font=dict(color='#CCCCCC'),
                   titlefont=dict(color='#CCCCCC', size=14),
                   plot_bgcolor="#191A1A",
                   paper_bgcolor="#020202")

if not (column_name in dff.columns.get_level_values(0)):
    return {'data': [],
            'layout': layout}

wind = [0,2]
aot = [0.0001,0.1]
sza = 20
azi =90
vza = 40
dff = df.loc[(wind,aot,slice(None),sza,azi,vza)]


parameters = dff.index[:, (color_column_name)].values

wl = dff.columns.droplevel().values
dff = dff.stack(level=['wl'])
norm = mpl.colors.Normalize(vmin=np.nanmin(parameters), vmax=np.nanmax(parameters))
# create a ScalarMappable and initialize a data structure
cmap = cm.Spectral
s_m = cm.ScalarMappable(cmap=cmap, norm=norm)
s_m.set_array([])
i = 0

trace = []
for idx, data  in dff.groupby(level=[0,1]):
    print(idx)
    trace.append(go.Scattergl(
        x=data.index.get_level_values(2),  # spectrum,
        y=data.rho,
        text=data.index.get_level_values(0),

        mode='lines+markers',
        marker={
            'size': 7,
            'opacity': 0.5,
             #'color': 'rgba({}, {}, {}, {})'.format(*s_m.to_rgba(parameters[i]).flatten()),
            # x.unique(),#color': df.index.get_level_values(0),
            'line': {'width': 0.5, 'color': 'white'},
        },
        #line=go.scatter.Line()#color=rgba({}, {}, {}, {})'.format(*s_m.to_rgba(parameters[i]).flatten()), width=2),
    ))
    i = i + 1

# spectrum = df[label['aod']].stack()
fig = {
    'data': trace,
    'layout': layout
}

po.plot(fig)

app = dash.Dash()
# app.css.append_css('data/aeronet_layout.css')
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

# ------------------------------------------------------
# layout section
# ------------------------------------------------------

app.layout = html.Div([
    html.Div([
        html.H1(
            'Above-water data visualization',
            className='eight columns',
            style={'display': 'inline-block'}),

        #   file selection box
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '40%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px',
                'float': 'right'
            },
            # Allow multiple files to be uploaded
            multiple=False)],
        style={'margin-top': '0',
               'width': '100%', 'display': 'inline-block',
               }),
    html.Div([
        html.H4('File...', id='filename',style={'float': 'left','width': '60%'}),
        html.Div([
            html.H4('Color variable:',style={'margin-bottom': '0','width':'50%'}),
            html.Div([
                dcc.Dropdown(
                    id='color-column',
                    value='sza',

                ),
                # dcc.RadioItems(
                #     id='color-type',
                #     options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                #     value='Linear',
                #     labelStyle={'width': '25%','display': 'inline-block'})],
            ],
            style={'width': '50%','display': 'inline-block'})],
            style={'width': '40%',
                   'margin-top': '0',
                   'display': 'inline-block',
                   'margin-left': '0%',
                   'float': 'right'})],
        style={'margin-block-end': '7%'}),

    # Spectrum graphs
    html.Div([
        html.Div([

            html.H4('Spectral parameter 1'),
            dcc.Dropdown(
                id='spectrum1',
                value='Ed'),
        ],
            style={'width': '48.9%',
                   'float': 'left', }),

        html.Div([

            html.H4('Spectral parameter 2'),
            dcc.Dropdown(
                id='spectrum2',
                value='Lt'),
        ],
            style={'width': '48.9%',
                   'float': 'right', }),],
        style={'width':'100%','margin-block-start': '1%'}),

    html.Div([
        html.Div([
            dcc.Graph(id='graph1')],
            # className='eight columns',
            style={'width': '49.9%',
                   'margin-top': '0',
                   'display': 'inline-block',

                   }),
        html.Div([
            dcc.Graph(id='graph2')],
            # className='eight columns',
            style={'width': '49.9%',
                   'float': 'right',
                   'display': 'inline-block',

                   }),
    ],

         style={'height': '20%'},
        # className='row'
    ),

    # Spectrum graphs
    html.Div([
        html.Div([
            dcc.Graph(id='graph3')],
            # className='eight columns',
            style={'width': '49.9%',
                   'margin-top': '0',
                   'display': 'inline-block',

                   }),
        html.Div([
            dcc.Graph(id='graph4')],
            # className='eight columns',
            style={'width': '49.9%',
                   'float': 'right',
                   'display': 'inline-block',

                   }),
    ],

        # style={'display': 'inline-block'},
        # className='row'
    ),

    html.Div([

        html.H4('Spectral parameter'),
        dcc.Dropdown(
            id='spectrum3',
            value='Rrs(awr)'),
    ],
        style={'width': '48.9%',
               'float': 'left', }),

    html.Div([

        html.H4('Spectral parameter'),
        dcc.Dropdown(
            id='spectrum4',
            value='Rrs(swr)'),
    ],
        style={'width': '48.9%',
               'float': 'right', }),

    html.Div([
        dcc.Markdown(d("""
                **Selection Data**

                Choose the lasso or rectangle tool in the graph's menu
                bar and then select points in the graph.
            """)),
        # html.Pre(id='selected-data', style=styles['pre']),
    ], className='three columns'),

    # hidden signal value
    html.Div(id='dataset', style={'display': 'none'}),
],

    style={
        'width': '90%',
        'fontFamily': 'Sans-Serif',
        'margin-left': 'auto',
        'margin-right': 'auto'})


def figure_spectrum(df, column_name, color_column_name):
    dff = df
    layout = go.Layout( xaxis={'title': 'Wavelength (nm)'},
                        yaxis={'title': column_name},
                        margin={'l': 50, 'b': 40, 't': 20, 'r': 50},
                        hovermode='closest',
                        height=300,
                        font=dict(color='#CCCCCC'),
                        titlefont=dict(color='#CCCCCC', size='14'),
                        plot_bgcolor="#191A1A",
                        paper_bgcolor="#020202")

    if not(column_name in dff.columns.get_level_values(0)):
        return  {'data': [],
                 'layout': layout}

    parameters = df.loc[:, (color_column_name)].values
    dff = dff.loc[:, ([column_name])]
    wl = dff.columns.droplevel().values
    dff = dff.stack(level=['wl'])
    norm = mpl.colors.Normalize(vmin=np.nanmin(parameters), vmax=np.nanmax(parameters))
    # create a ScalarMappable and initialize a data structure
    cmap = cm.Spectral
    s_m = cm.ScalarMappable(cmap=cmap, norm=norm)
    s_m.set_array([])
    i = 0
    trace = []
    for date, x in dff.groupby(level=0):
        trace.append(go.Scattergl(
            x=wl,  # spectrum,
            y=x[column_name].values.flatten(),
            text=x.index.get_level_values(0),
            name=str(parameters[i]),
            mode='lines',
            marker={
                'size': 7,
                'opacity': 0.5,
                # 'color': 'rgba({}, {}, {}, {})'.format(*s_m.to_rgba(parameters[i]).flatten()),
                # x.unique(),#color': df.index.get_level_values(0),
                'line': {'width': 0.5, 'color': 'white'},
            },
            line=go.Line(color='rgba({}, {}, {}, {})'.format(*s_m.to_rgba(parameters[i]).flatten()), width=2),
            showlegend=False
        ))
        i = i + 1

    # spectrum = df[label['aod']].stack()
    return {
        'data': trace,
        'layout': layout
    }


def list_data(contents, level=0):
    # content_type, content_string = contents.split(',')
    # decoded = base64.b64decode(content_string)
    # df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), header=[0, 1, 2], index_col=0, nrows=0, parse_dates=True)
    c = df.columns.levels[level]
    # remove useless variables
    c = c.drop(filter(lambda s: re.match('.*(Wave|Tri|[sS]ite|Dat)', s), c))
    return [{'label': i, 'value': i} for i in c]
#
def parse_contents(contents):
    global df
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), header=[0, 1], index_col=0, parse_dates=True)

# ------------------------------------------------------
# callback section
# ------------------------------------------------------
# ---------------------------
# update uploaded data

@app.callback(Output('dataset', 'children'),
              [Input('upload-data', 'contents'),
               Input('upload-data', 'filename')])
def update_output(contents, filename):
    print(filename)
    parse_contents(contents)
    return contents


@app.callback(Output('filename', 'children'),
              [Input('upload-data', 'filename')])
def show_filename(filename):
    return 'File: ' + str(filename)

# ---------------------------
# update dropdown menus

@app.callback(Output('color-column', 'options'),
              [Input('dataset', 'children')])
def update_dropdown(contents):
    return list_data(contents)


@app.callback(Output('spectrum1', 'options'),
              [Input('dataset', 'children')])
def update_dropdown(contents):
    return list_data(contents, level=0)


@app.callback(Output('spectrum2', 'options'),
              [Input('dataset', 'children')])
def update_dropdown(contents):
    return list_data(contents, level=0)


@app.callback(Output('spectrum3', 'options'),
              [Input('dataset', 'children')])
def update_dropdown(contents):
    return list_data(contents, level=0)


@app.callback(Output('spectrum4', 'options'),
              [Input('dataset', 'children')])
def update_dropdown(contents):
    return list_data(contents, level=0)


# selection from time series graph -> spectrum graph
@app.callback(Output('graph1', 'figure'),
              [Input('spectrum1', 'value'),
               Input('color-column', 'value'),
               Input('dataset', 'children')])
def spectrum_figure(column_name, color_column_name,void):
    return figure_spectrum(df, column_name, color_column_name)


# selection from time series graph -> spectrum graph
@app.callback(Output('graph2', 'figure'),
              [Input('spectrum2', 'value'),
               Input('color-column', 'value'),
               Input('dataset', 'children')])
def spectrum_figure(column_name, color_column_name,void):
    return figure_spectrum(df, column_name, color_column_name)


@app.callback(Output('graph3', 'figure'),
              [Input('spectrum3', 'value'),
               Input('color-column', 'value'),
               Input('dataset', 'children')])
def spectrum_figure(column_name, color_column_name,void):
    return figure_spectrum(df, column_name, color_column_name)


# selection from time series graph -> spectrum graph
@app.callback(Output('graph4', 'figure'),
              [Input('spectrum4', 'value'),
               Input('color-column', 'value'),
               Input('dataset', 'children')])
def spectrum_figure(column_name, color_column_name,void):
    return figure_spectrum(df, column_name, color_column_name)


app.run_server()
