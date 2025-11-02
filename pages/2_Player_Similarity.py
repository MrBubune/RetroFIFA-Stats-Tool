import streamlit as st
import pandas as pd
from modules.utils import load_sample_df, preprocess_uploaded_df
from modules.similarity import compute_similarity_table
import plotly.express as px

st.title("⚽ Player Similarity")

# upload or sample
uploaded = st.file_uploader("Upload match-level CSV (same file as Data Explorer)", type=["csv"], key="sim")
if uploaded:
    df = pd.read_csv(uploaded)
else:
    if st.checkbox("Use sample dataset for similarity"):
        df = load_sample_df()
    else:
        st.info("Upload a CSV or check 'Use sample'.")
        st.stop()

df = preprocess_uploaded_df(df)

st.sidebar.header("Similarity options")
player_col = st.sidebar.selectbox("Player name column", ["Player"] + list(df.columns))
id_col = player_col

agg_mode = st.sidebar.radio("Aggregation mode", ["Average (per-match mean)", "Total (season totals)"])
sim_method = st.sidebar.selectbox("Similarity method", ["Cosine", "Euclidean"])
top_n = st.sidebar.slider("Top N similar players", 3, 20, 8)

# numeric features
num_cols = df.select_dtypes(include='number').columns.tolist()
if not num_cols:
    st.warning("No numeric columns found. The similarity needs numeric stats.")
    st.stop()

chosen_feats = st.multiselect("Numeric features to compare", num_cols, default=num_cols[:6])
if not chosen_feats:
    st.warning("Pick at least one numeric feature.")
    st.stop()

# choose player
players = df[player_col].dropna().unique().tolist()
sel_player = st.selectbox("Choose player", players)

if st.button("Find similar players"):
    result_df, base_row = compute_similarity_table(
        df, player_col, sel_player, chosen_feats,
        agg_mode="avg" if agg_mode.startswith("Average") else "total",
        method=sim_method.lower(), top_n=top_n
    )

    st.subheader("Top similar players")
    st.dataframe(result_df)

    # radar / polar chart comparison
    radar = pd.concat([base_row, result_df[[player_col] + chosen_feats].rename(columns={player_col: player_col})])
    radar = radar.set_index(player_col)
    radar = radar.reset_index().melt(id_vars=player_col, var_name="stat", value_name="value")
    fig = px.line_polar(radar, r="value", theta="stat", color=player_col, line_close=True,
                        title="Attribute comparison (selected player vs similar players)")
    st.plotly_chart(fig, use_container_width=True)

    # scatter matrix of chosen features for context
    st.subheader("Scatter matrix (features)")
    fig2 = px.scatter_matrix(pd.concat([result_df, base_row], ignore_index=True), dimensions=chosen_feats, color=player_col)
    st.plotly_chart(fig2, use_container_width=True)
