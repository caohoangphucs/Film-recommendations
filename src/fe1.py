import streamlit as st
import pandas as pd
from rapidfuzz import process
from recommender import MOVIE_PATH, rcm

movies_df = pd.read_csv(MOVIE_PATH) 
movie_titles = movies_df ["title"].tolist()

# đưa vào str trả về một list(str) phim giống nhất và loại trừ list(str) phim đã chọn
def search_suggest(query, movies, exclude_list=None, limit=10):
    if exclude_list is None:
        exclude_list = []
    exclude_set = set(exclude_list)
    candidates = [ # loại bỏ các phim đã chọn
        m for m in movies
        if m not in exclude_set
    ]
    results = process.extract(
        query,
        candidates,
        score_cutoff=60,
        limit=limit
    )
    return [r[0] for r in results]


st.set_page_config(layout="wide")# cấu hình trang
if "selected_movies" not in st.session_state:
    st.session_state.selected_movies = {}  # {movieId: rating}
if "page" not in st.session_state:# trang hiện tại
    st.session_state.page = "home"


with st.sidebar:
    st.markdown("🎬 Movie Recommender")
    st.caption("Content-based Filtering")

    st.markdown("---")

    if st.button("🏠 Trang chủ", use_container_width=True):
        st.session_state.page = "home"

    if st.button("🎬 Gợi ý phim", use_container_width=True):
        st.session_state.page = "movie"

    if st.button("phần con linh", use_container_width=True):
        st.session_state.page = "user"

    st.markdown("---")
    st.caption("📚 Đồ án Hệ gợi ý phim")


page = st.session_state.page

if page == "home":
    st.title("🏠 Trang chủ")
    st.write("Chào mừng bạn đến hệ thống gợi ý phim")

elif page == "movie":
    st.title("🎬 Gợi ý theo phim")
    top = st.container()
    bottom = st.container()

    with top:
        col_left, col_right = st.columns([6, 4])
        # phần tìm kiếm phim
        with col_left:
            st.header("🔍 Tìm kiếm & đánh giá phim")

            query = st.text_input(
                "Nhập tên phim",
                placeholder="Avatar, Titanic, Batman..."
            )

            if query:
                suggestions = search_suggest(
                    query,
                    movie_titles,
                    exclude_list=[
                        movies_df.loc[movies_df["movieId"] == mid, "title"].values[0]
                        for mid in st.session_state.selected_movies.keys()
                    ]
                )

                for title in suggestions:
                    if st.button(f"➕ {title}", key=f"add_{title}"):
                        movie_id = int(
                            movies_df.loc[movies_df["title"] == title, "movieId"].values[0]
                        )
                        st.session_state.selected_movies[movie_id] = 5
                        st.rerun()
            # --- DANH SÁCH ĐÃ CHỌN + ĐÁNH GIÁ ---
            if st.session_state.selected_movies:
                st.subheader("⭐ Phim bạn đã chọn")

                for movie_id, rating in st.session_state.selected_movies.items():
                    title = movies_df.loc[
                        movies_df["movieId"] == movie_id, "title"
                    ].values[0]

                    col_a, col_b, col_c = st.columns([4, 3, 1])

                    with col_a:
                        st.write("🎬", title)

                    with col_b:
                        new_rating = st.slider(
                            "Đánh giá",
                            1, 5,
                            rating,
                            key=f"rate_left_{movie_id}"
                        )
                        st.session_state.selected_movies[movie_id] = new_rating

                    with col_c:
                        if st.button("❌", key=f"remove_left_{movie_id}"):
                            del st.session_state.selected_movies[movie_id]
                            st.rerun()


        with col_right:
            selected_movie_ids = list(st.session_state.selected_movies.keys())
            ratings_user = [st.session_state.selected_movies[mid] for mid in selected_movie_ids]

            if not selected_movie_ids:
                st.info("Hãy chọn ít nhất 1 phim để nhận gợi ý")
            else:
                recommendations = rcm.recommend((selected_movie_ids, ratings_user))

                if not recommendations:
                    st.warning("Không tìm được phim phù hợp")
                else:
                    for movie, score in recommendations:
                        box = st.container(border=True)
                        with box:
                            col_a, col_b = st.columns([4, 1])

                            with col_a:
                                st.write(f"🎬 **{movie.title}** ({movie.year})")
                                st.caption(
                                    f"⭐ Rating TB: {movie.average_score:.1f} | 🎯 Độ tương đồng: {score:.2f}"
                                )

                            with col_b:
                                if st.button("Chọn", key=f"rec_{movie.id}"):
                                    st.session_state.selected_movies[movie.id] = 5
                                    st.rerun()


        
    st.markdown("---")

    # phần các phim đã chọn
    with bottom:
        for movie_id, rating in st.session_state.selected_movies.items():
            title = movies_df.loc[movies_df["movieId"] == movie_id, "title"].values[0]

            col_a, col_b, col_c = st.columns([4, 3, 1])

            with col_a:
                st.write("🎬", title)

            with col_b:
                new_rating = st.slider("Đánh giá", 1, 5, rating, key=f"rate_{movie_id}")
                st.session_state.selected_movies[movie_id] = new_rating

            with col_c:
                if st.button("❌", key=f"remove_{movie_id}"):
                    del st.session_state.selected_movies[movie_id]
                    st.rerun()

elif page == "user":
    st.title("👤 Gợi ý cho người dùng")
    st.write("Gợi ý phim dựa trên lịch sử đánh giá")


