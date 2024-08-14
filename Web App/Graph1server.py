import pandas as pd
import dash
from datetime import datetime, timedelta
from dash import dcc, html, Input, Output
# from wordcloud import WordCloud
# import base64
import random
# import re
# import nltk
# from nltk.sentiment import SentimentIntensityAnalyzer
# nltk.download('vader_lexicon')
# nltk.download('punkt')
# nltk.download('stopwords')
import plotly.graph_objs as go
import openai
# from openai import OpenAI
import json
from io import BytesIO
import os




full_df = pd.read_csv(r"C:\Users\user\Desktop\v22.csv")
full_df['Category'] = full_df['Category'].apply(json.loads)
full_df['date'] = pd.to_datetime(full_df['date'], format='%Y-%m-%d', errors='coerce')
full_df['file_path'] = full_df['file_path'].apply(str)
country_names = {1: 'United States', 2: "United Kingdom", 3: "Israel", 4: "Canada", 5: 'Tunisia'}
real_data = full_df.copy()
wanted_categories = ['Economy', 'Education', 'Environment', 'Foreign Policy', 'Healthcare', 'Judicial System', 'Military', 'Social Issues', 'Other']
news_df1 = pd.read_csv(r"C:\Users\user\Desktop\news.csv")
news_df1['Category'] = news_df1['Category'].apply(json.loads)
news_df1['date'] = pd.to_datetime(news_df1['date'], format='%Y-%m-%d', errors='coerce')

client = openai.OpenAI(
    # This is the default and can be omitted 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
    api_key='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',
)


def generate_explanation(files, titles, country, category, date):
    full_text = ''
    d = r'C:\Users\user\Desktop'
    for file in files:
        path = os.path.join(d, file)
        with open(path, 'r') as json_file:
            alltext = json.load(json_file) 
        partial_full_text=''
        for speech_obj in alltext:
            speech = speech_obj.get('speech', '')
            if len(partial_full_text)<500 and len(speech) <100:
                partial_full_text += speech 
            elif len(partial_full_text)<500 and len(speech)>100: 
                 partial_full_text+=speech[:100]
            else:
                break  
        if len(full_text)+len(partial_full_text)<700:
            full_text+=partial_full_text 
        else:
            full_text+=partial_full_text 
            full_text=full_text[:700] 

    message = f"I have sampled some parliamentary discussions from a dataset focusing on {category} in {country} on {date}, where there was a noticeable spike marked as an outlier. Here are excerpts from the discussions concatenated one after the other: {full_text}. These are the titles: {titles} .Based on these excerpts, can you provide potential reasons or insights that might explain why these discussions are considered outliers on this date?, i want you to return as little text as possible while explaining the reason (max 20 words NO MORE)."
    # message = f"The following text is a partial transcription of parliamentary debates. These debates occurred because of a significant issue. Analyze the concatenated debate titles and text to determine the main issue or reason for the debates.this is the partial debates text{full_text} this is the titles-{titles}. Provide a concise explanation (maximum 10 tokens) of the issue."

    chat_completion = client.chat.completions.create(
                messages=[
                {
                    "role": "user",
                    "content": message,
                }
            ],
            model="gpt-3.5-turbo-0125" # gpt-3.5-turbo-1106 gpt-3.5-turbo-0125 gpt-4o

        )
        # print(partial_full_text)
    return chat_completion.choices[0].message.content


def generate_explanation_news(df, country, category, date):
    # Filter the dataframe for relevant data
    start_date = date.start_time  # Start of the period
    end_date = date.end_time  # End of the period

    # Filter the dataframe for relevant data
    # Check if dates fall within the period
    articles = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    # articles = df[(df['date'] == pd.to_datetime(date))]

    # full_text = ""
    titles = ""
    for index, row in articles.iterrows():  # This ensures 'row' is a Series
        # article = row['content']  # Now 'row' is correctly accessed
        title = row['title']
        # if len(article) > 500:
        #     article = article[:500]
        # full_text += article
        titles += title

    # print('this is the full text',full_text)
    message = f"I have sampled some news articles from a dataset focusing on {category} in {country} on {date}, where there was a noticeable spike marked as an outlier. Here are the titles of the news articles from that time and from that category concatenated one after the other: {titles}. Based on these excerpts, can you provide potential reasons or insights that might explain why these discussions are considered outliers on this date?,i want you to return as little text as possible while explaining the reason (max 20 words NO MORE)."
    # message = f"The following text is a partial transcription of parliamentary debates. These debates occurred because of a significant issue. Analyze the concatenated debate titles and text to determine the main issue or reason for the debates.this is the partial debates text{full_text} this is the titles-{titles}. Provide a concise explanation (maximum 10 tokens) of the issue."

    chat_completion = client.chat.completions.create(
                messages=[
                {
                    "role": "user",
                    "content": message,
                }
            ],
            model="gpt-3.5-turbo-0125" # gpt-3.5-turbo-1106 gpt-3.5-turbo-0125 gpt-4o
        )
        # print(partial_full_text)
    return chat_completion.choices[0].message.content

