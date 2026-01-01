import streamlit as st
import pandas as pd
import os
import visualize
from rapidfuzz import process
from recommender import MOVIE_PATH, rcm
from PIL import Image

# ================== PATH CHUẨN ==================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # thư mục chứa file .py
DATA_DIR = os.path.join(BASE_DIR, "data")
POSTER_DIR = os.path.join(DATA_DIR, "poster")

# ================== LOAD POSTER ==================
@st.cache_data(show_spinner=False)
def load_poster_fit(path: str, target_w: int = 130, target_h: int = 180):
    """
    Center-crop ảnh về đúng tỉ lệ rồi resize về target_w x target_h
    => Ảnh luôn full khung, không méo
    """
    img = Image.open(path).convert("RGB")
    w, h = img.size

    target_ratio = target_w / target_h
    src_ratio = w / h

    if src_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))

    img = img.resize((target_w, target_h))
    return img

# ================== LOAD DATA ==================
movies_df = pd.read_csv(MOVIE_PATH)
movie_titles = movies_df["title"].tolist()

# ================== SEARCH GỢI Ý ==================
def search_suggest(query, movies, exclude_list=None, limit=10):
    if exclude_list is None:
        exclude_list = []

    exclude_set = set(exclude_list)
    candidates = [m for m in movies if m not in exclude_set]

    results = process.extract(
        query,
        candidates,
        score_cutoff=60,
        limit=limit
    )
    return [r[0] for r in results]

# ================== SESSION ==================
st.set_page_config(layout="wide")

if "selected_movies" not in st.session_state:
    st.session_state.selected_movies = {}   # {movieId: rating}

if "page" not in st.session_state:
    st.session_state.page = "home"

# ================== SIDEBAR ==================
with st.sidebar:
    st.markdown("🎬 Movie Recommender")
    st.caption("Content-based Filtering")

    st.markdown("---")

    if st.button("🏠 Trang chủ", use_container_width=True):
        st.session_state.page = "home"

    if st.button("🎬 Gợi ý phim", use_container_width=True):
        st.session_state.page = "movie"

    if st.button("📈 Trực quan dữ liệu", use_container_width=True):
        st.session_state.page = "user"

    st.markdown("---")
    st.caption("📚 Đồ án Hệ gợi ý phim")

# ================== PAGE ROUTER ==================
page = st.session_state.page

# ================== HOME ==================
if page == "home":
    st.title("🏠 Trang chủ")
    st.write("Chào mừng bạn đến hệ thống gợi ý phim")

