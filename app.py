import pickle
import requests
import streamlit as st
import gzip
from huggingface_hub import hf_hub_download

# =========================
# CONFIG
# =========================
REPO_ID = "YuvrajChauhan3888/movie-recommender-data"  # your HF dataset repo

# =========================
# CSS Loader
# =========================
def load_css(css_file_path: str):
    try:
        with open(css_file_path, "r") as f:
            css = f.read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠ style.css not found. Skipping custom styles.")

# Load external CSS
load_css("style.css")

# =========================
# DATA LOADER
# =========================
@st.cache_resource
def load_data():
    # --- Download movie_list.pkl ---
    movie_list_path = hf_hub_download(
        repo_id=REPO_ID,
        repo_type="dataset",   # 👈 important fix
        filename="movie_list.pkl"
    )
    with open(movie_list_path, "rb") as f:
        movies = pickle.load(f)

    # --- Download similarity_compressed.pkl.gz ---
    similarity_path = hf_hub_download(
        repo_id=REPO_ID,
        repo_type="dataset",   # 👈 important fix
        filename="similarity_compressed.pkl.gz"
    )
    with gzip.open(similarity_path, "rb") as f:
        similarity = pickle.load(f)

    return movies, similarity

# Load data
movies, similarity = load_data()

# =========================
# HELPER FUNCTIONS
# =========================
def fetch_poster(movie_id):
    """Fetch poster from TMDB API"""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=3311b8aedeb68f05554d54a201c6ce0c&language=en-US"
    try:
        data = requests.get(url).json()
        poster_path = data.get('poster_path', '')
        return "https://image.tmdb.org/t/p/w500/" + poster_path if poster_path else ""
    except Exception:
        return ""

def recommend(movie):
    """Recommend top 5 similar movies"""
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

# =========================
# STREAMLIT UI
# =========================
st.markdown('<div class="main-header">🎬 Movie Recommender</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Discover your next favorite film! Select a movie and get 5 beautiful recommendations.</div>',
    unsafe_allow_html=True
)

# Dropdown
movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or choose a movie you like",
    movie_list,
    key="movie_dropdown"
)

# Recommendations
if st.button('Show Recommendations'):
    names, posters = recommend(selected_movie)
    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            safe_title = names[i].replace("<", "&lt;").replace(">", "&gt;")
            st.markdown(f"<div class='movie-title' title='{safe_title}'>{safe_title}</div>", unsafe_allow_html=True)
            if posters[i]:
                st.image(posters[i], use_container_width=True)
            else:
                st.text("(Poster unavailable)")
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
