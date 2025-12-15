import pandas as pd
import os
from dotenv import load_dotenv
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed 
load_dotenv()

KEY = os.getenv("API_KEY")
API_IMAGE = os.getenv("API_IMAGE_URL")
API_RESOURCE_URL = os.getenv("API_RESOURCE_URL")
SIZE="w500"


POSTER_PATH = "data/poster"
with open("data/poster/not_exist.txt", "r", encoding="utf-8") as f:
        not_found = list(map(int, f.read().splitlines()))
def get_poster_path(movie_id: int):
    if movie_id in not_found:
        return "Non-Poster-Film"
    return f"{POSTER_PATH}/{movie_id}.jpg"
def get_poster(tmdb_id: int, movie_id: int):
    try:
        #Check for poster folder
        os.makedirs(POSTER_PATH, exist_ok=True)

        request_url = API_IMAGE.replace("{movie_id}", str(tmdb_id))
        params = {"api_key" : KEY}

        res = requests.get(request_url, params=params).json()
        backdrop = res["backdrops"]
        best = max(
            backdrop,
            key = lambda x: (x["vote_average"])
        )
        best_path = best.get("file_path")
        image_path = API_RESOURCE_URL.replace("{size}", SIZE).replace("{file_path}", best_path[1:])
        image = requests.get(image_path)
        print(f"Found poster for move {movie_id} : {image_path}")

        with open(f"{POSTER_PATH}/{int(movie_id)}.jpg", "wb") as f:
            f.write(image.content)
        print(f"Saved poster image for move {movie_id}")
    except Exception as e:
        print(f"Movie {movie_id} poster not exist")
        with open("data/poster/not_exist.txt", "a", encoding="utf-8") as f:
            f.write(f"{movie_id}\n")
        return
def craw_poster_image(move_id_link_path: str, offset=1, max_workers=8):
    df = pd.read_csv(move_id_link_path)
    existing = {
        int(f.split(".")[0])
        for f in os.listdir(POSTER_PATH)
        if f.endswith(".jpg")
    }
    tasks = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for idx, row in df.iterrows():
            if idx + 1 < offset:
                continue
            
            tmdb_id = row["tmdbId"]
            movie_id = int(row["movieId"])
            if movie_id in existing or movie_id in not_found:
                continue
            tasks.append(
                executor.submit(get_poster, tmdb_id, movie_id)
            )
        for _ in tqdm(as_completed(tasks), total = len(tasks), desc="Poster sync"):
            pass


        