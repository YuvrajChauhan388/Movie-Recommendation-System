import pickle
import requests
import streamlit as st
import os
import gdown

# File IDs from Google Drive
MOVIE_LIST_ID = "17-lf9cKAUjcazaIUBS3ByUZq-qGmoDid"
SIMILARITY_ID = "1MIcCeKBaNJFujd4gOrCHs8_DssIlYLgE"

MOVIE_LIST_FILE = "movie_list.pkl"
SIMILARITY_FILE = "similarity.pkl"


# ----------------- Helper: Download from Google Drive -----------------
def download_file_google_drive(file_id, destination):
    if not os.path.exists(destination):
        with st.spinner(f"Downloading {destination} ..."):
            url = f"https://drive.google.com/uc?export=download&id={file_id}"
            gdown.download(url, destination, quiet=False)
        if os.path.exists(destination):
            size = os.path.getsize(destination)
            if size < 1000:  # suspiciously small
                st.error(f"Download failed: {destination} too small. Check link/permissions.")
                st.stop()
        st.success(f"Downloaded {destination}")


# ----------------- CSS Loader -----------------
def load_css(css_file_path: str):
    if os.path.exists(css_file_path):
        with open(css_file_path, "r") as f:
            css = f.read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# ----------------- Download Required Files -----------------
download_file_google_drive(MOVIE_LIST_ID, MOVIE_LIST_FILE)
download_file_google_drive(SIMILARITY_ID, SIMILARITY_FILE)

# Load CSS
load_css("style.css")

# ----------------- Load Pickle Files -----------------
try:
    with open(MOVIE_LIST_FILE, 'rb') as f:
        movies = pickle.load(f)
    with open(SIMILARITY_FILE, 'rb') as f:
        similarity = pickle.load(f)
except Exception as e:
    st.error(f"Failed to load pickle files: {e}")
    st.stop()


# ----------------- TMDB Poster Fetch -----------------
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=3311b8aedeb68f05554d54a201c6ce0c&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path', '')
    return "https://image.tmdb.org/t/p/w500/" + poster_path if poster_path else ""


# ----------------- Recommendation Function -----------------
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


# ----------------- Streamlit App Layout -----------------
st.markdown('<div class="main-header">🎬 Movie Recommender</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Discover your next favorite film! Select a movie and get 5 recommendations.</div>',
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

    st.markdown("<hr style='margin:2em 0 1em 0; border-top:1.5px solid #4970a399'>", unsafe_allow_html=True)
    st.markdown(
        "<div style='color:#3ddad7; font-size:1.09rem; font-weight:600; text-align:center; margin-top:0.8em;'>"
        "Don't see your favorite? Try another movie for a fresh set of recommendations!"
        "</div>",
        unsafe_allow_html=True
    )

st.markdown(
    "<div style='text-align: center; font-size: 0.98rem; color: #f0e3bb; padding-top:22px'>"
    "Made with ❤️ for movie fans everywhere 🍿</div>",
    unsafe_allow_html=True
)
