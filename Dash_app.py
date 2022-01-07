import pandas as pd
import datetime as dt

## Import Dash
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

### Import FOlium
import os 
import folium
from folium import plugins
import rioxarray as rxr
import earthpy as et
import earthpy.spatial as es

## Get Mapbox access token.
px.set_mapbox_access_token("")


df1 = pd.read_csv('data/NFDB_point_20210916.csv', sep=",", encoding ="iso-8859-1")
df2 = df1[((df1.MONTH != 0) | (df1.DAY != 0 )) & (df1.YEAR != 1930)].copy()
names = df2.SRC_AGENCY.value_counts() >= 300
names1=names[names == True].index
df=df2[df2['SRC_AGENCY'].isin(list(names1))].copy()
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUMEN],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}])

app.layout = dbc.Container([

            dbc.Row([
                dbc.Col(html.H1("Canadian Forest Fire Analysis Dashbord 1950 - 2020 ", 
                                className='text-center text-primary mb-4'),
                        width=12)
            ]),
 
            dbc.Row([
              #  html.P("Select only 4 provinces :",
              #  style={"textDecoration": "underline"}),
                dbc.Col([
                html.P("Select only 4 provinces :",
                style={"textDecoration": "underline"}),
                dcc.Dropdown(
                id='my_dropdown',                      # used to identify component in callback
                options=[
                         {'label': x, 'value': x, 'disabled':False}
                         for x in sorted(df['SRC_AGENCY'].unique())
                ],
                value=['AB','SK','QC','ON'],    # values chosen by default
                multi=True,
                ),
                dcc.RadioItems(
                id='crossfilter-xaxis-type',
                options=[{'label': i, 'value': i} for i in ['FIRE_TYPE', 'DECADE','CAUSE','PROTZONE']],
                value='DECADE',
                labelClassName='btn btn-secondary m-2 text-success'
                ),
                dcc.Graph(id='the_graph',figure={})  
                ], #width={'size': 6, 'offset':0, 'order':1}
                  xs=12, sm=12, md=12, lg=5, xl=5 ),
                
                dbc.Col([
                html.P("Select burnt area size (3K= 3000 Hectors) :",
                style={"textDecoration": "underline"}),

                dcc.RadioItems(
                id='crossfilter-xaxis-type_right',
                options=[{'label': i, 'value': i} for i in ['Size_3K_TO_25K','Size_1K_TO_3K','Size_300_TO_1K']],
                value='Size_1K_TO_3K',
                labelClassName='btn btn-secondary m-2 text-success'
                ),
                dcc.Graph(id='the_graph_right',figure={})  
                ], #width={'size': 6, 'offset':0, 'order': 2}
                    xs=12, sm=12, md=12, lg=5, xl=5     ),
   
            ], justify='center'),
            
            dbc.Row([
            dbc.Col([
            html.P("Select Province:",
                   style={"textDecoration": "underline"}),
            dcc.RadioItems(
                id='bar_radio', 
                options=[
                {'label': x, 'value': x, 'disabled':False}
                for x in sorted(df['SRC_AGENCY'].unique())
                ],
                value='BC',    # values chosen by default
                # options=[
                #          {'label': x, 'value': x, 'disabled':False}
                #          for x in sorted(df['SRC_AGENCY'].unique())
                # ],
                # value=['BC'],    # values chosen by default
                labelClassName='btn btn-secondary m-2 text-success'
            ),
            dcc.Graph(id='the_graph_hist', figure={}),
        ], #width={'size':6, 'offset':0},
           xs=12, sm=12, md=12, lg=5, xl=5
        ),
        dbc.Col([
        html.P("Select Province:",
                   style={"textDecoration": "underline"}),
        dcc.RadioItems(
            id='hist_radio',           
           options=[
                {'label': x, 'value': x, 'disabled':False}
                for x in sorted(df['SRC_AGENCY'].unique())
                ],
            value='BC',    # values chosen by default
            labelClassName='btn btn-secondary m-2 text-success'
            ),
        dcc.Graph(id='the_graph_box', figure={}),
        ], #width={'size':6, 'offset':0},
          xs=12, sm=12, md=12, lg=5, xl=5
        ),    
                 
            ], justify='center'),
            
    ], fluid=True)


