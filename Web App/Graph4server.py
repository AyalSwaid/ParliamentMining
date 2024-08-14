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
from nltk.sentiment import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')
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
# from googletrans import Translator
from translate import Translator
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F

full_df = pd.read_csv(r"C:\Users\user\Desktop\v22.csv")
full_df['Category'] = full_df['Category'].apply(json.loads)
full_df['date'] = pd.to_datetime(full_df['date'], format='%Y-%m-%d', errors='coerce')
# full_df['Category'] = full_df['Category'].apply(lambda x: [category.strip() for category in x[0].split(',')])

country_names = {1: 'United States', 2: "United Kingdom", 3: "Israel", 4: "Canada", 5: 'Tunisia'}
wanted_categories = ['Economy', 'Education', 'Environment', 'Foreign Policy', 'Healthcare', 'Judicial System', 'Military', 'Social Issues', 'Other']
df4 = full_df.copy()
sia = SentimentIntensityAnalyzer()

from bidi.algorithm import get_display
import arabic_reshaper
import spacy
from spacy.lang.en.stop_words import STOP_WORDS as en_stop
from spacy.lang.he.stop_words import STOP_WORDS as he_stop
from spacy.lang.ar.stop_words import STOP_WORDS as ar_stop


def clean_text(text):
    text = re.sub(r'Mr\.|Mrs\.|Ms\.|Dr\.|Hon\.|Rep\.|Sen\.|Speaker|President|Member|Committee|Senate|House|States|America|Congress|Introduced|bill|committee|ways|means', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\(.*?\)', '', text)  # Remove text within parentheses
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra whitespace
    return text
# For English, we can use the same `spacy` model if already loaded
nlp_en = spacy.load('en_core_web_sm')
real_data = full_df.copy()

parliamentary_stop_words_eng = [
    "Mr", "Madam", "Speaker", "President", "Member", "Members", "Honourable", 
    "Minister", "Government", "Opposition", "House", "Parliament", "Chair", 
    "Committee", "Debate", "Motion", "Bill", "Clause", "Question", "Answer", 
    "Vote", "Session", "Meeting", "Point", "Order", "Chairperson", "Colleague", 
    "Colleagues", "Gentleman", "Gentlemen", "Lady", "Ladies", "Sir", "Ma'am", 
    "Secretary", "Cabinet", "Prime", "Deputy", "Leader", "Chief", "Office", 
    "Official", "Policy", "Agenda", "Vote", "Yes", "No", "Abstain",
    "Mr", "Madam", "Speaker", "President", "Member", "Members", "Honourable", 
    "Minister", "Government", "Opposition", "House", "Parliament", "Chair", 
    "Committee", "Debate", "Motion", "Bill", "Clause", "Question", "Answer", 
    "Vote", "Session", "Meeting", "Point", "Order", "Chairperson", "Colleague", 
    "Colleagues", "Gentleman", "Gentlemen", "Lady", "Ladies", "Sir", "Ma'am", 
    "Secretary", "Cabinet", "Prime", "Deputy", "Leader", "Chief", "Office", 
    "Official", "Policy", "Agenda", "Vote", "Yes", "No", "Abstain", "Rt", 
    "Hon", "Lord", "Baroness", "Duke", "Duchess", "Viscount", "Viscountess", 
    "Earl", "Countess", "Marquess", "Marquessate", "Dame", "Majesty", "Prince", 
    "Princess", "Duke", "Duchess", "Archbishop", "Bishop", "Canon", "Reverend", 
    "Chaplain", "Clerk", "Treasurer", "Comptroller", "Usher", "Beadle", "Serjeant", 
    "Clerk", "Principal", "Registrar", "Provost", "Dean", "Bailiff", "Master", 
    "Commissioner", "Councillor", "Alderman", "Sheriff", "Recorder", "Mayor", 
    "Governor", "Agent", "Solicitor", "Advocate", "Prosecutor", "Defendant", 
    "Plaintiff", "Magistrate", "Constable", "Coroner", "Officer", "Inspector", 
    "Detective", "Sergeant", "Corporal", "Lieutenant", "Captain", "Major", 
    "Colonel", "Brigadier", "General", "Admiral", "Marshal", "Warrant", 'lord, gentelman', 'friend', 'gentelmen', 'canada', 'canadian'
    , 'minister', 'government', 'noble'
]

hebrew_stop_words = [
    "ה", "של", "על", "עם", "ש", "כ", "הם", "אני", "אנחנו", "אתה", "את", "אתם",
    "אתן", "הוא", "היא", "הם", "הן", "זה", "זאת", "אלה", "אלו", "מה", "מי", 
    "לא", "כן", "אם", "או", "כל", "כמו", "כי", "אשר", "אף", "אבל", "עוד", 
    "למה", "איך", "היכן", "כאן", "שם", "איפה", "מתי", "כמה", "איזה", "ליד", 
    "מול", "אחרי", "לפני", "בין", "תחת", "מאחורי", "האם", "כדי", "למרות", 
    "מאוד", "יותר", "פחות", "גם", "רק", "שוב", "כמעט", "בדרך כלל", "לעתים קרובות", 
    "לפעמים", "אף פעם", "תמיד", "פעמים רבות", "מעטים", "רבים", "במידה", "יכול", 
    "יוכל", "מוצע", "ממליץ", "מומלץ", "פרופ'", 'ח"כ', "חברי הכנסת", "מזכיר", 
    "מזכירה", "ממשלה", "אופוזיציה", "יושב ראש", "הצעה", "חוק", "סעיף", "שאלה", 
    "תשובה", "הצבעה", "ישיבה", "ישיבות", "נקודה", "סדר", "חבר", "חברים", "גברת", 
    "גבירותיי", "אדון", "אדונים", "שר", "שרים", "מזכירים", "הנשיא", "ראש הממשלה", 
    'מנכ"ל', "יועץ", "מדיניות", "תכנית", "סדר יום", "כן", "לא", "נמנע", 'הכנסת', 'בוועדה',
    'בוועדת', 'חברי הכנסת', 'הזה' ,'ואני', 'נוכח', 'נוכחת', 'חברת', 'שזה', 'שהוא', 'שלא', 'אינו', 'אינה',
    'הממשלה', 'שאנחנו', 'כבר', 'היום', 'הזאת', 'לך', 'חברי','ולא', 'הייתה', 'בממשלה', 'השר','אבל', 'אחר', 'אחרת', 'אם', 'אנחנו', 'אני', 'את', 'אתה', 
    'באמצע', 'בגלל', 'בין', 'בלי', 'גם', 'דרך', 'היא', 'היה', 
    'היתה', 'הם', 'הן', 'ועוד', 'זאת', 'זה', 'זות', 'יותר', 
    'יש', 'כמו', 'כן', 'לא', 'למה', 'לפני', 'מאוד', 'מה', 
    'מי', 'מכל', 'מכיוון', 'מלא', 'ממש', 'מעט', 'עד', 'על', 
    'עם', 'פה', 'רק', 'שוב', 'תחת', 'אף', 'הכל', 'אף-על-פי', 
    'אף-על-פי-כן', 'אל', 'אולי', 'אז', 'אחת', 'אותה', 'אותו', 
    'אותן', 'אותם', 'אותי', 'אותך', 'אותנו', 'אשר', 'ב', 
    'בא', 'באיזה', 'באיזו', 'באיזו', 'באמת', 'בערך', 'ברור', 
    'בדיוק', 'בזמן', 'בלבד', 'בכלל', 'בכלליות', 'בלי', 'בעבר', 
    'בעצם', 'בפני', 'בקשר', 'ברם', 'בשום', 'גם-כן', 'זאת-אומרת', 
    'יותר-מידי', 'יותר-מדי', 'כיצד', 'כאשר', 'כאן', 'כבר', 
    'ל', 'לאחר', 'לבינתיים', 'לגמרי', 'להיות', 'לו', 'לומר', 
    'למה', 'למעט', 'לעולם', 'לפיכך', 'מאחורי', 'מאחר', 'מדי', 
    'מישהו', 'משום', 'מתחת', 'נא', 'נגד', 'עדיין', 'עוד', 
    'אכן', 'עכשיו', 'עם-זאת', 'עצמה', 'עצמם', 'עצמו', 'עצמי', 
    'פחות', 'פה', 'צד', 'קודם', 'רוב', 'שוב', 'שום', 'שלה', 
    'שלו', 'שלי', 'שלנו', 'תחת', 'אותו', 'אותה', 'אותם', 
    'אותן', 'אותך', 'אותי', 'אתכם', 'אתכן', 'איתו', 'איתך', 
    'איתי', 'איתה', 'איתם', 'איתן', 'כלשהו', 'כלשהי', 'כולם', 
    'כולן', 'כולו', 'כולה', 'כמובן', 'כפי', 'כאילו', 'כן', 
    'כאן', 'כזה', 'כמו', 'כפי', 'כי', 'לכן', 'לעתים', 'מאוד', 
    'מאחר', 'מכל', 'מלבד', 'מן', 'מני', 'ממנו', 'ממנה', 'ממך', 
    'ממני', 'מס', 'נגד', 'נו', 'נאמר', 'נא', 'נראה', 'סוף', 
    'עוד', 'עבור', 'עמו', 'עצמם', 'עצמן', 'עצמו', 'עצמה', 
    'פה', 'במקום', 'בעצם', 'באמת', 'באופן', 'בלי', 'ברור', 
    'בסופו', 'בתוך', 'בדרך', 'במקום', 'בחוץ', 'בתוך', 'יותר', 
    'יחד', 'לבד', 'לבין', 'לגמרי', 'לכן', 'לפיכך', 'מאז', 
    'מאחורי', 'מאיתנו', 'מאיתכם', 'מאיתכן', 'מאותו', 'מאותה', 
    'מאותם', 'מאותן', 'מאחר', 'מאז', 'מדוע', 'מה', 'מהם', 
    'מהן', 'מהי', 'מהו', 'מהן', 'מאיזה', 'מזה', 'מי', 'מי', 
    'מכם', 'מכן', 'מזה', 'מתי', 'מתחת', 'נראה', 'נאמר', 
    'כאן', 'כי', 'כל', 'כלל', 'כלשהו', 'כלשהי', 'כמובן', 
    'כמו', 'כן', 'לא', 'לבד', 'לגמרי', 'לה', 'לו', 'לי', 
    'למה', 'לנו', 'לעולם', 'לפני', 'מאוד', 'מאחר', 'מדה', 
    'מה', 'מהם', 'מהן', 'מי', 'מיליון', 'מכל', 'מלבד', 'מן', 
    'מנין', 'מעט', 'מקום', 'מתוך', 'נגד', 'נראה', 'נא', 
    'נעשה', 'סוף', 'סופי', 'סופית', 'על', 'עליה', 'עליהם', 
    'עליהן', 'עליו', 'עליה', 'עלי', 'עליהם', 'עליהן', 'עצמם', 
    'עצמו', 'עצמה', 'עצמם', 'פה', 'פי', 'צד', 'קודם', 'רק', 
    'שוב', 'שום', 'של', 'שלה', 'שלו', 'שלהם', 'שלהן', 'שלי', 
    'שלנו', 'שלהם', 'שלהן', 'שאם', 'שבו', 'שלה', 'שלו', 'שלי', 
    'שלנו', 'שם', 'שוב', 'שובו', 'תחת', 'תוך',"תודה" ,"שאני", "רבה",
    "התשפ","תשפ", "ט", "ג", "אומר", "אדוני היושה", "היושב", "ראש", "היושב ראש", 
    "בבקשה", "רוצה", "להגיד", "אפשר","שאתה","ואנחנו", "אדוני" ,"זה" ,"צריך", "לעשות", "גם", "אפילו", "אחד", "וגם"
]

stop_words_english = set(nltk.corpus.stopwords.words('english')) | set(parliamentary_stop_words_eng) | set(en_stop)
stop_words_hebrew = set(nltk.corpus.stopwords.words('hebrew')) | set(hebrew_stop_words) | set(he_stop) 
stop_words_arabic = set(nltk.corpus.stopwords.words('arabic')) | set(ar_stop)
real_data['date'] = pd.to_datetime(real_data['date'])


# Load heBERT model and tokenizer
hebrew_tokenizer = AutoTokenizer.from_pretrained("avichr/heBERT_sentiment_analysis")
hebrew_model = AutoModelForSequenceClassification.from_pretrained("avichr/heBERT_sentiment_analysis")

def translate_text(text, src_lang):
    translator = Translator(from_lang=src_lang, to_lang="en")
    try:
        translated_text = translator.translate(text)
        return translated_text
    except Exception as e:
        print(f"Error: {str(e)}")
        return f'Error: {str(e)}'

def sentiment_analysis(partial_path,country = 1):
    d = r'C:\Users\user\Desktop'
    path = os.path.join(d, partial_path)
    sent_dict = {}
    with open(path, 'r') as json_file:
        alltext = json.load(json_file)
    for i in alltext:
        member = i['name'].lower()  # Accessing the name directly
        if len(member) >70:
            continue
        text = i['speech']  # Accessing the speech text directly
        if len(text) > 10000:
            text = text[:10000]
        if country == 5:
            if len(text) > 250:
                text1 = text[:250]
            text = translate_text(text1,'ar')
        sentiment_scores = sia.polarity_scores(text)['compound']
        if member not in sent_dict.keys():
            sent_dict[member] = [float(sentiment_scores), 1]
        else:
            sent_dict[member][0] += float(sentiment_scores)
            sent_dict[member][1] += 1

    for i, j in sent_dict.items():
        sent_dict[i][0] /= sent_dict[i][1]
        sent_dict[i] = round(sent_dict[i][0], 3)
    return sent_dict

def sentiment_score_he(texts):
    # Tokenize the input texts
    inputs = hebrew_tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=256)
    
    # Get the model output
    with torch.no_grad():
        outputs = hebrew_model(**inputs)
    logits = outputs.logits
    
    # Apply softmax to get probabilities
    probs = F.softmax(logits, dim=1)
    
    # Extract positive, neutral, and negative probabilities
    negative_probs = probs[:, 0].tolist()
    positive_probs = probs[:, 2].tolist()
    
    # Calculate the sentiment scores
    sentiments = [pos - neg for pos, neg in zip(positive_probs, negative_probs)]
    
    return sentiments

