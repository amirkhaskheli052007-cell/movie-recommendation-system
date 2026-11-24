
import streamlit as st
import requests
from training import recommend, new_df

# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="CineMatch - Movie Recommendations",
    page_icon="🎬",
    layout="wide"
)

# ---------------- TMDB CONFIGURATION ----------------

TMDB_API_KEY = st.secrets.get("TMDB_API_KEY", "")

TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>
.stApp {
    background: #101010;
    color: white;
}

header {
    background: transparent !important;
}

.main-title {
    color: #e50914;
    font-size: 45px;
    font-weight: 900;
    text-align: center;
    margin-bottom: 0;
}

.subtitle {
    color: #bbbbbb;
    text-align: center;
    font-size: 17px;
    margin-bottom: 35px;
}

.section-title {
    color: white;
    font-size: 27px;
    font-weight: bold;
    margin-top: 25px;
}

.movie-title {
    color: white;
    font-size: 17px;
    font-weight: bold;
}

div.stButton > button {
    background-color: #e50914;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: bold;
    padding: 10px 25px;
}

div.stButton > button:hover {
    background-color: #b20710;
    color: white;
}

[data-testid="stSelectbox"] {
    background: #1c1c1c;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# ---------------- TMDB MOVIE DETAILS ----------------

@st.cache_data(ttl=86400)
def get_movie_details(movie_id, api_key):

    url = f"https://api.themoviedb.org/3/movie/{int(movie_id)}"

    try:
        response = requests.get(
            url,
            params={"api_key": api_key},
            timeout=20
        )

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException:
        return None


# ---------------- MOVIE DATA ----------------

movie_ids = dict(
    zip(new_df["title"], new_df["movie_id"])
)

movie_titles = new_df["title"].drop_duplicates().tolist()


# ---------------- HEADER ----------------

st.markdown(
    '<div class="main-title">🎬 CINEMATCH</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Discover Your Next Favourite Movie</div>',
    unsafe_allow_html=True
)

st.divider()

# ---------------- MOVIE SELECTION ----------------

st.markdown(
    '<div class="section-title">🔎 Find Your Movie</div>',
    unsafe_allow_html=True
)

selected_movie = st.selectbox(
    "Select a movie",
    movie_titles,
    index=movie_titles.index("Avatar")
    if "Avatar" in movie_titles else 0
)

# ---------------- SELECTED MOVIE DETAILS ----------------

selected_id = movie_ids[selected_movie]

selected_details = get_movie_details(
    selected_id,
    TMDB_API_KEY
)

if selected_details:

    left, right = st.columns([1, 2])

    with left:
        poster = selected_details.get("poster_path")

        if poster:
            st.image(
                TMDB_IMAGE_URL + poster,
                use_container_width=True
            )
        else:
            st.info("Poster not available.")

    with right:
        st.markdown(
            f"## {selected_details.get('title', selected_movie)}"
        )

        st.write(
            "⭐ Rating:",
            selected_details.get("vote_average", "N/A")
        )

        st.write(
            "📅 Release Date:",
            selected_details.get("release_date", "N/A")
        )

        genres = selected_details.get("genres", [])
        genre_names = ", ".join(
            genre["name"] for genre in genres
        )

        st.write("🎭 Genres:", genre_names or "N/A")

        st.write("**Movie Overview**")

        st.write(
            selected_details.get(
                "overview",
                "Overview not available."
            )
        )

else:
    st.warning(
        "Movie details could not be loaded from TMDB. "
        "Please check your API connection."
    )

# ---------------- RECOMMENDATIONS ----------------

st.divider()

if st.button("🔥 GET MOVIE RECOMMENDATIONS", use_container_width=True):

    recommendations = recommend(selected_movie)

    st.markdown(
        '<div class="section-title">🍿 Recommended For You</div>',
        unsafe_allow_html=True
    )

    if recommendations:

        columns = st.columns(5)

        for index, movie in enumerate(recommendations):

            with columns[index % 5]:

                movie_id = movie_ids.get(movie)

                if movie_id is None:
                    st.write(movie)
                    continue

                details = get_movie_details(
                    movie_id,
                    TMDB_API_KEY
                )

                if details:

                    poster = details.get("poster_path")

                    if poster:
                        st.image(
                            TMDB_IMAGE_URL + poster,
                            use_container_width=True
                        )
                    else:
                        st.info("Poster unavailable")

                    st.markdown(
                        f"**{details.get('title', movie)}**"
                    )

                    st.caption(
                        f"⭐ {details.get('vote_average', 'N/A')} "
                        f"| {details.get('release_date', 'N/A')[:4]}"
                    )

                else:
                    st.write(movie)
                    st.caption("Movie details unavailable")

    else:
        st.warning("No recommendations found.")

# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "Movie data and images provided by TMDB. "
    "This product uses the TMDB API but is not endorsed or certified by TMDB."
)
