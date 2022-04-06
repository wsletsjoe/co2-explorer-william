#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import plotly.express as px

#from jupyter_dash import JupyterDash
from dash import dcc, html, Dash
from dash.dependencies import Input, Output

import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template


# In[2]:


dbc_css = 'https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.2/dbc.min.css'
load_figure_template('bootstrap')


# # The CO2 explorer app
# 
# This notebook develops a `dash` application that allows users to explore CO2 emissions around the world and explore potential drivers of CO2 emissions. 

# In[3]:


# dictionary with indicators
indicators = {
    'EN.ATM.CO2E.KT'    : 'CO2 (kt)',    
    'EN.ATM.CO2E.PC'    : 'CO2 emissions (metric tons per capita)',
    'SP.POP.TOTL'       : 'Population, total',
    'SP.URB.TOTL.IN.ZS' : 'Urban population (% of total population)',
    'NY.GDP.PCAP.PP.KD' : 'GDP per capita, PPP (constant 2017 international $)',
    'EG.ELC.ACCS.ZS'    : 'Access to electricity (% of population)',
    'AG.LND.AGRI.ZS'    : 'Agricultural land (% of land area)',
    'NY.GDP.TOTL.RT.ZS' : 'Total natural resources rents (% of GDP)',
    'EG.FEC.RNEW.ZS'    : 'Renewable energy consumption (% of total final energy consumption)'
}


# Import necessary data files:

# In[4]:


# import data on country info
df_info = pd.read_csv('country_info.csv')

# import data on emissions and indicator in 2018
df_2018 = pd.read_csv('data_2018.csv')

# import data on emissions
df_co2 = pd.read_csv('co2_1960_2018.csv')


# Split the CO2 data into a `DataFrame` for total world emissions and into a `DataFrame` with country-level emissions

# In[5]:


# extract world
df_world = df_co2[df_co2['country'] == 'World'].dropna().copy()

# extract countries
df_country = df_co2.merge(df_info, on = 'country', how = 'inner').dropna().copy()


# Define a function that returns a line plot of CO2 emissions over time. Use the function to create a line plot of both total emissions and per capita emissions for the world over time. 

# In[6]:


def create_line(metric, title, df = df_world):
    
    fig = px.line(
        df,
        x = 'year',
        y = metric
    )

    fig.update_layout(
        yaxis_title = None,                         
        xaxis_title = None,                         
        title = title,  
        title_x = 0.5,      
        margin = {'l' : 0, 'r' : 0, 'b' : 0}
    )
    
    return fig

fig_total = create_line('EN.ATM.CO2E.KT', 'Total emissions')
fig_per_capita = create_line('EN.ATM.CO2E.PC', 'Per capita emissions')


# Create the necessary selectors to allow the user to explore the data. There are two dropdown menus for choosing a year and an indicator, and radio buttons for selecting the CO2 metric (total emissions or per capita emissions). All selectors come from the `dash-core-components` module.

# In[7]:


year_dropdown = dcc.Dropdown(
    id = 'my_year',
    options = [{'label' : year, 'value' : year} for year in df_country['year'].unique()],
    value = 2018
)

ind_dropdown = dcc.Dropdown(
    id = 'my_ind',
    options = [
        {'label': 'Population, total', 'value': 'SP.POP.TOTL'},
        {'label': 'CO2 (kt)', 'value': 'EN.ATM.CO2E.KT'},
        {'label': 'Urban population (% of total population)', 'value': 'SP.URB.TOTL.IN.ZS'},
        {'label': 'GDP per capita, PPP (constant 2017 international $)', 'value': 'NY.GDP.PCAP.PP.KD'},
        {'label': 'Access to electricity (% of population)', 'value': 'EG.ELC.ACCS.ZS'},
        {'label': 'Agricultural land (% of land area)', 'value': 'AG.LND.AGRI.ZS'},
        {'label': 'Total natural resources rents (% of GDP)', 'value': 'NY.GDP.TOTL.RT.ZS'},
        {'label': 'Renewable energy consumption (% of total final energy consumption)', 'value': 'EG.FEC.RNEW.ZS'}
    ],
    value = 'SP.URB.TOTL.IN.ZS',
    clearable = False   # very important! (if no value is selected then the callback will throw an error)
)