def sentiment_analysis_hebrew(partial_path):
    d = r'C:\Users\user\Desktop'
    path = os.path.join(d, partial_path)
    sent_dict = {}
    
    with open(path, 'r', encoding='utf-8') as json_file:
        alltext = json.load(json_file)

    # Preprocess texts and members
    texts, members = [], []
    for i in alltext:
        member = i['name'].lower()
        if len(member) > 70:
            continue
        text = i['speech']
        if len(text) > 700:
            text = text[200:700]
        texts.append(text)
        members.append(member)

    # Batch processing
    batch_size = 16
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        batch_members = members[i:i+batch_size]
        sentiment_scores = sentiment_score_he(batch_texts)
        
        for member, sentiment_score in zip(batch_members, sentiment_scores):
            if member not in sent_dict:
                sent_dict[member] = [sentiment_score, 1]
            else:
                sent_dict[member][0] += sentiment_score
                sent_dict[member][1] += 1

    for member, scores in sent_dict.items():
        sent_dict[member][0] /= scores[1]
        sent_dict[member] = round(sent_dict[member][0], 3)
    
    return sent_dict

def sentiment_color(sentiment):
    if sentiment < -0.25:
        return 'red'
    elif sentiment > 0.25:
        return 'green'
    else:
        return 'yellow'

