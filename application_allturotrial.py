from flask import Flask, url_for, send_file, send_from_directory
from flask import render_template
from markupsafe import escape
from flask import request
import pandas as pd
from datetime import datetime
import urllib
from dash import Dash, dcc, html, Input, Output, State
import json
import plotly
import plotly.express as px


server = Flask(__name__)


@server.route("/")
def home():
    return "Hello, Flask!"


app = Dash(server=server, routes_pathname_prefix="/dash/")

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df1 = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

fig = px.bar(df1, x="Fruit", y="Amount", color="City", barmode="group")

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for your data.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

###################app2 page 2#####################################
app2 = Dash(server=server, routes_pathname_prefix="/dash2/")
app2.layout = html.Div([
    html.H6("Change the value in the text box to see callbacks in action!"),
    html.Div([
        "Input: ",
        dcc.Input(id='my-input', value='initial value', type='text')
    ]),
    html.Br(),
    html.Div(id='my-output'),

])


@app2.callback(
    Output(component_id='my-output', component_property='children'),
    Input(component_id='my-input', component_property='value')
)
def update_output_div(input_value):
    return f'Output: {input_value}'
###################app page 2#####################################finished 


###################app3 page #####################################
df3 = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')

app3 = Dash(server=server, routes_pathname_prefix="/dash3/")

app3.layout = html.Div([
    dcc.Graph(id='graph-with-slider'),
    dcc.Slider(
        df3['year'].min(),
        df3['year'].max(),
        step=None,
        value=df3['year'].min(),
        marks={str(year): str(year) for year in df3['year'].unique()},
        id='year-slider'
    )
])

@app3.callback(
    Output('graph-with-slider', 'figure'),
    Input('year-slider', 'value'))
def update_figure(selected_year):
    filtered_df = df3[df3.year == selected_year]

    fig = px.scatter(filtered_df, x="gdpPercap", y="lifeExp",
                     size="pop", color="continent", hover_name="country",
                     log_x=True, size_max=55)

    fig.update_layout(transition_duration=500)

    return fig
###################app page #####################################finished 




###################app4 page #####################################
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app4 = Dash(server=server, external_stylesheets=external_stylesheets,routes_pathname_prefix="/dash4/")

app4.layout = html.Div([
    dcc.Input(
        id='num-multi',
        type='number',
        value=5
    ),
    html.Table([
        html.Tr([html.Td(['x', html.Sup(2)]), html.Td(id='square')]),
        html.Tr([html.Td(['x', html.Sup(3)]), html.Td(id='cube')]),
        html.Tr([html.Td([2, html.Sup('x')]), html.Td(id='twos')]),
        html.Tr([html.Td([3, html.Sup('x')]), html.Td(id='threes')]),
        html.Tr([html.Td(['x', html.Sup('x')]), html.Td(id='x^x')]),
    ]),
])

@app4.callback(
    Output('square', 'children'),
    Output('cube', 'children'),
    Output('twos', 'children'),
    Output('threes', 'children'),
    Output('x^x', 'children'),
    Input('num-multi', 'value'))
def callback_a(x):
    return x**2, x**3, 2**x, 3**x, x**x
###################app4 page #####################################finished 





###################app5 page #####################################

app5 = Dash(server=server, routes_pathname_prefix="/dash5/")


df5 = pd.read_csv('https://plotly.github.io/datasets/country_indicators.csv')

app5.layout = html.Div([
    html.Div([

        html.Div([
            dcc.Dropdown(
                df5['Indicator Name'].unique(),
                'Fertility rate, total (births per woman)',
                id='xaxis-column'
            ),
            dcc.RadioItems(
                ['Linear', 'Log'],
                'Linear',
                id='xaxis-type',
                inline=True
            )
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                df5['Indicator Name'].unique(),
                'Life expectancy at birth, total (years)',
                id='yaxis-column'
            ),
            dcc.RadioItems(
                ['Linear', 'Log'],
                'Linear',
                id='yaxis-type',
                inline=True
            )
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),

    dcc.Graph(id='indicator-graphic'),

    dcc.Slider(
        df5['Year'].min(),
        df5['Year'].max(),
        step=None,
        id='year--slider',
        value=df5['Year'].max(),
        marks={str(year): str(year) for year in df5['Year'].unique()},

    )
])


@app5.callback(
    Output('indicator-graphic', 'figure'),
    Input('xaxis-column', 'value'),
    Input('yaxis-column', 'value'),
    Input('xaxis-type', 'value'),
    Input('yaxis-type', 'value'),
    Input('year--slider', 'value'))
def update_graph(xaxis_column_name, yaxis_column_name,
                 xaxis_type, yaxis_type,
                 year_value):
    dff = df5[df5['Year'] == year_value]

    fig = px.scatter(x=dff[dff['Indicator Name'] == xaxis_column_name]['Value'],
                     y=dff[dff['Indicator Name'] == yaxis_column_name]['Value'],
                     hover_name=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'])

    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    fig.update_xaxes(title=xaxis_column_name,
                     type='linear' if xaxis_type == 'Linear' else 'log')

    fig.update_yaxes(title=yaxis_column_name,
                     type='linear' if yaxis_type == 'Linear' else 'log')

    return fig




###################appcontinous page #####################################
external_stylesheets_c = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
appchain = Dash(server=server,external_stylesheets=external_stylesheets_c, routes_pathname_prefix="/dashchain/")


all_options = {
    'America': ['New York City', 'San Francisco', 'Cincinnati'],
    'Canada': [u'Montréal', 'Toronto', 'Ottawa']
}
appchain.layout = html.Div([
    dcc.RadioItems(
        list(all_options.keys()),
        'Canada',
        id='countries-radio',
    ),

    html.Hr(),

    dcc.RadioItems(id='cities-radio'),

    html.Hr(),

    html.Div(id='display-selected-values')
])


@appchain.callback(
    Output('cities-radio', 'options'),
    Input('countries-radio', 'value'))
def set_cities_options(selected_country):
    return [{'label': i, 'value': i} for i in all_options[selected_country]]


@appchain.callback(
    Output('cities-radio', 'value'),
    Input('cities-radio', 'options'))
def set_cities_value(available_options):
    return available_options[0]['value']


@appchain.callback(
    Output('display-selected-values', 'children'),
    Input('countries-radio', 'value'),
    Input('cities-radio', 'value'))
def set_display_children(selected_country, selected_city):
    return u'{} is a city in {}'.format(
        selected_city, selected_country,
    )

###################appcontinous page finish #####################################

###################app submit page #####################################

external_stylesheets_s = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app_sub = Dash(server=server,external_stylesheets=external_stylesheets_s, routes_pathname_prefix="/dashsubmit/")

app_sub.layout = html.Div([
    dcc.Input(id='input-1-state', type='text', value='Montréal'),
    dcc.Input(id='input-2-state', type='text', value='Canada'),
    html.Button(id='submit-button-state', n_clicks=0, children='Submit'),
    html.Div(id='output-state')
])


@app_sub.callback(Output('output-state', 'children'),
              Input('submit-button-state', 'n_clicks'),
              State('input-1-state', 'value'),
              State('input-2-state', 'value'))
def update_output_submit(n_clicks, input1, input2):
    return u'''
        The Button has been pressed {} times,
        Input 1 is "{}",
        and Input 2 is "{}"
    '''.format(n_clicks, input1, input2)

###################app submit page finished #####################################


if __name__ == "__main__":
    app.run_server(debug=True,host="127.0.0.1", port=5000)