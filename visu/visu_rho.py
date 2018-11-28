import os
import time
from textwrap import dedent

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
from dash.dependencies import Input, Output, State


from visu import dash_reusable_components as drc
from visu.figures import serve_prediction_plot, serve_roc_curve, \
    serve_pie_confusion_matrix


app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(children=[
    # .container class is fixed, .container.scalable is scalable
    html.Div(className="banner", children=[
        # Change App Name here
        html.Div(className='container scalable', children=[
            # Change App Name here
            html.H2(html.A(
                'Surface reflection factor',
                href='https://github.com/plotly/dash-svm',
                style={
                    'text-decoration': 'none',
                    'color': 'inherit'
                }
            )),

            html.A(
                html.Img(src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe-inverted.png"),
                href='https://plot.ly/products/dash/'
            )
        ]),
    ]),

    html.Div(id='body', className='container scalable', children=[
        html.Div(className='row', children=[
            html.Div(
                id='div-graphs',
                children=dcc.Graph(
                    id='graph-sklearn-svm',
                    style={'display': 'none'}
                )
            ),

            html.Div(
                className='three columns',
                style={
                    'min-width': '24.5%',
                    'max-height': 'calc(100vh - 85px)',
                    'overflow-y': 'auto',
                    'overflow-x': 'hidden',
                },
                children=[
                    drc.Card([
                        drc.NamedDropdown(
                            name='Select Dataset',
                            id='dropdown-select-dataset',
                            options=[
                                {'label': 'Moons', 'value': 'moons'},
                                {'label': 'Linearly Separable',
                                 'value': 'linear'},
                                {'label': 'Circles', 'value': 'circles'}
                            ],
                            clearable=False,
                            searchable=False,
                            value='moons'
                        ),

                        drc.NamedSlider(
                            name='Sample Size',
                            id='slider-dataset-sample-size',
                            min=100,
                            max=500,
                            step=100,
                            marks={i: i for i in [100, 200, 300, 400, 500]},
                            value=300
                        ),

                        drc.NamedSlider(
                            name='Noise Level',
                            id='slider-dataset-noise-level',
                            min=0,
                            max=1,
                            marks={i / 10: str(i / 10) for i in
                                   range(0, 11, 2)},
                            step=0.1,
                            value=0.2,
                        ),
                    ]),

                    drc.Card([
                        drc.NamedSlider(
                            name='Threshold',
                            id='slider-threshold',
                            min=0,
                            max=1,
                            value=0.5,
                            step=0.01
                        ),

                        html.Button(
                            'Reset Threshold',
                            id='button-zero-threshold'
                        ),
                    ]),

                    drc.Card([
                        drc.NamedDropdown(
                            name='Kernel',
                            id='dropdown-svm-parameter-kernel',
                            options=[
                                {'label': 'Radial basis function (RBF)',
                                 'value': 'rbf'},
                                {'label': 'Linear', 'value': 'linear'},
                                {'label': 'Polynomial', 'value': 'poly'},
                                {'label': 'Sigmoid', 'value': 'sigmoid'}
                            ],
                            value='rbf',
                            clearable=False,
                            searchable=False
                        ),

                        drc.NamedSlider(
                            name='Cost (C)',
                            id='slider-svm-parameter-C-power',
                            min=-2,
                            max=4,
                            value=0,
                            marks={i: '{}'.format(10 ** i) for i in
                                   range(-2, 5)}
                        ),

                        drc.FormattedSlider(
                            style={'padding': '5px 10px 25px'},
                            id='slider-svm-parameter-C-coef',
                            min=1,
                            max=9,
                            value=1
                        ),

                        drc.NamedSlider(
                            name='Degree',
                            id='slider-svm-parameter-degree',
                            min=2,
                            max=10,
                            value=3,
                            step=1,
                            marks={i: i for i in range(2, 11, 2)},
                        ),

                        drc.NamedSlider(
                            name='Gamma',
                            id='slider-svm-parameter-gamma-power',
                            min=-5,
                            max=0,
                            value=-1,
                            marks={i: '{}'.format(10 ** i) for i in
                                   range(-5, 1)}
                        ),

                        drc.FormattedSlider(
                            style={'padding': '5px 10px 25px'},
                            id='slider-svm-parameter-gamma-coef',
                            min=1,
                            max=9,
                            value=5
                        ),

                        drc.NamedRadioItems(
                            name='Shrinking',
                            id='radio-svm-parameter-shrinking',
                            labelStyle={
                                'margin-right': '7px',
                                'display': 'inline-block'
                            },
                            options=[
                                {'label': ' Enabled', 'value': True},
                                {'label': ' Disabled', 'value': False},
                            ],
                            value=True,
                        ),
                    ]),

                    html.Div(
                        dcc.Markdown(dedent("""
                        [Click here](https://github.com/plotly/dash-svm) to visit the project repo, and learn about how to use the app.
                        """)),
                        style={'margin': '20px 0px', 'text-align': 'center'}
                    ),
                ]
            ),
        ]),
    ])
])

app.run_server()