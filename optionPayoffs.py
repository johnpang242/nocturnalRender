import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import init_notebook_mode, iplot, plot
class Option:
    def __init__(self, type_, K, price, side):
        self.type = type_
        self.K = K
        self.price = price
        self.side = side
    
    def __repr__(self):
        side = 'long' if self.side == 1 else 'short'
        return f'Option(type={self.type},K={self.K}, price={self.price},side={side})'

class strat:
    def __init__(self, name, S0):
        self.name = name
        self.S0 = S0
        self.STs = np.arange(0, S0*3, 1)
        self.payoffs = np.zeros_like(self.STs)
        self.instruments = [] 
           
    def long_call(self, K, C, Q=1):
        payoffs =  np.array([max(s-K,0)  - C for s in self.STs])*Q
        self.payoffs = self.payoffs +payoffs
        self._add_to_self('call', K, C, 1, Q)
        print('call', K, C, 1, Q)
    
    def short_call(self, K, C, Q=1):
        payoffs =  np.array([max(s-K,0) * -1 + C for s in self.STs])*Q
        self.payoffs = self.payoffs + payoffs
        self._add_to_self('call', K, C, -1, Q)
    
    def long_put(self, K, P, Q=1):
        payoffs = np.array([max(K-s,0) - P for s in self.STs])*Q
        self.payoffs = self.payoffs + payoffs
        self._add_to_self('put', K, P, 1, Q)
        print('put', K, P, 1, Q)
        
    def short_put(self, K, P, Q=1):
        payoffs = np.array([max(K-s,0)*-1 + P for s in self.STs])*Q
        self.payoffs = self.payoffs + payoffs
        self._add_to_self('put', K, P, -1, Q)

    def long_spot(self, spot, Q=1):
      K = 0
      C = 0
      payoffs =  np.array([(s-spot)  - C for s in self.STs])*Q
      self.payoffs = self.payoffs +payoffs - spot
      self._add_to_self('spot', K, C, 1, Q)

    def short_spot(self, spot, Q=1):
      K = 0
      C = 0
      payoffs =  np.array([(s-spot) * -1 + C for s in self.STs])*Q
      self.payoffs = self.payoffs + payoffs 
      self._add_to_self('spot', K, C, -1, Q)

    def _add_to_self(self, type_, K, price, side, Q):
        o = Option(type_, K, price, side)
        for _ in range(Q):
            self.instruments.append(o)
    
    def plot2(self,name = "Unnamed Strategy" ,lowerLimit = 0,upperLimit=2):
        yProfit = []
        yLoss = []
        for i in self.payoffs:
            yProfit.append(max(i,0))
            yLoss.append(min(i,0))
        df = pd.DataFrame()
        df["Price at Expiration"] = self.STs
        df["PnL ($)"] = self.payoffs
        df['yProfit'] = yProfit
        df['yLoss'] = yLoss
        df = df[df['Price at Expiration'].between(lowerLimit*self.S0,upperLimit*self.S0,inclusive = "both")]
        fig = go.Figure()
        fig.update_layout(title_font_color='#ffffff')
        fig.add_trace(go.Scatter(x=self.STs, y=df.yProfit,fill='tozeroy', fillcolor='rgba(38,255,82,0.5)',
                        hoveron = 'points+fills', # select where hover is active
                        line_color='#6495ED',
                        text="Price at Expiration : PnL",
                        hoverinfo = 'text+x+y',))
        
        fig.add_trace(go.Scatter(x=self.STs, y=df.yLoss,fill='tozeroy', fillcolor='rgba(250,50,50,0.5)',
                        hoveron = 'points+fills', # select where hover is active
                        line_color='#6495ED',
                        text="Price at Expiration,PnL",
                        hoverinfo = 'text+x+y'))
        fig.add_hline(y=0)
        fig.update_layout(
            paper_bgcolor="rgb(0,0,0,0)",
            showlegend=False,
            title="<b>Payoff - %s </b>"%name,
            xaxis_title="<b>Price at Expiration</b>",
            yaxis_title="<b>PnL ($)</b>",
            font=dict(
                family="Times New Roman, Serif",
                size=12,
                color="white"
            ),
            autosize=True,
            template = 'plotly_dark'
        )

        return fig
    
    
    def describe(self):
        max_profit  = self.payoffs.max()
        max_loss = self.payoffs.min()
        outstr = ""
        outstr+=(f"Max Profit: ${round(max_profit,3)}")
        outstr+= "\n"
        outstr+=(f"Max Loss: ${round(max_loss,3)}")
        outstr+= "\n"
        c = 0
        xC = 0
        for o in self.instruments:
            #print(o)
            if o.type == 'call' and o.side==1:
                c += o.price
            elif o.type == 'call' and o.side == -1:
                c -= o.price
                xC += o.K*0.3
            elif o.type =='put' and o.side == 1:
                c += o.price
            elif o.type =='put' and o.side == -1:
                c -+ o.price
                xC += o.K*0.3
        outstr+=(f"Cost of entering position ${c}")
        outstr+= "\n"
        outstr+=(f"Extra collateral required ${xC}")
        return outstr

