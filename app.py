import pickle
import requests
import streamlit as st
import os
from huggingface_hub import hf_hub_download

# =========================
# Load CSS safely
# =========================
def load_css(css_file_path: str):
    if os.path.exists(css_file_path):
        with open(css_file_path, "r") as f:
            css = f.read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Try to load external CSS
load_css("style.css")

# =========================
# Poster Fetcher (with fallback)
# =========================
TMDB_API_KEY = "3311b8aedeb68f05554d54a201c6ce0c"

def fetch_poster(movie_id, movie_title=None):
    try:
        # Try fetching by movie_id
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            poster_path = data.get("poster_path", "")
            if poster_path:
                return "https://image.tmdb.org/t/p/w500/" + poster_path
    except:
        pass

    # If movie_id failed, fallback to search by title
    if movie_title:
        try:
            search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_title}"
            res = requests.get(search_url).json()
            results = res.get("results", [])
            if results:
                poster_path = results[0].get("poster_path", "")
                if poster_path:
                    return "https://image.tmdb.org/t/p/w500/" + poster_path
        except:
            pass

    # No poster found
    return ""

# =========================
# Recommendation Function
# =========================
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
        movie_title = movies.iloc[i[0]].title
        recommended_movie_names.append(movie_title)
        recommended_movie_posters.append(fetch_poster(movie_id, movie_title))

    return recommended_movie_names, recommended_movie_posters

# =========================
# Load Pickle files
# =========================
@st.cache_resource
def load_data():
    movies = pickle.load(open("movie_list.pkl", "rb"))
    similarity = pickle.load(open("similarity.pkl", "rb"))
    return movies, similarity

movies, similarity = load_data()

# =========================
# Streamlit App Layout
# =========================
st.markdown('<div class="main-header">🎬 Movie Recommender</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Discover your next favorite film! Select a movie and get 5 beautiful recommendations.</div>',
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
            if posters[i]:
                st.image(posters[i], use_container_width=True)
            else:
                st.error("Poster not available")

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