def truncate_title(title, max_length=90):
    try:
        if isinstance(title, str) and len(title) >= max_length:
            return title[:max_length] + '...'
        return title.lower()
    except Exception as e:
        return "Error truncating title"
    
def clean_name(name):
    # Remove titles and other specific words
    name = re.sub(r'Mr\.|Ms\.|Mrs\.|Dr\.|Hon\.|Sir|mr\.|ms\.|mrs\.|dr\.|hon\.|sir|היו"ר|יו"ר|מזכירת|הכנסת|מזכיר', '', name)
    # Remove parentheses and their contents
    name = re.sub(r'\(.*?\)', '', name)
    # Remove trailing colons and any surrounding whitespace
    name = re.sub(r':\s*$', '', name).strip()
    return name

def match_name(name, names_list):
    cleaned_name = clean_name(name)
    pattern = re.compile(r'\b{}\b'.format(re.escape(cleaned_name.lower().strip())))
    matches = [pattern.search(clean_name(n).lower().strip()) for n in names_list]
    matched_names = [names_list[i] for i in range(len(matches)) if matches[i] is not None]
    return matched_names if matched_names else None

df4['truncated_title'] = df4['debate_title'].apply(truncate_title)

CA_par = pd.read_csv(r'C:\Users\user\Desktop\Data\csv_files\members\CA_members.csv')
IL_par = pd.read_csv(r'C:\Users\user\Desktop\Data\csv_files\members\IL_members.csv')
TN_par = pd.read_csv(r'C:\Users\user\Desktop\Data\csv_files\members\TN_members.csv')
UK_par = pd.read_csv(r'C:\Users\user\Desktop\Data\csv_files\members\UK_members.csv')
US_par = pd.read_csv(r'C:\Users\user\Desktop\Data\csv_files\members\US_members.csv')

