import streamlit as st
from modules.utils import load_sample_df

st.set_page_config(page_title="FIFA Season Stats", layout="wide")

st.title("⚽ FIFA Season Match Stats Visualizer")

st.markdown("""
This app visualizes match-level player stats across a season.
Upload your CSV or use the sample dataset.
""")

st.header("Quick notes")
st.markdown("""
- Data should be match-level. One row = one player's performance in one match.
- Typical columns: `Player`, `Team`, `Opponent`, `Date`, `Minutes`, `Goals`, `Assists`, `Shots`, `KeyPasses`, `Tackles`, `Interceptions`, `PassesCompleted`, `DistanceKm`, etc.
- Use **Player Similarity** to compare players by totals or averages across the season.
""")

st.sidebar.header("Start")
use_sample = st.sidebar.button("Load sample dataset")
if use_sample:
    df = load_sample_df()
    st.write("Sample dataset loaded (first 20 rows).")
    st.dataframe(df.head(20))
else:
    st.sidebar.write("Open the pages in the top-left menu.")
