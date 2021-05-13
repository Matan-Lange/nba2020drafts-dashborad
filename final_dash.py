import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import numpy as np
from datetime import datetime

players = ['Anthony Edwards', 'James Wiseman', ' LaMelo Ball', 'Patrick Williams', 'Isaac Okoro', 'Onyeka Okongwu',
           'Killian Hayes'
    , 'Obi Toppin', 'Deni Avdija', 'Jalen Smith']
stats = ['points', 'min', 'fgm', 'fga', 'fgp', 'ftm',
         'fta', 'ftp', 'tpm', 'tpa', 'tpp', 'offReb', 'defReb', 'totReb',
         'assists', 'pFouls', 'steals', 'turnovers', 'blocks', 'plusMinus']

# prepdata
df = pd.read_csv('data_10draft')
df.fillna(0, inplace=True)


def f(x):
    if x == '' or x == np.nan:
        return 0
    else:
        return float(x)


def sortdate(x):
    date = x.split('T')[0]
    return datetime.strptime(date, '%Y-%m-%d')


def minset(x):
    if type(x) == str:
        return x.replace(":", ".")
    else:
        return x


for name in stats:
    if name == 'min':
        df['min'].fillna(0, inplace=True)
        df['min'] = df['min'].apply(minset)

    df[df[name].isna()] = 0
    df[name] = df[name].apply(f)

df['startTimeUTC'] = df['startTimeUTC'].apply(sortdate)

# dash app

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )
server = app.server

app.layout = dbc.Container([

    dbc.Row(
        dbc.Col(html.H1("2020 Top-10 NBA drafts",
                        className='text-center text-primary mb-4 '),
                width=12)
    ),

    dbc.Row([

        # dbc.Col([

        # dcc.DatePickerRange(
        # id='my-date-picker-range',
        # min_date_allowed=date(2020, 12, 1),
        # max_date_allowed=date(2021, 4, 21),
        # initial_visible_month=date(2020, 12, 1),
        # end_date=date(2021, 4, 21))
        # ], width={'size': 2}),

        dbc.Col([
            dcc.Dropdown(id="slct_stats",
                         options=[
                             {"label": x, "value": x} for x in stats],
                         multi=True,
                         value="points",
                         style={'background-color': '#d0d0d0',
                                'border-color': '#000000'}
                         ),

                dcc.Graph(id='line-fig1', figure={})
        ], width={'size': 5, 'offset': 0, 'order': 1}),
        # xs=12, sm=12, md=12, lg=6, xl=5),

        dbc.Col([
            dcc.Dropdown(id="slct_player",
                         options=[{"label": x, "value": x} for x in players],
                         multi=True,
                         value='Deni Avdija',
                         style={'background-color': '#d0d0d0',
                                'border-color': '#000000'}),

            dcc.Graph(id='line-fig2', figure={})
        ], width={'size': 5, 'offset': 0, 'order': 2})
        # xs=12, sm=12, md=12, lg=6, xl=5)

    ], no_gutters=True, justify='center'),  # Horizontal:start,center,end,between,around

    dbc.Row([

        dbc.Col([

            dcc.Graph(id='line-fig3', figure={})

        ], width={'size': 10})

    ], justify='center')

], fluid=True, style={'background-color': '#d0d0d0'})




@app.callback(
    [Output(component_id='line-fig1', component_property='figure'),
     Output(component_id='line-fig3', component_property='figure'),
     Output(component_id='line-fig2', component_property='figure')
     ],
    [  # Input(component_id='slct_year', component_property='value'),
        Input(component_id='slct_stats', component_property='value'),
        Input(component_id='slct_player', component_property='value')]
)

def update_graphs(stat, players):
    dff = df.copy()
    # show relevent players
    if type(players) == list:
        names = [name.split()[1] for name in players]
        dff = dff[dff['lastName'].isin(names)]
    else:
        dff = dff[dff['lastName'].isin([players.split()[1]])]
        names = [players.split()[1]]

    if type(stat) == list:
        pass
    else:
        stat = [stat]
    #first graph
    fig1 = px.bar(dff.groupby('lastName').mean()[stat], barmode="group")
    fig1.update_layout(paper_bgcolor="#d0d0d0",
                       plot_bgcolor="#d0d0d0", title='mean stats over season', title_x=0.5)
    fig1.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=True, title='player name')
    fig1.update_yaxes(showline=True, linewidth=1, linecolor='black', mirror=True)

    # second graph
    fig2 = go.Figure()
    line_stat = stat[0]
    for player in names:
        fig2.add_trace(go.Scatter(x=dff[dff['lastName'] == player]['startTimeUTC']
                                  , y=dff[dff['lastName'] == player][line_stat], name=player, mode='lines+markers'))
    fig2.update_layout(paper_bgcolor="#d0d0d0",
                       plot_bgcolor="#d0d0d0",
                       title='stats over the season(first stat in dropdown)', title_x=0.5)
    fig2.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=True)
    fig2.update_yaxes(showline=True, linewidth=1, linecolor='black', mirror=True)

    # third graph
    fig3 = go.Figure()
    for player in names:
        r_v = []
        for s in stat:
            r_v.append(dff[dff['lastName'] == player][s].mean())

        fig3.add_trace(go.Scatterpolar(
            r=r_v,
            theta=stat,
            fill='toself',
            name=player))

    # update len of radar chart if min stat showed
    if 'min' in stat:
        up = 40
    else:
        up = 20

    fig3.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, up]
            )),
        showlegend=True,
    )
    fig3.update_layout(paper_bgcolor="#d0d0d0",
                       plot_bgcolor="#d0d0d0")


    return fig1, fig2, fig3


if __name__ == '__main__':
    app.run_server(debug=True)
