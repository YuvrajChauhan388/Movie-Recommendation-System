import pickle
import requests
import streamlit as st
import os
import gdown

MOVIE_LIST_ID = "17-lf9cKAUjcazaIUBS3ByUZq-qGmoDid"
SIMILARITY_ID = "1MIcCeKBaNJFujd4gOrCHs8_DssIlYLgE"

MOVIE_LIST_FILE = "movie_list.pkl"
SIMILARITY_FILE = "similarity.pkl"

def download_file_google_drive(file_id, destination):
    if not os.path.exists(destination):
        url = f"https://drive.google.com/uc?id={file_id}&export=download"
        gdown.download(url, destination, quiet=False, fuzzy=True)

@st.cache_resource
def load_pickles():
    download_file_google_drive(MOVIE_LIST_ID, MOVIE_LIST_FILE)
    download_file_google_drive(SIMILARITY_ID, SIMILARITY_FILE)

    with open(MOVIE_LIST_FILE, "rb") as f:
        movies = pickle.load(f)
    with open(SIMILARITY_FILE, "rb") as f:
        similarity = pickle.load(f)
    return movies, similarity

try:
    movies, similarity = load_pickles()
except Exception as e:
    st.error(f"❌ Failed to load pickle files: {e}")
    st.stop()

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=3311b8aedeb68f05554a201c6ce0c&language=en-US"
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
    names, posters = [], []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        names.append(movies.iloc[i[0]].title)
        posters.append(fetch_poster(movie_id))
    return names, posters

st.title("🎬 Movie Recommender System")

movie_list = movies["title"].values
selected_movie = st.selectbox("Select a movie you like", movie_list)

if st.button("Show Recommendations"):
    names, posters = recommend(selected_movie)
    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            st.text(names[i])
            st.image(posters[i], use_container_width=True)
