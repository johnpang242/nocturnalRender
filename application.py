from dash import Dash, html, dcc, dash_table, Input, Output, State
import optionPayoffs
import pandas as pd
from collections import OrderedDict
import numpy as np
from scipy.stats import norm

strat = optionPayoffs.strat('',0)

#def addDiagram(types,K,price,qty):

tempData = [["None",0,0,0],["None",0,0,0],["None",0,0,0],["None",0,0,0],["None",0,0,0]]
df = pd.DataFrame(tempData)
df.columns = ['Type','Strike','Price','Position']

tempData2 =[["Spot Price",None], ['Volatility',None],['Risk Free Rate',None],['Days to Expiration',None],['Dividend Yield',None]]
dfapp2 = pd.DataFrame(tempData2)
dfapp2.columns = ['Parameters','Value']

app2Cols = ['Call Value','Call Delta','Call Gamma','Call Theta',"Call Vega",'Call Elst.','- Strike', 'Put Value','Put Delta','Put Gamma','Put Theta','Put Vega','Put Elst.']
app2temp = ['','','','','','','','','','','','','']
app2tempDf = pd.DataFrame([app2temp,app2temp,app2temp,app2temp,app2temp,app2temp,app2temp],columns = app2Cols)



def pRows(rows):
    pruned_rows = []
    # require that all elements in a row are specified
    # the pruning behavior that you need may be different than this
    for row in rows:
        if all([cell != '' for cell in row.values()]):
            pruned_rows.append(row)
    return pruned_rows


def N(d):
  return norm.cdf(d)

def N_prime(d):
  return norm.pdf(d)

def bsData(vals):
    output = {}
    S = vals[0]
    K = vals[1]
    sig = vals[2]
    r = vals[3]
    t = vals[4]/365
    q = vals[5]
    d1 = (np.log(S/K)+t*(r-q+(sig**2)/2))/(sig*np.sqrt(t))
    d2 = d1 - (sig*np.sqrt(t))
    C = S*np.exp(-q*t)*N(d1) - K*np.exp(-r*t)*N(d2)
    P = K*np.exp(-r*t)*N(-d2) - S*np.exp(-q*t)*N(-d1)
    deltaC = N(d1)*np.exp(-q*t)
    deltaP = N(d2)*np.exp(-q*t)
    gammaC = (np.exp(-q*t)/(S*sig*np.sqrt(t)))*N_prime(d1)
    gammaP = (np.exp(-q*t)/(S*sig*np.sqrt(t)))*N_prime(-d1)
    thetaC = (-(((S*sig*np.exp(-q*t))/(2*np.sqrt(t)))*N_prime(d1)) - (r*K*np.exp(-r*t)*N(d2)) + (q*S*np.exp(-q*t)*N(d1)))/365
    thetaP = (-(((S*sig*np.exp(-q*t))/(2*np.sqrt(t)))*N_prime(d1)) + (r*K*np.exp(-r*t)*N(-d2)) - (q*S*np.exp(-q*t)*N(-d1)))/365
    elasticityC = (S*deltaC)/C
    elasticityP = (S*deltaP)/P
    vega = S*np.exp(-q*t)*np.sqrt(t)*N_prime(d1)*0.01
    temp = {'Call Value':C, 'Call Delta':N(d1),'Call Gamma':gammaC,'Call Theta':thetaC,'Call Vega':vega,'Call Elst.':elasticityC,'- Strike': K ,'Put Value':P, 'Put Delta':N(-d1),'Put Gamma':gammaP,'Put Theta':thetaP,'Put Vega':vega,'Put Elst.':elasticityP}
    output = []
    for i in temp.keys():
        if i == 'Call Gamma' or i == "Put Gamma":
            output.append(round(temp[i],6))
        else:
            output.append(round(temp[i],2))
    return output

app = Dash(__name__)

server = app.server

