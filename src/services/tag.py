import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix


def cosine(a: csr_matrix, b: csr_matrix):
    dot = a.multiply(b).sum()

    len_a = np.sqrt(a.multiply(a).sum())
    len_b = np.sqrt(b.multiply(b).sum())

    if len_a==0 or len_b ==0:
        return 0

    return dot / (len_a * len_b)

def combine(vec_ls: list[csr_matrix], scale = list[float]):
    w = sum(scale)
    if not vec_ls or w ==0:
        raise RuntimeError("Scale must not be 0")
    
    q = sum(v.multiply(s) for v, s in zip(vec_ls, scale)).multiply(1.0 / w)
    norm = np.sqrt(q.multiply(q).sum())
    if norm != 0:
        q = q.multiply(1.0 / norm)
    return q
            
def build_query_vector(
    movieids: list[int],
    stars: list[int],
    X: csr_matrix,
    movie2idx: dict[int, int]
) -> csr_matrix:
    if len(movieids) != len(stars):
        raise RuntimeError("Movie list must have the same lenth of star list")
    vecs = []
    scales = []
    for movid, star in zip(movieids, stars):
        if movid not in movie2idx:
            continue
        vecs.append(X[movie2idx[movid]])
        scales.append(star)
    return combine(vecs, scales)

def init_matrix(tag_path: str):
    df = pd.read_csv(tag_path)
    df = df[df["relevance"] > 0.3]


    movies = df["movieId"].unique()
    tags = df["tagId"].unique()

    movie2idx = {m: i for i, m in enumerate(movies)}
    tag2idx = {m: i for i, m in enumerate(tags)}


    rows = df["movieId"].map(movie2idx).to_numpy()
    cols = df["tagId"].map(tag2idx).to_numpy()
    data = df["relevance"].to_numpy()

    X = csr_matrix(
        (data, (rows, cols)),
        shape=(len(movies), len(tags))
    )

    return movie2idx, tag2idx, X


def get_top_k(
    q: tuple[list[int], list[int]],
    X: csr_matrix,
    movie2idx: dict[int, int],
    k: int = 10,
) -> list[tuple[int, float]]:
    """
    Get top-k movieIds most similar to input query (movieids, stars)
    """

    query = build_query_vector(q[0], q[1], X, movie2idx)

    scores = (X @ query.T).toarray().ravel()

    movie_norms = np.sqrt(X.multiply(X).sum(axis=1)).A1

    sim = np.zeros_like(scores)
    mask = movie_norms != 0
    sim[mask] = scores[mask] / movie_norms[mask]

    top_idx = np.argsort(sim)[-(k+len(q[0])):][::-1]

    idx2movie = {v: m for m, v in movie2idx.items()}

    return [(idx2movie[i], sim[i]) for i in top_idx if idx2movie[i] not in q[0]]
