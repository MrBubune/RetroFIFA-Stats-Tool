import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import pairwise_distances

def compute_aggregate(df, player_col, mode="avg"):
    """
    Return aggregated dataframe indexed by player.
    mode: "avg" => mean per player. "total" => sum per player.
    """
    numeric = df.select_dtypes(include='number')
    if mode == "avg":
        agg = df.groupby(player_col)[numeric.columns].mean().reset_index()
    else:
        agg = df.groupby(player_col)[numeric.columns].sum().reset_index()
    return agg

def compute_similarity_table(df, player_col, player_name, features, agg_mode="avg", method="cosine", top_n=8):
    """
    Returns:
      - result_df: top_n similar players with their aggregated features and similarity score
      - base_row: a single-row DataFrame with the selected player's aggregated features
    """
    agg = compute_aggregate(df, player_col, mode=agg_mode)
    agg = agg.dropna(subset=features)
    # ensure numeric
    X = agg[features].astype(float).values
    # compute distances / similarities
    if method == "cosine":
        sim = cosine_similarity(X)
        # similarity matrix
        players = agg[player_col].tolist()
        idx = players.index(player_name)
        scores = sim[idx]
        score_name = "similarity"
        df_scores = pd.DataFrame({player_col: players, score_name: scores})
        merged = agg.merge(df_scores, on=player_col)
        res = merged.sort_values(by=score_name, ascending=False)
    else:
        # euclidean distance -> lower is nearer. convert to similarity-like (1 / (1 + dist))
        dists = pairwise_distances(X, metric='euclidean')
        players = agg[player_col].tolist()
        idx = players.index(player_name)
        dist_vec = dists[idx]
        sim_scores = 1 / (1 + dist_vec)
        score_name = "similarity"
        df_scores = pd.DataFrame({player_col: players, score_name: sim_scores})
        merged = agg.merge(df_scores, on=player_col)
        res = merged.sort_values(by=score_name, ascending=False)

    # base row
    base = res[res[player_col] == player_name].copy()
    base = base[[player_col] + features]
    base = base.reset_index(drop=True)

    # results excluding the player itself
    top = res[res[player_col] != player_name].head(top_n)
    return top.reset_index(drop=True), base
