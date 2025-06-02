import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@st.cache_data
def load_data():
    df = pd.read_csv('megaGymDataset.csv')
    df['Desc'] = df['Desc'].fillna('No description available')
    df['Rating'] = df['Rating'].fillna(df['Rating'].mean())
    df['Equipment'] = df['Equipment'].fillna('No equipment specified')
    df['Title'] = df['Title'].fillna('Unknown Exercise')
    df['Type'] = df['Type'].fillna('Unknown Type')
    df['BodyPart'] = df['BodyPart'].fillna('Unknown BodyPart')
    df['Level'] = df['Level'].fillna('Unknown')
    df['combined_features'] = df['Title'] + ' ' + df['Type'] + ' ' + df['BodyPart'] + ' ' + df['Equipment'] + ' ' + df['Desc']
    df = df.drop_duplicates()
    return df

@st.cache_resource
def initialize_model(df):
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['combined_features'])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    return tfidf, tfidf_matrix, cosine_sim