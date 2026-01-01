import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Top 10 bộ phim đánh giá cao theo năm (người dùng nhập)
def plot_top10_movies_by_year(movie_path, rating_path, year):
    movies = pd.read_csv(movie_path)
    ratings = pd.read_csv(rating_path)

    df = movies.merge(ratings, on="movieId", how="inner")
    df["year"] = df["title"].str.extract(r"\((\d{4})\)").astype(float)
    df_year = df[df["year"] == year]

    if df_year.empty:
        st.warning(f"Không có dữ liệu cho năm {year}")
        return

    top10 = (
        df_year.groupby("title", as_index=False)["avg"]
        .mean()
        .sort_values("avg", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    y_pos = np.arange(len(top10))

    threshold = 4.5

    colors = ["#b65200" if v >= threshold else "#3E5C24" for v in top10["avg"]]

    ax.hlines(
        y=y_pos,
        xmin=0,
        xmax=top10["avg"],
        color=colors,   
        linewidth=3,
        alpha=0.6
    )

    ax.scatter(
        top10["avg"],
        y_pos,
        color=colors,  
        s=120,
        zorder=3
    )

    for i, v in enumerate(top10["avg"]):
        ax.text(
            v + 0.05,
            i,
            f"{v:.2f}",
            va="center",
            fontsize=10,
            fontweight='bold',
            color="#333333"
        )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(top10["title"])
    ax.set_xlabel("Điểm đánh giá trung bình, fontsize=12, fontweight='bold'") 
    ax.set_title(f"Top 10 phim được đánh giá cao nhất năm {year}, fontsize=14, fontweight='bold', pad=20")

    ax.invert_yaxis()

    ax.grid(axis="x", linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    st.pyplot(fig)

# top 10 thể loại phổ biến
def plot_top_genres(movies_path):
    movies = pd.read_csv(movies_path)
    genres = movies["genres"].str.split("|").explode()
    genre_count = genres.value_counts().head(10)

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = plt.cm.Blues(np.linspace(0.8, 0.4, len(genre_count)))

    bars = ax.bar(
        genre_count.index,
        genre_count.values,
        color=colors,
        edgecolor="#112d49",
        linewidth=0.8,
        alpha=0.9
    )

    max_val = genre_count.values.max()
    threshold = max_val * 0.7  
    for bar in bars:
        yval = bar.get_height()
        text_color = "#581811" if yval >= threshold else "#333333"
        font_weight = 'bold' if yval >= threshold else 'normal'
        
        ax.text(
            bar.get_x() + bar.get_width()/2, 
            yval + 1, 
            int(yval), 
            ha='center', 
            va='bottom', 
            fontsize=11, 
            color=text_color, 
            fontweight=font_weight 
        )

    ax.set_xlabel("Thể loại phim", fontsize=12, fontweight='bold')
    ax.set_ylabel("Số lượng phim", fontsize=12, fontweight='bold')
    ax.set_title("Top 10 Thể loại phim phổ biến nhất", fontsize=14, fontweight='bold', pad=20)

    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    st.pyplot(fig)

# số lượng phim theo năm
def plot_movies_per_year(movies_path):
    movies = pd.read_csv(movies_path)
    movies["year"] = movies["title"].str.extract(r"\((\d{4})\)").astype(float)
    movie_per_year = movies["year"].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(
        movie_per_year.index,
        movie_per_year.values,
        color="#2c3e50",
        linewidth=2.5,
        alpha=0.8
    )

    ax.fill_between(
        movie_per_year.index, 
        movie_per_year.values, 
        color="#3498db", 
        alpha=0.2  
    )
    max_year = movie_per_year.idxmax()
    max_val = movie_per_year.max()

    ax.scatter(movie_per_year.index, movie_per_year.values, color="#38517A", s=20, zorder=3)

    ax.scatter(max_year, max_val, color="#DF550A", s=120, edgecolor="white", linewidth=2, zorder=4)
    

    ax.set_xlabel("Năm phát hành", fontsize=12, fontweight='bold')
    ax.set_ylabel("Số lượng phim", fontsize=12, fontweight='bold')
    ax.set_title("Xu hướng số lượng phim phát hành qua các năm", fontsize=14, fontweight='bold', pad=20)

    ax.grid(True, linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    st.pyplot(fig)

# Phân bố điểm đánh giá
def plot_rating_distribution(rating_path):
    ratings = pd.read_csv(rating_path)

    fig, ax = plt.subplots(figsize=(10, 6))
    counts, bins, patches = ax.hist(
        ratings["avg"],
        bins=20,
        edgecolor="white",
        linewidth=0.5,
        alpha=0.85
    )

    for bin_value, patch in zip(bins, patches):
        if bin_value < 2.5:
            patch.set_facecolor("#0C1327")
        elif bin_value < 4.0:
            patch.set_facecolor("#1F5071")
        else:
            patch.set_facecolor("#a0d7ff")

    ratings["avg"].plot(kind='kde', ax=ax, secondary_y=True, color="#a84e00", linewidth=2)
    ax.right_ax.set_yticks([])

    ax.set_xlabel("Điểm đánh giá trung bình", fontsize=12, fontweight='bold')
    ax.set_ylabel("Số lượng phim (Tần suất)", fontsize=12, fontweight='bold')
    ax.set_title("Phân bổ điểm đánh giá của các bộ phim", fontsize=14, fontweight='bold', pad=20)

    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    st.pyplot(fig)


# Đánh giá sự tranh cãi
def plot_rating_controversy_donut(rating_path):
    ratings = pd.read_csv(rating_path)

    stats = ratings.groupby("movieId")["rating"].agg(["std", "count"])
    stats = stats[stats["count"] > 50]

    def label_opinion(std):
        if std >= 1.1:
            return "Tranh cãi cao"
        elif std <= 0.8:
            return "Đồng thuận cao"
        else:
            return "Ý kiến trái chiều"

    stats["opinion"] = stats["std"].apply(label_opinion)
    opinion_counts = stats["opinion"].value_counts()

    order = ["Tranh cãi cao", "Ý kiến trái chiều", "Đồng thuận cao"]
    opinion_counts = opinion_counts.reindex(order).dropna()

    colors = ["#D62828", "#F77F00", "#EAE2B7"]

    # ===== CANVAS =====
    fig, ax = plt.subplots(figsize=(3.8, 3.8))

    wedges, _, autotexts = ax.pie(
        opinion_counts,
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        radius=1.15,                      # DONUT TO
        pctdistance=0.65,
        wedgeprops=dict(
            width=0.35,
            edgecolor="white",
            linewidth=1.5
        )
    )

    # % trong donut
    plt.setp(autotexts, fontsize=6, fontweight="bold")

    # Title
    ax.set_title(
        "Mức độ đồng thuận của khán giả",
        fontsize=12,
        fontweight="bold",
        pad=6
    )

    # Legend KHÔNG đè donut
    ax.legend(
        wedges,
        opinion_counts.index,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.22),
        frameon=False,
        fontsize=9
    )

    ax.set_aspect("equal")
    plt.tight_layout()

    return fig
# Biểu đồ Phân bổ Kỷ nguyên Điện ảnh
def plot_movie_eras_donut(movies_path):
    import pandas as pd
    import matplotlib.pyplot as plt

    movies = pd.read_csv(movies_path)
    movies["year"] = movies["title"].str.extract(r"\((\d{4})\)").astype("Int64")
    movies = movies.dropna(subset=["year"])

    def categorize_era(year):
        if year < 1980:
            return "Cổ điển (<1980)"
        elif year < 2000:
            return "Giao thời (80s–90s)"
        elif year < 2015:
            return "Hiện đại (2000s)"
        else:
            return "Mới nhất (2015+)"

    era_data = movies["year"].apply(categorize_era).value_counts()

    order = [
        "Cổ điển (<1980)",
        "Giao thời (80s–90s)",
        "Hiện đại (2000s)",
        "Mới nhất (2015+)"
    ]
    era_data = era_data.reindex(order).dropna()

    colors = ["#1D3557", "#457B9D", "#A8DADC", "#F1FAEE"]

    # ===== FIG NHỎ – DONUT TO – CÂN GIỮA =====
    fig, ax = plt.subplots(figsize=(2.6, 2.8))

    wedges, _, autotexts = ax.pie(
        era_data,
        autopct="%1.1f%%",
        startangle=90,
        colors=colors,
        pctdistance=0.65,
        wedgeprops=dict(width=0.32, edgecolor="white", linewidth=1.2)
    )

    plt.setp(autotexts, fontsize=4.5, fontweight="bold")

    ax.legend(
        wedges,
        era_data.index,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.22),
        ncol=1,
        frameon=False,
        fontsize=6
    )

    ax.set_title(
        "Phân bổ phim theo kỷ nguyên",
        fontsize=6,
        fontweight="bold",
        pad=4
    )
    return fig