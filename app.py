import streamlit as st
import requests
import pickle
import os
import gdown

# File IDs extracted from your Google Drive links
MOVIE_LIST_ID = "1bGfGQj4Af1sUqnpfoTdRzfG7vzuVfSji"
SIMILARITY_ID = "13eR-sqqXGKsb8WwJ5sXJpFLX15h2D05i"

MOVIE_LIST_FILE = "movie_list.pkl"
SIMILARITY_FILE = "similarity.pkl"

def download_file_google_drive(file_id, destination):
    if not os.path.exists(destination):
        with st.spinner(f"Downloading {destination} ..."):
            gdown.download(f'https://drive.google.com/uc?id={file_id}', destination, quiet=False, fuzzy=True)
        st.success(f"Downloaded {destination}")

download_file_google_drive(MOVIE_LIST_ID, MOVIE_LIST_FILE)
download_file_google_drive(SIMILARITY_ID, SIMILARITY_FILE)

st.write(f"{MOVIE_LIST_FILE} size: {os.path.getsize(MOVIE_LIST_FILE)} bytes")
st.write(f"{SIMILARITY_FILE} size: {os.path.getsize(SIMILARITY_FILE)} bytes")

try:
    with open(MOVIE_LIST_FILE, 'rb') as f:
        movies = pickle.load(f)
    with open(SIMILARITY_FILE, 'rb') as f:
        similarity = pickle.load(f)
except Exception as e:
    st.error(f"Failed to load pickle files: {e}")
    st.stop()

def load_css(css_path):
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

CSS_FILE = "style.css"
load_css(CSS_FILE)

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=3311b8aedeb68f05554d54a201c6ce0c&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path', '')
    return "https://image.tmdb.org/t/p/w500/" + poster_path if poster_path else ""

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    rec_names = []
    rec_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        rec_names.append(movies.iloc[i[0]].title)
        rec_posters.append(fetch_poster(movie_id))
    return rec_names, rec_posters

st.markdown('<div class="main-header">🎬 Movie Recommender</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Discover your next favorite film! Select a movie and get 5 beautiful recommendations.<br>(Hover to see long titles.)</div>', unsafe_allow_html=True)

movie_list = movies['title'].values
selected_movie = st.selectbox("Type or choose a movie you like", movie_list)

if st.button('Show Recommendations'):
    names, posters = recommend(selected_movie)
    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            safe_title = names[i].replace("<", "&lt;").replace(">", "&gt;")
            st.markdown(f"<div class='movie-title' title='{safe_title}'>{safe_title}</div>", unsafe_allow_html=True)
            st.image(posters[i], use_container_width=True)
    st.markdown("<hr style='margin:2em 0 1em 0; border-top:1.5px solid #4970a399'>", unsafe_allow_html=True)
    st.markdown("<div style='color:#3ddad7; font-size:1.09rem; font-weight:600; text-align:center; margin-top:0.8em;'>Don't see your favorite? Try another movie for a fresh set of recommendations!</div>", unsafe_allow_html=True)

st.markdown("<div style='text-align: center; font-size: 0.98rem; color: #f0e3bb; padding-top:22px'>Made with love for movie fans everywhere 🍿</div>", unsafe_allow_html=True)