metric_button = dcc.RadioItems(
    id = 'my_metric',
    options = [{'label' : 'Total', 'value' : 'EN.ATM.CO2E.KT'}, {'label' : 'Per capita', 'value' : 'EN.ATM.CO2E.PC'}], 
    value = 'EN.ATM.CO2E.KT'
)


# Place graphs that visualize CO2 emissions over time inside a `Card` component from `dash-bootstrap-components`. The card contains two `Tab` components, one that visualize total CO2 emissions over time, while the other visualize country-level emissions over time. 

# In[8]:


tab1 = dbc.Tab(
    children = [
        dbc.Row(
            children = [
                dbc.Col(dcc.Graph(figure = fig_total), width = 6),
                dbc.Col(dcc.Graph(figure = fig_per_capita), width = 6)
            ]
        )
    ],
    label = 'Total'
)

tab2 = dbc.Tab(
    children = [
        dbc.Row(
            children = [
                dbc.Col([html.Label('Select year:'), year_dropdown], width = 3), 
                dbc.Col([html.Label('Select metric:'), metric_button], width = 3),
            ]
        ),
        dcc.Graph(id = 'my_map')
    ],
    label = 'By country'
)

card1 = dbc.Card(
    children =  [
        html.H4('CO2 emissions over time', className = 'card-title'),
        html.P('Click on the tabs to explore total or country-level CO2 emissions over time:', className = 'card-text'),
        dbc.Tabs(
            children = [
                tab1,
                tab2
            ]
        )
    ], body = True
)


# Create a second `Card` component that displays a scatter plot between country-level CO2 emissions per capita and potential drivers of emission in 2018. 

# In[9]:


card2 = dbc.Card(
    children = [
        html.H4('Drivers of CO2 emissions', className = 'card-title'),
        html.P('Explore potential drivers of CO2 emissions in 2018 by selecting an indicator from the menu:', className = 'card-text'),
        dbc.Row(dbc.Col(ind_dropdown, width = 6)),
        dcc.Graph(id = 'my_scatter')
    ], 
    body = True
)


# Create a `JupyterDash` app and add the content to the app layout. Add two callback functions, `update_map` and `update_scatter` that allow the user to modify some of the visualizations in the app.

# In[10]:


app = Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP, dbc_css])

server = app.server
app.layout = dbc.Container(
    children = [
        
        # header
        html.H1('CO2 emissions around the world'),
        dcc.Markdown(
            """Data on emissions and potential drivers are extracted from the 
               [World Development Indicators](https://datatopics.worldbank.org/world-development-indicators/) 
               database."""
        ),
        
        # insert cards
        card1,
        html.Br(),
        card2,
        html.Br(),
        
    ],
    className = 'dbc'
)

@app.callback(
    Output('my_map', 'figure'),
    Input('my_metric', 'value'),
    Input('my_year', 'value'),
)
def update_map(metric, year, df = df_country):
    
    subset = df[df['year'] == year].copy()

    fig = px.choropleth(
        subset,                               
        locations = 'iso3c',                  
        color = metric,                  
        color_continuous_scale = 'blues',    
        hover_name = 'country',              
        hover_data = {'iso3c' : False},
    )

    fig.update_layout(
        coloraxis_colorbar_title = None,
        geo_showframe = False,
        margin = {'l' : 0, 'r' : 0, 'b' : 0, 't' : 0}
    )
    
    return fig

@app.callback(
    Output('my_scatter', 'figure'),
    Input('my_ind', 'value'),
)
def update_scatter(xvar, d = indicators, df = df_2018):
    
    fig = px.scatter(
        df,
        x = xvar,
        y = 'EN.ATM.CO2E.PC',
        size = 'SP.POP.TOTL',
        color = 'region',                          
        hover_name = 'country',
        hover_data = {'region' : False, 'SP.POP.TOTL' : False},                
    )

    fig.update_layout(
        yaxis_title = 'CO2 emissions (metric tons per capita)',                    
        xaxis_title = d[xvar], 
        legend_title_text = None,                
    )
    
    return fig

if __name__ == '__main__':
    
    app.run_server(debug = True)


# In[ ]:




