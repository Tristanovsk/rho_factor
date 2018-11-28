import os
import time
from textwrap import dedent

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
from dash.dependencies import Input, Output, State

from visu import dash_reusable_components as drc
# from visu.figures import serve_prediction_plot, serve_roc_curve, \
#     serve_pie_confusion_matrix


app = dash.Dash(__name__)


app.layout = html.Div(children=[
    # .container class is fixed, .container.scalable is scalable
    html.Div(className="banner", children=[
        # Change App Name here
        html.Div(className='container scalable', children=[
            # Change App Name here
            html.H2(html.A(
                'Surface reflection factor',
                href='https://github.com/Tristanovsk/rho_factor',
                style={
                    'text-decoration': 'none',
                    'color': 'inherit'
                }
            )),

            html.A(
                html.Img(src="https://github.com/Tristanovsk/rho_factor/blob/master/fig/lut_fig_rho_tables_wl550.0nm_aot0.0001.png"),
                href='https://plot.ly/products/dash/'
            )
        ]),
    ]),

    html.Div(id='body', className='container scalable', children=[
        html.Div(className='row', children=[
            html.Div(
                id='div-graphs',
                children=dcc.Graph(
                    id='main_graph',
                    style={'display': 'none'}
                )
            ),

            html.Div(
                className='three columns',
                style={
                    'min-width': '24.5%',
                    'max-height': 'calc(100vh - 85px)',
                    'overflow-y': 'auto',
                    'overflow-x': 'auto',
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
                            name='Time range',
                            id='slider-dataset-sample-size',
                            min=100,
                            max=500,
                            step=100,
                            marks={i: i for i in [100, 200, 300, 400, 500]},
                            value=300
                        ),

                        drc.NamedSlider(
                            name='Exclude spectra',
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
                        html.P(f'Geometry:'),
                        drc.NamedSlider(
                            name='Viewing zenith angle (deg)',
                            id='slider-vza',
                            min=0,
                            max=1,
                            value=0.5,
                            step=0.01
                        ),
                        drc.NamedSlider(
                            name='Azimuth angle (deg)',
                            id='slider-azi',
                            min=0,
                            max=1,
                            value=0.5,
                            step=0.01
                        ),

                        html.Button(
                            'Reset to standard values',
                            id='button-reset'
                        ),
                    ]),

                    drc.Card([
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


@app.callback(Output('slider-vza', 'value'),
              [Input('button-reset', 'n_clicks')],
              [State('main_graph', 'figure')])
def reset_threshold_center(n_clicks, figure):
    if n_clicks:
        Z = np.array(figure['data'][0]['z'])
        value = - Z.min() / (Z.max() - Z.min())
    else:
        value = 0.4959986285375595
    return value

@app.callback(Output('div-graphs', 'children'),
              [Input('dropdown-select-dataset', 'value'),
              ])
def update_svm_graph(kernel,
                     degree,
                     C_coef,
                     C_power,
                     gamma_coef,
                     gamma_power,
                     dataset,
                     noise,
                     shrinking,
                     threshold,
                     sample_size):
    return [
        html.Div(
            className='three columns',
            style={
                'min-width': '24.5%',
                'height': 'calc(100vh - 90px)',
                'margin-top': '5px',

                # Remove possibility to select the text for better UX
                'user-select': 'none',
                '-moz-user-select': 'none',
                '-webkit-user-select': 'none',
                '-ms-user-select': 'none'
            },
            children=[
                dcc.Graph(
                    id='graph-line-roc-curve',
                    style={'height': '40%'},
                    #figure=None
                ),

                dcc.Graph(
                    id='graph-pie-confusion-matrix',
                    #figure=None,
                    style={'height': '60%'}
                )
            ]),

        html.Div(
            className='six columns',
            style={'margin-top': '5px'},
            children=[
                dcc.Graph(
                    id='main_graph',
                    #figure=None,
                    style={'height': 'calc(100vh - 90px)'}
                )
            ])
    ]


external_css = [
#     "https://raw.githubusercontent.com/Tristanovsk/rho_factor/master/visu/assets/base-styles.css"
#     "https://raw.githubusercontent.com/Tristanovsk/rho_factor/master/visu/assets/custom-styles.css",
#
        "https://rawgit.com/xhlulu/9a6e89f418ee40d02b637a429a876aa9/raw/f3ea10d53e33ece67eb681025cedc83870c9938d/base-styles.css"
 ]
#
for css in external_css:
    app.css.append_css({"external_url": css})

# Running the server
if __name__ == '__main__':
    #app.run_server(debug=True)
    app.run_server()