app.layout = html.Div(
    style = {
            "background-color": "#181919",
            "margin-bottom":"10%",
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
        # App1 - Options Payoff Visualizer
        html.Div(
            id = "app1-container",
            style = {
                "background-color": "#181919",
                'verticalAlign':'top',
                #"border-bottom":"2px white solid"
            },
            children = [
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
                                type = 'text',
                                placeholder = "Enter strategy name/id",
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
                                    style_header={
                                        'fontWeight': 'bold',
                                        'color' : '#ffffff',
                                        'textAlign': 'center',
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
                                html.Br(),
                                html.Br(),
                                html.Button(
                                    "Reset",
                                    id = 'Reset',
                                    n_clicks = 0,
                                    style = {
                                        'margin-top':'1%',
                                        'width':'30%',
                                    }
                                ),
                                html.Div(
                                    html.Br(),
                                    style={
                                        'margon-bottom':'20%'
                                    }
                                ),
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
        # Divider1
        html.Div(
            html.Br(),
            style = {
                #"border-bottom":"2px white solid",
                'width':'99%',
                'background-color':'#292a2e',
                "margin-left" : '1%',
                'margin-right':'1%'
            },
        ),
        # App-2
        html.Div(
            id = "app2-container",
            style = {
                "background-color": "#181919",
                'verticalAlign':'top',
                'width':'100%',
                #"border-bottom":"2px white solid"
            },
            children = [
                html.Div(
                    id = 'left-col2',
                    style={
                            "width":"25%",
                            'background-color':'#292a2e',
                            "padding": "2rem 1rem",
                            "margin-left":"1%",
                            'display': 'inline-block',
                            'margin-right':'1%',
                            "color": "#ffffff",
                            'verticalAlign':'top',
                        },
                    className = 'inputs',
                    children = [
                        html.Center(html.B("Options Value Calculator"),style={'margin-top':'2.5%','margin-bottom':'7.5%'}),
                        html.Label("User Inputs",style={'margin-top':'2px','margin-bottom':'2%'}),
                        html.Br(),
                        html.Div(
                            dash_table.DataTable(
                                    id = 'app2-input',
                                    data=dfapp2.to_dict('records'),
                                    columns= [
                                        {'id':'Parameters','name':'Parameters'},
                                        {'id':'Value','name':'Value'},
                                    ],
                                    style_as_list_view=True,
                                    style_cell={
                                        'textAlign': 'center',
                                        'backgroundColor': '#292a2e',
                                        'color':'#ffffff',
                                        },
                                    editable = True
                                    
                            ),
                            style = {
                                'width':'95%',
                                'margin-bottom':'20%'
                            },
                        ),
                        
                    ]
                ),
                html.Div(
                    id = 'rightCol2',
                    style={
                        'height':'100%',
                        "width":"70%",
                        'display': 'inline-block',
                        'float':'right',
                        "verticalAlign": "top"
                    },
                    children =[
                        html.H3('Value & Greeks from Inputs',style = {'color':'#ffffff','margin-left':'5%','margin-top':'2%'}),
                        html.Div(
                            dash_table.DataTable(
                                id = 'greeksTable',
                                #editable = True,
                                fixed_rows={'headers': True},
                                merge_duplicate_headers=True,
                                style_as_list_view=True,
                                style_cell={
                                    'textAlign': 'center',
                                    'backgroundColor': '#292a2e',
                                    'color':'#ffffff',
                                },
                                data = app2tempDf.to_dict('records'),
                                columns = [{"name":[i.split(' ')[0],i.split(' ')[1]], "id": i,'editable':(i == '- Strike')} for i in app2Cols],
                                style_cell_conditional=[{
                                    'if': {
                                        'column_id': '- Strike',
                                    },
                                    'fontWeight': 'bold',
                                    'backgroundColor': "#505154",
                                    'textAlign': 'center',
                                    'color': '#ffffff',
                                    }
                                ],
                            ),
                            style = {'width':'90%',
                                'margin-left':'5%',
                                'margin-bottom':'10%',
                                'height':'85%'
                                }
                        )
                    ]
                )
            ]
            
        ),
        #Divider 2
        html.Div(
            html.Br(),
            style = {
                #"border-bottom":"2px white solid",
                'width':'99%',
                'background-color':'#292a2e',
                "margin-left" : '1%',
                'margin-right':'1%'
            },
        ),
    ]
)


#Callbacks for App1
#   Update Figure
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
#Reset App1
#   Reset name input
@app.callback(
    Output('stratName','value'),    
    Input('Reset','n_clicks'),
)
def resetName(n_clicks):
    return " "
#   Reset spot input
@app.callback(
    Output('spotPrice','value'),    
    Input('Reset','n_clicks'),
)
def resetName(n_clicks):
    return 
#   Reset input table
@app.callback(
    Output('input-table','data'),    
    Input('Reset','n_clicks'),
)
def resetName(n_clicks):
    tempData = [["None",0,0,0],["None",0,0,0],["None",0,0,0],["None",0,0,0],["None",0,0,0]]
    pd.DataFrame(tempData)
    df.columns = ['Type','Strike','Price','Position']
    return df.to_dict('records')

#Callbacks for App2
@app.callback(
    Output('greeksTable','data'),    
    Input('greeksTable','data'),
    State('app2-input','data')
)
def outputGreeks(table1, table2):
    output = []
    t1 = pRows(table1)
    t2 = pRows(table2)
    d = {}
    for r in t2:
        d[r['Parameters']] = r['Value']
    for i in table1:
        if "- Strike" in i.keys():
            if i['- Strike'] != '':
                vals = [int(d['Spot Price']),float(i['- Strike']),float(d['Volatility']),float(d['Risk Free Rate']),float(d['Days to Expiration']),float(d['Dividend Yield'])]
                output.append(bsData(vals))
            else:
                output.append(app2temp)
        else:
            output.append(app2temp)
    odf = pd.DataFrame(output)
    odf.columns = app2Cols
    return odf.to_dict('records')


    

if __name__=='__main__':
    app.run_server(debug = False)