@app.callback(
    Output(component_id='the_graph', component_property='figure'),
    [Input(component_id='my_dropdown', component_property='value'),
    Input(component_id='crossfilter-xaxis-type', component_property='value')]
)
def update_graph(options_chosen,options_chosen1):
    var1= options_chosen1
    d1 = {}
    for n in range(0,len(options_chosen)):
        df_test=(df[df.SRC_AGENCY == options_chosen[n]])
        d = {'Total_Forest_Fire': df_test[var1].dropna().value_counts(),
             var1: df_test[var1].dropna().unique()}
        d1[n] = pd.DataFrame(data=d)
        del(d)
        del(df_test)

    fig = make_subplots(rows=2, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}],
                                               [{'type':'domain'}, {'type':'domain'}]])
    fig.add_trace(go.Pie(labels=list(d1[0][var1].values),
                            values=d1[0].Total_Forest_Fire.values,name=options_chosen[0],),1, 1)
    fig.add_trace(go.Pie(labels=list(d1[1][var1].values),
                            values=d1[1].Total_Forest_Fire.values,name=options_chosen[1]),1, 2)
    fig.add_trace(go.Pie(labels=list(d1[2][var1].values),
                            values=d1[2].Total_Forest_Fire.values,name=options_chosen[2]),2, 1)
    fig.add_trace(go.Pie(labels=list(d1[3][var1].values),
                            values=d1[3].Total_Forest_Fire.values,name=options_chosen[3]),2, 2)

    fig.update_traces(hole=.32, hoverinfo="label+percent+name")
#    fig.update_layout(height=900, width=1000, showlegend=True)
#    fig.update_layout(height=600, width=700, showlegend=True)
    fig.update_layout(height=570,width=700)
    fig.update_layout(title_text="Distribution of "+ var1,
                        annotations=[
                            dict(text=options_chosen[0], x=0.18, y=0.83, font_size=15, showarrow=False),
                            dict(text=options_chosen[1], x=0.81, y=0.83, font_size=15, showarrow=False),
                            dict(text=options_chosen[2], x=0.19, y=0.19, font_size=15, showarrow=False),
                            dict(text=options_chosen[3], x=0.81, y=0.19, font_size=15, showarrow=False)
                                    ])
    return (fig)

@app.callback(
    Output(component_id='the_graph_right', component_property='figure'),
    [Input(component_id='crossfilter-xaxis-type_right', component_property='value')]
)

def update_graph(options_chosen1):
    #Size_3K_25K_HA','Size_1K_3K_HA','Size_300_1K_HA'
    # Source https://plotly.com/python/scattermapbox/
     mapbox_access_token = open(".mapbox_token").read()
     if options_chosen1 == "Size_3K_TO_25K":
         dff = df[(df.SIZE_HA >= 3000) & (df.SIZE_HA <= 25000)]
         lat=dff['LATITUDE']
         lon=dff['LONGITUDE']

     elif options_chosen1 == "Size_1K_TO_3K":
         dff = df[(df.SIZE_HA >= 1000) & (df.SIZE_HA <= 3000)]
         lat=dff['LATITUDE']
         lon=dff['LONGITUDE']

     else:
         dff = df[(df.SIZE_HA >= 100) & (df.SIZE_HA <= 3000)]
         lat=dff['LATITUDE']
         lon=dff['LONGITUDE']


     fig = px.scatter_mapbox(dff, lat=lat, lon=lon,  color="SIZE_HA", size="SIZE_HA",color_continuous_scale=px.colors.sequential.BuGn,title="Size of area burnt due to Forest Fire in Hectors ",size_max=20, zoom=3,opacity=0.4)
     fig.update_layout(height=600)
     return (fig)

@app.callback(
    Output(component_id='the_graph_hist', component_property='figure'),
    [Input(component_id='bar_radio', component_property='value')]
)

def update_graph(options_chosen):
    dff = df[df['SRC_AGENCY']==options_chosen]
    dff['date']=dff['YEAR'].astype('str') + dff['MONTH'].astype('str')
    dff['date'] = pd.to_datetime(dff['date'], format='%Y%m')
    df_sum = dff.drop(columns=['SRC_AGENCY']).set_index('date').sum(level='date')
    
    ## Source https://plotly.com/python/colorscales/
    fig= px.scatter(df_sum, x=df_sum.index,y='SIZE_HA', 
                    color = 'SIZE_HA',
                    trendline="expanding")
    fig.update_layout( title="Area burnt due to Forest Fire in "+options_chosen,
                      xaxis_title="Years",
                      yaxis_title="Area Burnt (Hectors)")
    return (fig)


@app.callback(
    Output(component_id='the_graph_box', component_property='figure'),
    [Input(component_id='hist_radio', component_property='value')]
)

def update_graph(options_chosen):
#    dff = df[df['SRC_AGENCY'].isin(options_chosen)].groupby(['YEAR','MONTH']).count().reset_index()
    dff = df[df['SRC_AGENCY'] == options_chosen].groupby(['YEAR','MONTH','CAUSE']).count().reset_index()
    print(dff)
    fig = px.box(dff, x='MONTH', y='SIZE_HA',color="CAUSE")
    fig.update_layout( title="Number of Forest Fire incidences in "+options_chosen,
                      xaxis_title="MONTHS",
                      yaxis_title="Number of Fires")
    return fig

# #------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
