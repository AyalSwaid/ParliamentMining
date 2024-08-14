import pandas as pd
import dash
from datetime import datetime, timedelta
from dash import dcc, html, Input, Output
import plotly.express as px
# from wordcloud import WordCloud
# import base64
# import random
# import re
# import nltk
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

df5 = full_df.copy()
countries = df5['country'].unique()
df5['Year'] = df5['date'].dt.year
df5['Year'] = df5['Year'].astype('Int64') 
unique_years = df5['Year'].unique()
unique_years = unique_years.dropna()

color_map = {
    'Economy': '#FFD700',          # Gold/Yellow for economic prosperity
    'Healthcare': '#66B2FF',       # Light Blue for health and well-being
    'Education': '#FF9999',        # Light Red for education and learning
    'Military': '#CCCCCC',         # Gray for military and defense
    'Environment': '#66FF66',      # Green for environmental conservation
    'Judicial System': '#FF66FF',  # Magenta for legal and judicial matters
    'Social Issues': '#FF9933',    # Orange for social issues and welfare
    'Other': '#999999',            # Dark Gray for other/miscellaneous
    'Foreign Policy': '#009900'    # Dark Green for foreign policy
}


def create_dash_app5(flask_app):
    app = dash.Dash(server=flask_app, name = 'CountryInterest', url_base_pathname="/CountryInterest/")

    app.layout = html.Div([
        html.H1("Countries' interests through time", style={'textAlign': 'center'}),
        html.Div([
            html.Label('Select Years:', style={'padding': '5px', 'fontSize': '20px'}),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': i, 'value': i} for i in sorted(unique_years,reverse=True)],
                value=[unique_years.tolist()[0]],  # Default to one year
                multi=True,
                style={'width': '90%', 'margin': '5px'}
            )
        ], style={'width': '33%', 'display': 'inline-block'}),

        # Country Filter Dropdown
        html.Div([
            html.Label('Country:'),
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': country_names[country], 'value': country} for country in df5['country'].unique()],
                value=[df5['country'].unique()[0]],  # Default to one country
                style={'width': '90%', 'display': 'inline-block'},
                multi=True
            )
        ], style={'width': '33%', 'display': 'inline-block'}),

        html.Div(id='pie-charts', style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'center'}),
         html.Div([
            "This visualization showcases the interests of different countries over selected years.", html.Br(),
            "Each pie chart represents the distribution of discussion categories within a specific country and year.", html.Br(),
            "The size of each segment indicates the proportion of discussions dedicated to each category."
        ], style={'textAlign': 'left', 'margin': '20px 0', 'fontSize': '16px'})

    ])

    @app.callback(
        Output('pie-charts', 'children'),
        [Input('year-dropdown', 'value'),
        Input('country-dropdown', 'value')]
    )
    def update_pie_charts(selected_years, selected_countries):
        # print("Selected Years:", selected_years)
        # print("Selected Countries:", selected_countries)

        filtered_df = df5[(df5['Year'].isin(selected_years)) & (df5['country'].isin(selected_countries))]
        
        # print("Filtered DataFrame:")
        # print(filtered_df.head())

        if filtered_df.empty:
            print("No data available for the selected years and countries.")
            return [html.Div('No data available for the selected years and countries.')]

        pie_charts = []
        for country in selected_countries:
            for year in selected_years:
                country_year_df = filtered_df[(filtered_df['country'] == country) & (filtered_df['Year'] == year)]

                if country_year_df.empty:
                    continue  # Skip empty dataframes

                # Flatten the lists of categories
                category_counts = country_year_df['Category'].explode().value_counts()

                # Use the string representations as keys in the color_map dictionary
                colors = [color_map[cat] for cat in category_counts.index]

                fig = go.Figure(data=[go.Pie(
                    labels=category_counts.index,
                    values=category_counts.values,
                    marker=dict(colors=colors)
                )])
                fig.update_layout(title=f'{country_names[country]} Interests in {year}')

                pie_charts.append(
                    html.Div(dcc.Graph(figure=fig), style={'width': '45%', 'margin': '10px'})
                )

        return pie_charts
    return app