import os
import pickle
import streamlit as st
import requests
from huggingface_hub import hf_hub_download

# Hugging Face repo details
REPO_ID = "YuvrajChauhan3888/movie-recommender-data"  # <-- your repo
REPO_TYPE = "dataset"

@st.cache_resource
def load_pickles():
    movie_path = hf_hub_download(repo_id=REPO_ID, repo_type=REPO_TYPE, filename="movie_list.pkl")
    sim_path = hf_hub_download(repo_id=REPO_ID, repo_type=REPO_TYPE, filename="similarity.pkl")
    
    with open(movie_path, "rb") as f:
        movies = pickle.load(f)
    with open(sim_path, "rb") as f:
        similarity = pickle.load(f)
    return movies, similarity

# Load pickles
movies, similarity = load_pickles()

# --- Poster fetch helper ---
TMDB_KEY = "3311b8aedeb68f05554a201c6ce0c"  # replace with your API key
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_KEY}&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get("poster_path", "")
    return "https://image.tmdb.org/t/p/w500/" + poster_path if poster_path else ""

# --- Recommend function ---
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    names, posters = [], []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        names.append(movies.iloc[i[0]].title)
        posters.append(fetch_poster(movie_id))
    return names, posters

# --- Streamlit UI ---
st.title("🎬 Movie Recommender")
movie_list = movies['title'].values
selected_movie = st.selectbox("Choose a movie", movie_list)
if st.button("Show Recommendations"):
    names, posters = recommend(selected_movie)
    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            st.markdown(f"**{names[i]}**")
            st.image(posters[i], use_container_width=True)
