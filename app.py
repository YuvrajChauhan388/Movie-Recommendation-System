import pickle
import requests
import streamlit as st
import gzip
from huggingface_hub import hf_hub_download

# Define repo details
REPO_ID = "YuvrajChauhan3888/movie-recommender-data"

# Download files from HF Hub
@st.cache_resource
def load_data():
    # download movie_list.pkl
    movie_list_path = hf_hub_download(repo_id=REPO_ID, filename="movie_list.pkl")
    with open(movie_list_path, "rb") as f:
        movies = pickle.load(f)

    # download compressed similarity.pkl.gz
    similarity_path = hf_hub_download(repo_id=REPO_ID, filename="similarity_compressed.pkl.gz")
    with gzip.open(similarity_path, "rb") as f:
        similarity = pickle.load(f)

    return movies, similarity

movies, similarity = load_data()

# CSS
def load_css():
    try:
        with open("style.css", "r") as f:
            css = f.read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css()

# Helper functions
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=3311b8aedeb68f05554d54a201c6ce0c&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get("poster_path", "")
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

# UI
st.markdown('<div class="main-header">🎬 Movie Recommender</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Discover your next favorite film!</div>', unsafe_allow_html=True)

movie_list = movies['title'].values
selected_movie = st.selectbox("Type or choose a movie you like", movie_list)

if st.button("Show Recommendations"):
    names, posters = recommend(selected_movie)
    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            safe_title = names[i].replace("<", "&lt;").replace(">", "&gt;")
            st.markdown(f"<div class='movie-title'>{safe_title}</div>", unsafe_allow_html=True)
            st.image(posters[i], use_container_width=True)
