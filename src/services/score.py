import pandas as pd



def calc_avg_score(rating_path, result_path):
    df = pd.read_csv(rating_path, usecols=["movieId", "rating"])

    avg_df = (
        df.groupby("movieId", as_index=False)["rating"]
        .mean()
        .rename(columns={"rating": "avg"})
    )

    avg_df.to_csv(result_path, index=False)

