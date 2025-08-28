import streamlit as st
import requests
import pickle
import os
import gdown

# Google Drive file IDs for your pickles
MOVIE_LIST_ID = "1bGfGQj4Af1sUqnpfoTdRzfG7vzuVfSji"
SIMILARITY_ID = "13eR-sqqXGKsb8WwJ5sXJpFLX15h2D05i"

MOVIE_LIST_FILE = "movie_list.pkl"
SIMILARITY_FILE = "similarity.pkl"

def download_file_google_drive(file_id, destination):
    if not os.path.exists(destination):
        with st.spinner(f"Downloading {destination} ..."):
            # Use fuzzy=True to handle confirmation tokens
            gdown.download(f"https://drive.google.com/uc?id={file_id}", destination, quiet=False, fuzzy=True)
        st.success(f"Downloaded {destination}")

# Download files if missing
download_file_google_drive(MOVIE_LIST_ID, MOVIE_LIST_FILE)
download_file_google_drive(SIMILARITY_ID, SIMILARITY_FILE)

# Confirm file sizes
st.write(f"{MOVIE_LIST_FILE} size: {os.path.getsize(MOVIE_LIST_FILE)} bytes")
st.write(f"{SIMILARITY_FILE} size: {os.path.getsize(SIMILARITY_FILE)} bytes")

# Load pickle files safely
try:
    with open(MOVIE_LIST_FILE, "rb") as f:
        movies = pickle.load(f)
    with open(SIMILARITY_FILE, "rb") as f:
        similarity = pickle.load(f)
except Exception as e:
    st.error(f"Error loading pickle files: {e}")
    st.stop()

# Load CSS if exists
def load_css(css_path="style.css"):
    if os.path.exists(css_path):
        with open(css_path) as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
load_css()

# Helper function to get movie poster from TMDB API
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=3311b8aedeb68f05554d54a201c6ce0c&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get("poster_path")
    if poster_path:
        return "https://image.tmdb.org/t/p/w500" + poster_path
    return ""

# Recommendation function
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_titles = []
    recommended_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_titles.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))
    return recommended_titles, recommended_posters

# Streamlit app UI
st.markdown('<h1 style="text-align:center">🎬 Movie Recommender</h1>', unsafe_allow_html=True)
st.markdown('<h4 style="text-align:center">Select a movie to get 5 personalized recommendations</h4>', unsafe_allow_html=True)

movie_list = movies['title'].values
selected_movie = st.selectbox("Choose a movie:", movie_list)

if st.button("Show Recommendations"):
    names, posters = recommend(selected_movie)
    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            st.image(posters[idx], width=140)
            st.caption(names[idx])

st.markdown("<div style='text-align:center; margin-top:20px; color:#777;'>Made with ❤️ for movie fans</div>", unsafe_allow_html=True)
