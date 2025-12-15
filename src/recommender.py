from data.poster import get_poster,craw_poster_image, get_poster_path, POSTER_PATH
from data.score import calc_avg_score
from data.tag import *
from typing import Optional
import os
from dataclasses import dataclass
import pandas as pd
import re
from scipy.sparse import csr_matrix

TAG_PATH="data/genome_scores.csv"
LINK_MOVEID_TMDB="data/link.csv"
RATING_PATH = "data/rating.csv"
MOVIE_PATH = "data/movie.csv"
RESULT_RATING_PATH = "data/avg_rating.csv"
@dataclass
class Movie:
    id: int
    title: str
    year: int
    genres: list[str]
    average_score: float
    poster_path: Optional[str] = None

    def show(self):
        genres = ", ".join(self.genres)
        poster = self.poster_path or "N/A"

        print(
            f" {self.id} {self.title} ({self.year})\n"
            f" Rating: {self.average_score}\n"
            f" Genres: {genres}\n"
            f" Poster: {poster}"
        )
class Recommender:
    movies : list[Movie]
    embeder : tuple[dict[int, int], dict[int, int], csr_matrix]
    movie_map: dict
    def __init__(self, movies : list[Movie], embeder: tuple[dict[int, int], dict[int, int], csr_matrix]):
        self.movies = movies
        self.embeder = embeder
        self.movie_map: dict[int, Movie] = {m.id: m for m in movies}
    def get_movie(self, movie_id: int):
        return self.movie_map.get(movie_id)
    def recommend(self, rated_movie: tuple[list[int], list[int]])->list[tuple[Movie, float]]:
        """Return a list of movie which similar to input list
        input list need to be a list of movie id and how many stars user rated
        Example: ([1, 10, 20], [1, 4, 5]) mean get recommend for movie id 1 with 1 stars, etc """
        results = get_top_k(rated_movie, self.embeder[2], self.embeder[0], k = 10)
        q_res = []
        for res in results:
            movieid = res[0]
            confident = res[1]
            q_res.append(tuple([self.get_movie(movieid), confident]))
        return q_res


#Poster is enough
print("Checking for poster....")
craw_poster_image(LINK_MOVEID_TMDB, max_workers=20)
print("Poster init done")



#Is average score caculated
print("Checking for avarage rating from user...")
if not os.path.exists(RESULT_RATING_PATH):
    calc_avg_score(RATING_PATH, RESULT_RATING_PATH)
print("Average score check done")

#Init vector for tag
print("Embeding tag....")
movieidx, tagidx, matrx = init_matrix(TAG_PATH)
print("Tag embed.")


#load all data to ram
movies = pd.read_csv(MOVIE_PATH)
ratings = pd.read_csv(RESULT_RATING_PATH)

df = movies.merge(ratings, on="movieId", how="left")

#Create in-ram database
db = []
for _, row in df.iterrows():
    raw_title = row["title"]

    m = re.search(r"\((\d{4})\)$", raw_title)
    if m:
        year = int(m.group(1))
        title = raw_title[:m.start()].strip()
    else:
        year = None
        title = raw_title

    new_movie = Movie(
        id=row["movieId"],
        title=title,
        year=year,
        genres=row["genres"].split("|"),
        average_score=row["avg"],
        poster_path=get_poster_path(row["movieId"]),
    )

    db.append(new_movie)

#Create recommender
rcm = Recommender(db, (movieidx, tagidx, matrx))

for result in rcm.recommend(([1], [5])):
    result[0].show()