import streamlit as st
import requests
import pickle
import os
import gdown

# Function to download file using gdown, handles Google Drive large file confirmation
def download_file_from_google_drive(drive_url, destination):
    if not os.path.exists(destination):
        st.spinner(f"Downloading {destination} ...")
        gdown.download(drive_url, destination, quiet=False)
        st.success(f"Downloaded {destination}")

# Load external CSS file
def load_css(css_file_path: str):
    with open(css_file_path, "r") as f:
        css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Your external CSS file path
CSS_FILE = "style.css"

# Google Drive direct URLs (use uc?export=download pattern)
MOVIE_LIST_URL = "https://drive.google.com/uc?export=download&id=1bGfGQj4Af1sUqnpfoTdRzfG7vzuVfSji"
SIMILARITY_URL = "https://drive.google.com/uc?export=download&id=13eR-sqqXGKsb8WwJ5sXJpFLX15h2D05i"

# Local file names to save
MOVIE_LIST_FILE = "movie_list.pkl"
SIMILARITY_FILE = "similarity.pkl"

# Download pickle files if missing
download_file_from_google_drive(MOVIE_LIST_URL, MOVIE_LIST_FILE)
download_file_from_google_drive(SIMILARITY_URL, SIMILARITY_FILE)

# Load CSS
load_css(CSS_FILE)

# Helper functions
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=3311b8aedeb68f05554d54a201c6ce0c&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path', '')
    return "https://image.tmdb.org/t/p/w500/" + poster_path if poster_path else ""

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

# Load pickle data
with open(MOVIE_LIST_FILE, 'rb') as f:
    movies = pickle.load(f)
with open(SIMILARITY_FILE, 'rb') as f:
    similarity = pickle.load(f)

# Streamlit UI
st.markdown('<div class="main-header">🎬 Movie Recommender</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Discover your next favorite film! Select a movie and get 5 beautiful recommendations.<br>(Hover to see long titles.)</div>',
    unsafe_allow_html=True
)

movie_list = movies['title'].values

selected_movie = st.selectbox(
    "Type or choose a movie you like",
    movie_list,
    key="movie_dropdown"
)

if st.button('Show Recommendations'):
    names, posters = recommend(selected_movie)
    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            safe_title = names[i].replace("<", "&lt;").replace(">", "&gt;")
            st.markdown(f"<div class='movie-title' title='{safe_title}'>{safe_title}</div>", unsafe_allow_html=True)
            st.image(posters[i], use_container_width=True)
    st.markdown(
        "<hr style='margin:2em 0 1em 0; border-top:1.5px solid #4970a399'>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='color:#3ddad7; font-size:1.09rem; font-weight:600; text-align:center; margin-top:0.8em;'>"
        "Don't see your favorite? Try another movie for a fresh set of recommendations!"
        "</div>",
        unsafe_allow_html=True
    )

st.markdown(
    "<div style='text-align: center; font-size: 0.98rem; color: #f0e3bb; padding-top:22px'>Made with love for movie fans everywhere 🍿</div>",
    unsafe_allow_html=True
)