def get_files_for_date(date_str,df):
    df['Category'] = df['Category'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else '')
    month = pd.to_datetime(date_str).month
    thing = df[(df['date'].dt.month == month)]
    
    if not thing.empty:
        return df[(df['date'].dt.month == month)]['file_path'].tolist()
    else:
        return None

def get_titles_for_date(date_str,df): 
    df['Category'] = df['Category'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else '')
    month = pd.to_datetime(date_str).month
    return df[(df['date'].dt.month == month)]['debate_title']


def count_discussions_per_day(df):
    discussions_per_day = df.groupby(df['date'].dt.date).size()
    return discussions_per_day

def count_articles_per_day(df):
    articles_per_day = df.groupby(df['date'].dt.date).size()
    return articles_per_day

def calculate_lagged_correlation(series1, series2, max_lag):
    correlations = {}
    for lag in range(-max_lag, max_lag + 1):
        if lag < 0:
            shifted_series = series1.shift(-lag)
            correlation = series2.corr(shifted_series)
        else:
            shifted_series = series2.shift(lag)
            correlation = series1.corr(shifted_series)
        correlations[lag] = correlation
    return correlations

def smooth_series(series, window_size):
    return series.rolling(window=window_size, center=True).mean()

def normalize_series(series):
    return (series - series.mean()) / series.std()

