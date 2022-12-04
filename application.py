from dash import Dash, html, dcc, dash_table, Input, Output, State
import optionPayoffs
import pandas as pd
from collections import OrderedDict

strat = optionPayoffs.strat('',0)

#def addDiagram(types,K,price,qty):

tempData = [["None",0,0,0],["None",0,0,0],["None",0,0,0],["None",0,0,0],["None",0,0,0]]
df = pd.DataFrame(tempData)
df.columns = ['Type','Strike','Price','Position']


app = Dash(__name__)

application = app.server

app.layout = html.Div(
    style = {
            "background-color": "#181919",
            "margin-bottom":"10%"
    },
    children = [
    html.Div(
        id = "app-container",
        style = {
            "background-color": "#181919",
            'verticalAlign':'top',
            "border-bottom":"2px white solid"
        },
        children = [
            #Banner
            html.Center(
                id = "banner",
                style = {
                    "background-color": "#181919",
                    "border-bottom":"2px white solid"
                },
                className = "banner",
                children = [
                    #Logo
                    html.Div(html.Img(src= "https://raw.githubusercontent.com/johnpang242/nocturnal/main/nocturnal-logo-4.png", style={'height':'10%', 'width':'10%'}))
                ],
            ),
            html.Div(
                    id = 'leftCol',
                    style={
                        "width":"25%",
                        'background-color':'#292a2e',
                        "padding": "2rem 1rem",
                        "margin-left":"1%",
                        'display': 'inline-block',
                        'margin-right':'1%',
                        "color": "#ffffff"
                    },
                    className = 'inputs',
                    children = [
                        html.Center(html.B("Options Payoff Visualizer"),style={'margin-top':'2.5%','margin-bottom':'7.5%'}),
                        html.Label("Name",style={'margin-top':'2px','margin-bottom':'1px'}),
                        html.Br(),
                        dcc.Input(
                            id = 'stratName',
                            placeholder = "Enter strategy name/id",
                            type = 'text',
                            style = {
                                'width':'90%',
                                'backgroundColor': '#afb2bd'
                            }
                        ),
                        html.Br(),
                        html.Br(),
                        html.Label("Underlying Spot Price",style={'margin-top':'2px','margin-bottom':'1px'}),
                        html.Br(),
                        dcc.Input(
                            id = 'spotPrice',
                            type='number',
                            placeholder = "Enter current spot price",
                            style = {
                                'width':'90%',
                                'margin-bottom':'1%',
                                'backgroundColor': '#afb2bd'
                            }
                        ),
                        
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Div(
                            dash_table.DataTable(
                                id = 'input-table',
                                data=df.to_dict('records'),
                                columns= [
                                    {'id':'Type','name':'Type','presentation':'dropdown'},
                                    {'id':'Strike','name':'Strike'},
                                    {'id':'Price','name':'Price'},
                                    {'id':'Position','name':'Position'}
                                ],
                                #[{'id': c, 'name': c} for c in df.columns],
                                editable = True,
                                dropdown = {
                                    'Type': {
                                        'options':[
                                            {'label':'Call','value':'Call'},
                                            {'label':'Put','value':'Put'},
                                            {'label':'Spot','value':'Spot'},
                                        ]
                                    }
                                },
                                style_as_list_view=True,
                                style_cell={
                                    'textAlign': 'center',
                                    'backgroundColor': '#292a2e'
                                    },
                            ),
                            style = {
                                'width':'95%'
                            },
                            ),
                            html.Button(
                                "Visualize",
                                id = 'visuals',
                                n_clicks = 0,
                                style = {
                                    'margin-top':'1%',
                                    'width':'95%',
                                }
                            ),
                            html.Div(
                                html.Br(),
                                style={
                                    'margon-bottom':'30%'
                                }
                            )
                    ]
                ),
            html.Div(
                id = 'rightCol',
                style={
                    'height':'100%',
                    "width":"70%",
                    'display': 'inline-block',
                    'float':'right',
                },
                children = [
                    dcc.Graph(
                        id = 'outputGraph',
                        figure = strat.plot2(),
                        style={
                            'height':'90%',
                            'width':'100%',
                            'margin-top':'5%',
                            'margin-bottom':'5%',
                            'float':'left'
                        }
                        ),
                ]
            )

        ]
    ),
    html.Div(
        html.Br(),
        id = 'seperator',
        style = {
        },
    )

])



@app.callback(
    Output('outputGraph','figure'),    
    Input('visuals','n_clicks'),
    State("stratName",'value'),
    State('spotPrice','value'),
    State('input-table', 'data'),
)
def update_output(n_clicks,value1,value2,rows):
    global strat
    strat = optionPayoffs.strat(value1,value2)
    pruned_rows = []
    for row in rows:
        # require that all elements in a row are specified
        # the pruning behavior that you need may be different than this
        if all([cell != '' for cell in row.values()]):
            pruned_rows.append(row)
        
    for i in pruned_rows:
        strike = int(i['Strike'])
        price = int(i['Price'])
        pos = int(i['Position'])
        if i['Type'] == "Call":
            if pos > 0:
                strat.long_call(strike,price,abs(pos))
            elif pos < 0:
                strat.short_call(strike,price,abs(pos))
            else:
                pass
        if i['Type'] == "Put":
            if pos > 0:
                strat.long_put(strike,price,abs(pos))
            elif pos < 0:
                strat.short_put(strike,price,abs(pos))
            else:
                pass
        if i['Type'] == 'Spot':
            if pos > 0:
                strat.long_spot(strike,abs(pos))
            elif pos < 0:
                strat.short_spot(strike,abs(pos))
            else:
                pass
    return strat.plot2(value1,0,2)

if __name__=='__main__':
    application.run(host='0.0.0.0', port='8080')