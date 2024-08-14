import pandas as pd
import dash
from datetime import datetime, timedelta
from dash import dcc, html, Input, Output
import plotly.express as px
from wordcloud import WordCloud
import base64
import random
import re
import nltk
# from nltk.sentiment import SentimentIntensityAnalyzer
# nltk.download('vader_lexicon')
# nltk.download('punkt')
# nltk.download('stopwords')
import plotly.graph_objs as go
# import openai
# from openai import OpenAI
import json
import os
from io import BytesIO
from itertools import chain
import flask


full_df = pd.read_csv(r"C:\Users\user\Desktop\v22.csv")
full_df['Category'] = full_df['Category'].apply(json.loads)
full_df['date'] = pd.to_datetime(full_df['date'], format='%Y-%m-%d', errors='coerce')
country_names = {1: 'United States', 2: "United Kingdom", 3: "Israel", 4: "Canada", 5: 'Tunisia'}
real_data = full_df.copy()
wanted_categories = ['Economy', 'Education', 'Environment', 'Foreign Policy', 'Healthcare', 'Judicial System', 'Military', 'Social Issues', 'Other']

df3 = full_df.copy()
df3['date'] = pd.to_datetime(df3['date'], format='%Y-%m-%d', errors='coerce')
df3['Year'] = df3['date'].dt.year
df3['Year'] = df3['Year'].astype('Int64')

df3['Country'] = df3['country'].map(country_names)
df3['GlobalIssue'] = df3['Category'].apply(lambda x: [item for item in x])
# print(df3)
df3_exploded = df3.explode('GlobalIssue')

# Now, you can group by the exploded 'GlobalIssue' column
df_grouped = df3_exploded.groupby(['Year', 'Country', 'GlobalIssue']).size().reset_index(name='Discussions')

unique_years = df_grouped['Year'].unique()
unique_countries = df_grouped['Country'].unique()
unique_global_issues = df_grouped['GlobalIssue'].unique()

country_colors = {
    'United States': '#EF553B',  # Default color for United States
    'United Kingdom': '#FFA15A',  # Default color for United Kingdom  US
    'Israel': '#636EFA',  # Default color for Israel
    'Canada': '#AB63FA',  # Default color for Canada
    'Tunisia': '#00CC96'  # Default color for Tunisia
}

def create_dash_app3(flask_app):
    app = dash.Dash(server=flask_app, name = 'GlobalIssues', url_base_pathname="/GlobalIssues/")
    app.layout = html.Div([
        html.H1('Parliamentary Discussions Analysis', style={'textAlign': 'center'}),

        html.Div([
            # Time Filter Dropdown (Year)
            html.Div([
                html.Label('Select Time (Year):', style={'padding': '5px', 'fontSize': '20px'}),
                dcc.Dropdown(
                    id='time-filter3',
                    options=[{'label': i, 'value': i} for i in unique_years],
                    value=unique_years.tolist(),  # Default to all years
                    multi=True,
                    style={'width': '90%', 'margin': '5px'}
                )
            ], style={'width': '33%', 'display': 'inline-block'}),

            # Country Filter Dropdown
            html.Div([
                html.Label('Select Country:', style={'padding': '5px', 'fontSize': '20px'}),
                dcc.Dropdown(
                    id='country-filter3',
                    options=[{'label': i, 'value': i} for i in unique_countries],
                    value=unique_countries.tolist(),  # Default to all countries
                    multi=True,
                    style={'width': '90%', 'margin': '5px'}
                )
            ], style={'width': '33%', 'display': 'inline-block'}),

            # Global Issue Filter Dropdown
            html.Div([
                html.Label('Select Global Issue:', style={'padding': '5px', 'fontSize': '20px'}),
                dcc.Dropdown(
                    id='global-issue-filter3',
                    options=[{'label': i, 'value': i} for i in wanted_categories],  # WANTED CATEGORIES AND NOT GLOBAL ISSUES
                    value=[wanted_categories[0]],  # Default to first issue
                    multi=True,
                    style={'width': '90%', 'margin': '5px'}
                )
            ], style={'width': '33%', 'display': 'inline-block'})
        ], style={'display': 'flex', 'flexWrap': 'wrap'}),

        dcc.Graph(id='bar-chart'),
                html.Div([
            "This bar chart shows the percentage of parliamentary discussions dedicated to various global issues over selected years and countries. ",html.Br(),
            "The x-axis represents the year, and the y-axis represents the percentage of discussions.",html.Br(),
            "The bars are grouped by country, and the hover text provides details about the global issue and the number of discussions."],
            style={'textAlign': 'left', 'margin': '20px 0', 'fontSize': '16px'})])


    @app.callback(
        Output('bar-chart', 'figure'),
        [Input('time-filter3', 'value'),
        Input('country-filter3', 'value'),
        Input('global-issue-filter3', 'value')]
    )
    def update_chart(selected_years, selected_countries, selected_global_issues):
                # Filter the DataFrame to include only discussions about the selected years and countries
        filtered_df = df_grouped[
            (df_grouped['Year'].isin(selected_years)) &
            (df_grouped['Country'].isin(selected_countries))
        ].copy()  # Create a copy of the DataFrame
        # Calculate total discussions for each country in each year
        total_discussions_per_country = filtered_df.groupby(['Year', 'Country'])['Discussions'].transform('sum')

        # Filter the DataFrame to include only discussions about the selected global issues
        filtered_df_global = df_grouped[
            (df_grouped['GlobalIssue'].isin(selected_global_issues)) &
            (df_grouped['Year'].isin(selected_years)) &
            (df_grouped['Country'].isin(selected_countries))
        ].copy()

        # Calculate the percentage of discussions dedicated to the selected global issues for each country in each year
        filtered_df_global['Percentage'] = (filtered_df_global['Discussions'] / total_discussions_per_country) * 100
        filtered_df_global['Discussions'] = filtered_df_global['Discussions']

        fig = px.bar(
            filtered_df_global,
            x='Year',
            y='Percentage',
            color='Country',
            barmode='group',
            title='Global Issues Analysis',
            hover_data={'GlobalIssue': True, 'Discussions': True},  # Include Discussions in hover data
            color_discrete_map=country_colors
        )

        # Customize hover text to include category information and number of discussions
        fig.update_traces(hovertemplate='<br>'.join([
            'Year: %{x}',
            'Global Issue: %{customdata[0]}',
            'Discussions: %{customdata[1]}',
            'Percentage: %{y:.2f}%'
        ]))
        fig.update_yaxes(ticksuffix="%")

        return fig
    return app