# ================== MOVIE RECOMMEND ==================
elif page == "movie":
    st.markdown(
        "<h2 style='text-align: center;'>Gợi ý phim theo sở thích của bạn</h2>",
        unsafe_allow_html=True
    )

    top = st.container()
    bottom = st.container()

    with top:
        col_left, col_right = st.columns([6, 4])

        # ===== SEARCH =====
        with col_left:
            st.subheader("🔍 Tìm kiếm các phim đã xem")

            query = st.text_input(
                "Nhập tên phim",
                placeholder="Avatar, Titanic, Batman..."
            )

            if query:
                suggestions = search_suggest(
                    query,
                    movie_titles,
                    exclude_list=[
                        movies_df.loc[
                            movies_df["movieId"] == mid, "title"
                        ].values[0]
                        for mid in st.session_state.selected_movies.keys()
                    ]
                )

                for title in suggestions:
                    if st.button(f"➕ {title}", key=f"add_{title}"):
                        movie_id = int(
                            movies_df.loc[
                                movies_df["title"] == title, "movieId"
                            ].values[0]
                        )
                        st.session_state.selected_movies[movie_id] = 5
                        st.rerun()

        # ===== RECOMMEND RESULT =====
        with col_right:
            st.subheader("⭐ Phim được gợi ý")

            selected_movie_ids = list(st.session_state.selected_movies.keys())
            ratings_user = [
                st.session_state.selected_movies[mid]
                for mid in selected_movie_ids
            ]

            if not selected_movie_ids:
                st.info("Hãy chọn và đánh giá ít nhất 1 phim")
            else:
                ratings_user_safe = [2 if r <= 1 else r for r in ratings_user]

                try:
                    recommendations = rcm.recommend(
                        (selected_movie_ids, ratings_user_safe)
                    )

                    seen_ids = set(selected_movie_ids)
                    recommendations = [
                        (movie, score)
                        for movie, score in recommendations
                        if movie.id not in seen_ids
                    ]
                except Exception:
                    st.error("Không thể tạo gợi ý")
                    st.stop()

                if not recommendations:
                    st.warning("Không tìm được phim phù hợp")
                else:
                    for movie, score in recommendations:
                        movie_id = movie.id

                        poster_path = os.path.join(POSTER_DIR, f"{movie_id}.jpg")
                        fallback_path = os.path.join(POSTER_DIR, "default.jpg")

                        if os.path.exists(poster_path):
                            show_path = poster_path
                        elif os.path.exists(fallback_path):
                            show_path = fallback_path
                        else:
                            show_path = None

                        with st.container(border=True):
                            col_img, col_info = st.columns([1, 2])

                            with col_img:
                                if show_path:
                                    st.image(load_poster_fit(show_path))
                                else:
                                    st.write("🖼️ No poster")

                            with col_info:
                                st.write(f"🎬 **{movie.title}** ({movie.year})")
                                st.caption(
                                    f"⭐ Rating TB: {movie.average_score:.1f}\n\n"
                                    f"🎯 Độ tương đồng: {score:.2f}"
                                )

    # ===== SELECTED MOVIES =====
    with bottom:
        st.subheader("🎞️ Các phim bạn đã xem & đánh giá")

        if not st.session_state.selected_movies:
            st.info("Bạn chưa chọn phim nào")
        else:
            for movie_id, rating in st.session_state.selected_movies.items():
                title = movies_df.loc[
                    movies_df["movieId"] == movie_id, "title"
                ].values[0]

                with st.container(border=True):
                    col_info, col_rating, col_action = st.columns([4, 3, 1])

                    with col_info:
                        st.write(f"🎬 **{title}**")

                    with col_rating:
                        new_rating = st.slider(
                            "Đánh giá của bạn",
                            1, 5,
                            rating,
                            key=f"rate_{movie_id}"
                        )
                        st.session_state.selected_movies[movie_id] = new_rating

                    with col_action:
                        st.write("")
                        if st.button("❌ Xóa", key=f"remove_{movie_id}"):
                            del st.session_state.selected_movies[movie_id]
                            st.rerun()

# ================== USER / VISUALIZE ==================
elif page == "user":
    st.title("📊 Phân tích & trực quan dữ liệu phim")
    st.markdown("---")

    MOVIES_ANALYSIS_PATH = os.path.join(DATA_DIR, "movie.csv")
    AVG_RATINGS_ANALYSIS_PATH = os.path.join(DATA_DIR, "avg_rating.csv")
    RATINGS_PATH = os.path.join(DATA_DIR, "rating.csv")

    st.subheader("🎬 Top 10 phim được đánh giá cao theo năm")
    year = st.number_input(
        "Nhập năm phát hành",
        min_value=1900,
        max_value=2025,
        value=2010,
        step=1
    )

    visualize.plot_top10_movies_by_year(
        movie_path=MOVIES_ANALYSIS_PATH,
        rating_path=AVG_RATINGS_ANALYSIS_PATH,
        year=year
    )

    st.markdown("---")
    st.subheader("🏷️ Top 10 thể loại phim phổ biến")
    visualize.plot_top_genres(MOVIES_ANALYSIS_PATH)

    st.markdown("---")
    st.subheader("📈 Xu hướng số lượng phim theo năm")
    visualize.plot_movies_per_year(MOVIES_ANALYSIS_PATH)

    st.markdown("---")
    st.subheader("⭐ Phân bố điểm đánh giá trung bình")
    visualize.plot_rating_distribution(AVG_RATINGS_ANALYSIS_PATH)

    # ===== DONUT TRANH CÃI =====
    st.markdown("---")
    st.subheader("🗣️ Mức độ tranh cãi trong đánh giá phim")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        fig = visualize.plot_rating_controversy_donut(
            rating_path=RATINGS_PATH
        )
        st.pyplot(fig, use_container_width=False)

    # ===== DONUT KỶ NGUYÊN =====
    st.markdown("---")
    st.subheader("🎞️ Phân bố phim theo kỷ nguyên phát hành")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        fig = visualize.plot_movie_eras_donut(
            movies_path=MOVIES_ANALYSIS_PATH
        )
        st.pyplot(fig, use_container_width=False)