def create_dash_app4(flask_app):
    app = dash.Dash(server=flask_app, name = 'SentimentAnalysisWordCloud', url_base_pathname="/SentimentAnalysisWordCloud/")
    app.layout = html.Div([
        html.H1('Sentiment Analysis & Wordcloud Graph', style={'textAlign': 'center'}),
        html.Div([
            html.Label('Country:'),
            dcc.Dropdown(
                id='country-dropdown2',
                options=[{'label': country_names[country], 'value': country} for country in real_data['country'].unique()],
                value=real_data['country'].unique()[0],
                style={'width': '45%', 'display': 'inline-block'}
            ),
            html.Label('Category:'),
            dcc.Dropdown(
                id='category-dropdown2',
                options=[{'label': category, 'value': category} for category in wanted_categories],
                value=wanted_categories[0],
                style={'width': '45%', 'display': 'inline-block'}
            ),
            html.Label('Discussion Title:'),
            dcc.Dropdown(
                id='debate-dropdown2',
                style={'width': '45%', 'display': 'inline-block'}
            ),
        ]),
        html.Div(id='discussion-info4', style={'textAlign': 'center', 'margin': '20px 0', 'fontSize': '24px', 'fontWeight': 'bold'}),
        html.Div([
            dcc.Graph(id='sentiment-graph', style={'width': '65%', 'height': '450px', 'display': 'inline-block'}),
            html.Div(id='wordcloud-container', style={'width': '35%', 'height': '450px', 'display': 'inline-block'})
        ], style={'display': 'flex', 'alignItems': 'stretch', 'justifyContent': 'space-between'}),
        html.Div(["This graph is made up of two graphs, Sentiment Analysis and WordCloud.",html.Br(),"The wordcloud graph visually represents the most frequently used words in the selected discussion.", html.Br(),
                "The size of each word indicates its frequency in the debate. Common parliamentary stopwords have been removed to highlight the key terms discussed.",html.Br(),
                "The Sentiment Analysis Graph illustrates the sentiment of parliamentarians regarding the chosen discussion.",html.Br(),
                "The x-axis represents the sentiment score, ranging from negative to positive sentiments.",html.Br(),
                "The y-axis represents the political parties, and each point represents an individual parliamentarian's sentiment.",html.Br(),
                "The average sentiment for each party is also displayed."], 
                style={'textAlign': 'left', 'margin': '20px 0', 'fontSize': '16px'})
    ])

    @app.callback(
        [Output('debate-dropdown2', 'options'),
        Output('debate-dropdown2', 'value')],
        [Input('country-dropdown2', 'value'),
        Input('category-dropdown2', 'value')]
    )
    def update_discussion_options(selected_country, selected_category):
        filtered_df = real_data[real_data['country'] == selected_country]
        if selected_category:
            filtered_df = filtered_df[filtered_df['Category'].apply(lambda x: selected_category in x)]
        
        discussion_options = [{'label': discussion, 'value': discussion} for discussion in filtered_df['debate_title'].unique()]
        if discussion_options:
            selected_discussion = discussion_options[0]['value']
            return discussion_options, selected_discussion
        else:
            return [], None


    @app.callback(
        Output('sentiment-graph', 'figure'),
        Output('discussion-info4', 'children'),
        [Input('country-dropdown2', 'value'),
        Input('category-dropdown2', 'value'),
        Input('debate-dropdown2', 'value')]
    )
    def update_graph(selected_countries, selected_categories, selected_discussions):
        filtered_df = df4[
            (df4['country'] == selected_countries) &
            (df4['Category'].apply(lambda x: selected_categories in x)) &
            (df4['debate_title'].isin([selected_discussions]))
        ]
        
        discussion_date = filtered_df['date'].iloc[0].strftime('%d-%m-%Y')
        discussion_info = f"Country: {country_names[selected_countries]}, Category: {selected_categories}, Date: {discussion_date}"
        
        path = filtered_df['file_path'].tolist()
        sent_dict = {}
        if selected_countries == 4:
            sent_dict = sentiment_analysis(path[0])
            parties_df = CA_par
        elif selected_countries == 3:
            sent_dict = sentiment_analysis_hebrew(path[0])
            parties_df = IL_par
        elif selected_countries == 2:
            sent_dict = sentiment_analysis(path[0])
            parties_df = UK_par
            parties_df['name'] = parties_df['name'].apply(clean_name)
        elif selected_countries == 1:
            sent_dict = sentiment_analysis(path[0])
            parties_df = US_par
        elif selected_countries == 5:
            sent_dict = sentiment_analysis(path[0], 5)
            parties_df = TN_par

        parties_df['startDate'] = pd.to_datetime(parties_df['startDate'])
        parties_df['endDate'] = pd.to_datetime(parties_df['endDate'])

        filtered_parties_df = parties_df[
            (parties_df['startDate'] <= discussion_date) &
            (parties_df['endDate'].isna() | (parties_df['endDate'] >= discussion_date))
        ]

        final_data = []
        reverse_lookup = {clean_name(key): key for key in sent_dict.keys()}
        
        for original_name, sentiment in sent_dict.items():
            cleaned_name = clean_name(original_name)
            if cleaned_name in reverse_lookup:
                matched_names = match_name(cleaned_name, filtered_parties_df['name'].tolist())
                if matched_names:
                    for matched_name in matched_names:
                        matched_row = filtered_parties_df[filtered_parties_df['name'] == matched_name]
                        original_matched_name = matched_row['name'].values[0]
                        party = matched_row['party'].values[0]
                        final_data.append((original_matched_name, sentiment, party))
                        break

        if final_data:
            merged_df = pd.DataFrame(final_data, columns=['matched_name', 'sentiment', 'party'])
        else:
            merged_df = pd.DataFrame([
            {'matched_name': name, 'sentiment': sent_dict.get(name, 0), 'party': 'No Party'} 
            for name in sent_dict.keys()
        ])
        
        if 'No Party' in merged_df['party'].unique() and not merged_df['party'].isnull().all():
            unique_parties = merged_df['party'].unique()
            party_to_y = {party: i for i, party in enumerate(unique_parties)}
            party_to_y['No Party'] = 0
        else:
            unique_parties = merged_df['party'].unique()
            party_to_y = {party: i for i, party in enumerate(unique_parties)}

        merged_df['color'] = merged_df['sentiment'].apply(sentiment_color)
        merged_df['y_position'] = merged_df['party'].map(party_to_y)
        
        avg_sentiments = merged_df.groupby('party')['sentiment'].mean().reset_index()
        avg_sentiments['sentiment'] = avg_sentiments['sentiment'].round(3)
        avg_sentiments['y_position'] = avg_sentiments['party'].map(party_to_y)
        avg_sentiments['color'] = avg_sentiments['sentiment'].apply(sentiment_color)
        
        fig = {
            'data': [
                go.Scatter(
                    x=merged_df['sentiment'],
                    y=merged_df['y_position'],
                    text=[f'{row["matched_name"]} (Party: {row["party"]}, Sentiment: {row["sentiment"]})' for _, row in merged_df.iterrows()],
                    mode='markers',
                    marker={'size': 15, 'color': merged_df['color']},
                    name = "Parliament Member"
                ),
                go.Scatter(
                x=avg_sentiments['sentiment'],
                y=avg_sentiments['y_position'],
                text=[f'The {row["party"]} Party Average Sentiment (Party: {row["party"]}, Sentiment: {row["sentiment"]})' for _, row in avg_sentiments.iterrows()],
                mode='markers',
                marker={'size': 20, 'color': avg_sentiments['color'], 'symbol': 'circle', 'opacity': 0.5},
                name='Average Sentiment'
            )
            ],
            'layout': go.Layout(
                title='MPs Sentiment by Party',
                xaxis={'title': 'Sentiment Score'},
                yaxis={'title': 'Party', 'tickvals': list(range(len(unique_parties))), 'ticktext': list(unique_parties)},
                hovermode='closest'
            )
        }
        return fig, discussion_info


    @app.callback(
        Output('wordcloud-container', 'children'),
        [Input('debate-dropdown2', 'value'),
        Input('country-dropdown2', 'value'),
        Input('category-dropdown2', 'value')]
    )
    def update_wordcloud(selected_debate, selected_country, selected_category):
        if selected_debate is None:
            return html.Div(), ""  # Return empty div and empty info if no debate is selected

        filtered_df = real_data[(real_data['debate_title'] == selected_debate) & 
                                (real_data['country'] == selected_country) & 
                                (real_data['Category'].apply(lambda x: selected_category in x))]
        discussion_date = filtered_df['date'].iloc[0].strftime('%Y-%m-%d')  # Format the date to show only the date part
        
        partial_path = filtered_df['file_path'].iloc[0]
        font = r"C:\Users\user\Desktop\OpenSans-Medium.ttf"
        arabic_flag, IL_flag = False, False
        initial_path = r'C:\Users\user\Desktop'
        if selected_country == 3:
            IL_flag = True

        elif selected_country == 5:
            arabic_flag = True
            font = r'C:\Users\user\Desktop\Cairo-VariableFont_slnt,wght.ttf'

        path = os.path.join(initial_path, partial_path)
        with open(path, 'r', encoding='utf-8') as json_file:
            alltext = json.load(json_file)

        full_text = ''
        for i in alltext:
            if len(full_text + i['speech']) < 50000:
                full_text += i['speech']
            else:
                rem = 50000 - len(full_text)
                full_text += i['speech'][:rem]

        cleaned_text = clean_text(full_text)
        if selected_country == 5:
            stop_words = stop_words_arabic
            tokens = [word for word in re.findall(r'\b\w+\b', cleaned_text) if word.lower() not in stop_words]
            preprocessed_text = ' '.join(tokens)
            preprocessed_text = arabic_reshaper.reshape(preprocessed_text)
            preprocessed_text = get_display(preprocessed_text)
        elif selected_country == 3:
            stop_words = stop_words_hebrew
            tokens = [word for word in re.findall(r'\b\w+\b', cleaned_text) if word.lower() not in stop_words]
            preprocessed_text = ' '.join(tokens)
            preprocessed_text = get_display(preprocessed_text)
        else:
            doc = nlp_en(cleaned_text)
            interesting_labels = ["PERSON", "ORG", "GPE", "LAW", "EVENT", "WORK_OF_ART", "DATE", "MONEY", "PRODUCT", "LOC", "FAC", "NORP", "PERCENT", "QUANTITY", "ORDINAL", "CARDINAL"]
            tokens = [ent.text for ent in doc.ents if ent.label_ in interesting_labels]
            tokens += [token.lemma_ for token in doc if token.pos_ in interesting_labels and token.lemma_.lower() not in stop_words_english]
            tokens_filtered_stopwords = [token for token in tokens if token.lower() not in stop_words_english]
            preprocessed_text = ' '.join(tokens_filtered_stopwords)

        if not preprocessed_text.strip():
            return html.Div("No meaningful words to display in the wordcloud.")

        wordcloud = WordCloud(width=400, height=415, background_color='white', font_path=font).generate(preprocessed_text)
        img_data = BytesIO()
        wordcloud.to_image().save(img_data, format='PNG')
        wordcloud_base64 = base64.b64encode(img_data.getvalue()).decode('utf-8')

        text_direction = 'rtl' if selected_country == 3 or selected_country == 5 else 'ltr'
        return html.Img(src='data:image/png;base64,{}'.format(wordcloud_base64), style={'width': '90%', 'height': 'auto', 'direction': text_direction, 'unicode-bidi': 'embed'})
    
    return app