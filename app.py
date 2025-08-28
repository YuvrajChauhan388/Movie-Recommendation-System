import pickle
import requests
import streamlit as st
import os
import gdown

# Google Drive File IDs
MOVIE_LIST_ID = "17-lf9cKAUjcazaIUBS3ByUZq-qGmoDid"
SIMILARITY_ID = "1MIcCeKBaNJFujd4gOrCHs8_DssIlYLgE"

MOVIE_LIST_FILE = "movie_list.pkl"
SIMILARITY_FILE = "similarity.pkl"

# Function to download files from Google Drive
def download_file_google_drive(file_id, destination):
    if not os.path.exists(destination):
        url = f"https://drive.google.com/uc?id={file_id}&export=download"
        with st.spinner(f"Downloading {destination} ..."):
            gdown.download(url, destination, quiet=False)
        st.success(f"Downloaded {destination}")

# Download pickle files
download_file_google_drive(MOVIE_LIST_ID, MOVIE_LIST_FILE)
download_file_google_drive(SIMILARITY_ID, SIMILARITY_FILE)

# Load pickle files safely
try:
    with open(MOVIE_LIST_FILE, 'rb') as f:
        movies = pickle.load(f)
    with open(SIMILARITY_FILE, 'rb') as f:
        similarity = pickle.load(f)
except Exception as e:
    st.error(f"Failed to load pickle files: {e}")
    st.stop()

# Helper: fetch movie poster
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=3311b8aedeb68f05554a201c6ce0c&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path', '')
    return "https://image.tmdb.org/t/p/w500/" + poster_path if poster_path else ""

# Helper: recommend movies
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
    return recommended_movie_names, recommended_movie_posters

# Streamlit UI
st.markdown('<h1 style="text-align:center; color:#2A5C99;">🎬 Movie Recommender</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; font-size:1.1rem;">Discover your next favorite film! Select a movie and get 5 recommendations.</p>', unsafe_allow_html=True)

movie_list = movies['title'].values
selected_movie = st.selectbox("Type or select a movie you like", movie_list)

if st.button('Show Recommendations'):
    names, posters = recommend(selected_movie)
    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            safe_title = names[i].replace("<", "&lt;").replace(">", "&gt;")
            st.markdown(f"<div style='text-align:center; font-weight:600;'>{safe_title}</div>", unsafe_allow_html=True)
            st.image(posters[i], use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#4B8DF8;'>Try another movie for fresh recommendations 🍿</p>", unsafe_allow_html=True)