def create_dash_app1(flask_app):
    app = dash.Dash(server=flask_app, name = 'TrendAnalysis', url_base_pathname="/trendanalysis/")
    
    app.layout = html.Div([
        html.H1('Parliamentary Trend Analysis', style={'textAlign': 'center'}),
        html.Div([
            html.Label("Select Country:"),
            dcc.Dropdown(
                id='country-dropdown1',
                options=[{'label': country_names[country], 'value': country} for country in real_data['country'].unique()],
                value=real_data['country'].unique()[0],
                style={'width': '45%', 'display': 'inline-block'}
            ),
        ], style={'margin-bottom': '10px'}),

        html.Div([
            html.Label("Select Category:"),
            dcc.Dropdown(
                id='category-dropdown1',
                options=[{'label': category, 'value': category} for category in wanted_categories],
                value=wanted_categories[0],
                style={'width': '45%', 'display': 'inline-block'}
            ),
        ], style={'margin-bottom': '10px'}),

        html.Div([
            html.Label("Select Time Period:"),
            dcc.DatePickerRange(
                id='date-range-picker1',
                min_date_allowed=min(real_data['date']),
                max_date_allowed=max(real_data['date']),
                initial_visible_month=max(real_data['date']),
                start_date=min(real_data['date']),
                end_date=max(real_data['date']),
                display_format='DD/MM/YYYY',
                style={'width': '45%', 'display': 'inline-block'}
            ),
        ], style={'margin-bottom': '10px'}),

        dcc.Graph(id='line-plot'),
        html.Div(id='graph-description2', style={'textAlign': 'left', 'margin': '20px 0', 'fontSize': '16px'})
    ])

    @app.callback(
        Output('line-plot', 'figure'),
        [Input('country-dropdown1', 'value'),
        Input('category-dropdown1', 'value'),
        Input('date-range-picker1', 'start_date'),
        Input('date-range-picker1', 'end_date')]
    )
    def update_graph(selected_country, selected_category, start_date, end_date):
        start_date = pd.Timestamp(start_date)
        end_date = pd.Timestamp(end_date) + pd.offsets.MonthEnd(0)

        filtered_discussions_df = real_data[(real_data['country'] == selected_country) &
                                            (real_data['Category'].apply(lambda x: selected_category in x)) &
                                            (real_data['date'] >= start_date) &
                                            (real_data['date'] <= end_date)]

        if filtered_discussions_df.empty:
            layout = go.Layout(title='No discussions found for the selected criteria',
                            xaxis_title='Date', yaxis_title='Count')
            return {'data': [], 'layout': layout}

        time_diff = end_date - start_date

        if time_diff <= timedelta(days=60):
            freq = 'D'
        elif time_diff <= timedelta(days=365):
            freq = 'W-Mon'
        elif time_diff <= timedelta(days=730):
            freq = '2W-Mon'
        else:
            freq = 'ME'

        discussions_per_week = filtered_discussions_df.resample(freq, on='date').size()

        Q1 = discussions_per_week.quantile(0.25)
        Q3 = discussions_per_week.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.65 * IQR
        upper_bound = Q3 + 1.65 * IQR
        outliers_mask = (discussions_per_week < lower_bound) | (discussions_per_week > upper_bound)
        
        outlier_dates = discussions_per_week.index[outliers_mask] 
        outlier_values = discussions_per_week[outliers_mask]

        actual_start_date = discussions_per_week.index.min()
        actual_end_date = discussions_per_week.index.max()

        filtered_news_df = news_df1[(news_df1['country'] == selected_country) &
                                    (news_df1['Category'].apply(lambda x: selected_category in x)) &
                                    (news_df1['date'] >= start_date) &
                                    (news_df1['date'] <= end_date)]

        outlier_explanations = []
        filtered_news_df['year_month'] = filtered_news_df['date'].dt.to_period('M')
        for date in outlier_dates:
            df = filtered_news_df.copy()
            date_period = date.to_period('M')  # Convert date to period
            # Directly check if the period is in the 'year_month' column
            if date_period in df['year_month'].values:
                explanation = generate_explanation_news(df, selected_country, selected_category, date_period)
            else:
                df = filtered_discussions_df.copy()
                files = get_files_for_date(date,df)
                titles = get_titles_for_date(date,df).tolist()
                if len(files)>10:
                    random_indices = random.sample(range(len(files)), 10)
                    files = [files[i] for i in random_indices]
                    titles = [titles[i] for i in random_indices]
                if files:
                    explanation = generate_explanation(files, titles,selected_country, selected_category, date)
                else:
                    explanation = "No content available for this date."     


            outlier_explanations.append(explanation)
        discussion_trace = go.Scatter(x=discussions_per_week.index, y=discussions_per_week.values,
                                    mode='lines+markers', name='Discussions', line=dict(color='blue'))

        outlier_trace = go.Scatter(
            x=outlier_dates,
            y=outlier_values,
            mode='markers',
            marker=dict(color='red', symbol='line-ns-open', size=20),
            name='Outliers',
            text=outlier_explanations,
            hoverinfo='text'
        )
        if not filtered_news_df.empty:
            articles_per_week = filtered_news_df.resample(freq, on='date').size()

            # Apply smoothing and normalization
            smoothed_discussions_per_week = smooth_series(discussions_per_week, window_size=3)
            smoothed_articles_per_week = smooth_series(articles_per_week, window_size=3)

            # Normalize series for correlation calculation
            normalized_discussions = normalize_series(smoothed_discussions_per_week)
            normalized_articles = normalize_series(smoothed_articles_per_week)

            if len(normalized_discussions) > 1 and len(normalized_articles) > 1:
                common_index = normalized_discussions.index.intersection(normalized_articles.index)
                discussions_common = normalized_discussions[common_index]
                articles_common = normalized_articles[common_index]
                max_lag = 5  # Define the maximum number of lags to consider
                correlations = calculate_lagged_correlation(discussions_common, articles_common, max_lag)
                best_lag = max(correlations, key=correlations.get)
                best_correlation = correlations[best_lag]
            else:
                best_correlation = 'N/A'
                best_lag = 'N/A'

            correlation_text = f'Pearson Correlation (best lag {best_lag}): {best_correlation:.2f}'

            discussion_trace = go.Scatter(x=discussions_per_week.index, y=discussions_per_week.values,
                                        mode='lines+markers', name='Discussions', line=dict(color='blue'))

            articles_trace = go.Scatter(x=articles_per_week.index, y=articles_per_week.values,
                                        mode='lines+markers', name='News Articles', line=dict(color='red'), yaxis='y2')

            layout = go.Layout(title=f'Discussions from {actual_start_date.strftime("%B %Y")} to {actual_end_date.strftime("%B %Y")} ({country_names[selected_country]}, {selected_category})',
                            xaxis_title='Date', yaxis=dict(title='Discussions Count'),
                            yaxis2=dict(title='News Articles Count', overlaying='y', side='right'),
                            legend=dict(x=0, y=1, traceorder="normal"),
                            annotations=[dict(
                                xref='paper',
                                yref='paper',
                                x=0.95,
                                y=-0.2,
                                text=correlation_text,
                                showarrow=False
                            )])

            fig = go.Figure(data=[discussion_trace, outlier_trace, articles_trace], layout=layout)
        else:
            layout = go.Layout(title=f'Discussions from {actual_start_date.strftime("%B %Y")} to {actual_end_date.strftime("%B %Y")} ({country_names[selected_country]}, {selected_category})',
                            xaxis_title='Date', yaxis=dict(title='Discussions Count'),
                            legend=dict(x=0, y=1, traceorder="normal"),
                            annotations=[dict(
                                xref='paper',
                                yref='paper',
                                x=0.95,
                                y=-0.2,
                                text='Pearson Correlation: N/A',
                                showarrow=False
                            )])

            fig = go.Figure(data=[discussion_trace, outlier_trace], layout=layout)
        return fig
    return app

