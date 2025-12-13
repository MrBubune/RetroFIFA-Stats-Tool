import streamlit as st
import pandas as pd
import plotly.express as px
from modules.utils import load_sample_df, preprocess_uploaded_df

st.set_page_config(page_title="Radar Comparison", layout="wide")

st.title("🕸️ Player Radar Comparison")

# --- 1. Data Loading (Session State Pattern) ---
if 'explorer_raw_data' in st.session_state and not st.session_state['explorer_raw_data'].empty:
    df = st.session_state['explorer_raw_data']
else:
    st.info("No data found in session. Using sample data for demo.")
    df = load_sample_df()

# Basic cleaning
df = preprocess_uploaded_df(df)

# --- 2. Sidebar Controls ---
st.sidebar.header("Configuration")

# Identify columns
all_cols = list(df.columns)
num_cols = df.select_dtypes(include='number').columns.tolist()

# a. Select Player Column
# Try to auto-detect 'Player' or 'Name'
default_player_col = "Player" if "Player" in all_cols else all_cols[0]
player_col = st.sidebar.selectbox("Player Name Column", all_cols, index=all_cols.index(default_player_col))

# b. Aggregation Method
agg_method = st.sidebar.radio("Aggregation Method", ["Average (per match)", "Total (season sum)"])

# --- 3. Main Selection Area ---

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. Select Players")
    # Get unique players
    unique_players = sorted(df[player_col].dropna().unique().tolist())
    
    # Default selection (first 3 players)
    default_players = unique_players[:3] if len(unique_players) >= 3 else unique_players
    
    selected_players = st.multiselect(
        "Choose players to compare:", 
        unique_players, 
        default=default_players
    )

with col2:
    st.subheader("2. Select Stats")
    # Filter out ID columns usually not useful for radar (like MatchID, Year)
    useful_numerics = [c for c in num_cols if "ID" not in c and "Year" not in c]
    
    selected_stats = st.multiselect(
        "Choose at least 3 numeric attributes:", 
        useful_numerics,
        default=useful_numerics[:5] if len(useful_numerics) >= 5 else useful_numerics
    )

# --- 4. Data Processing & Visualization ---

if not selected_players:
    st.warning("Please select at least one player.")
    st.stop()

if len(selected_stats) < 3:
    st.warning("Please select at least 3 stats to generate a valid radar chart.")
    st.stop()

# Filter data for selected players
filtered_df = df[df[player_col].isin(selected_players)]

# Aggregate data
if agg_method == "Total (season sum)":
    agg_df = filtered_df.groupby(player_col)[selected_stats].sum().reset_index()
else:
    agg_df = filtered_df.groupby(player_col)[selected_stats].mean().reset_index()

# --- Normalization Logic ---
# Radar charts work best when data is normalized (0-1 scale)
# Otherwise, "Passes" (50) dwarfs "Goals" (0.5).

use_normalization = st.checkbox("Normalize values (0-1 scale) for better shape comparison", value=True)

plot_df = agg_df.copy()

if use_normalization:
    # Normalize relative to the MAX value found in the *entire dataset* for that stat
    # (Using entire dataset is better so the scale is objective, not just relative to the 3 selected guys)
    for stat in selected_stats:
        max_val = df[stat].max()
        min_val = df[stat].min()
        if max_val != min_val:
            plot_df[stat] = (plot_df[stat] - min_val) / (max_val - min_val)
        else:
            plot_df[stat] = 0.5 # Default if no variance

# --- 5. Render Chart ---

# Melt to long format for Plotly
# [Player, Stat_Name, Value]
melted_df = plot_df.melt(id_vars=player_col, value_vars=selected_stats, var_name='Stat', value_name='Value')

st.subheader("Comparison Chart")

fig = px.line_polar(
    melted_df, 
    r='Value', 
    theta='Stat', 
    color=player_col, 
    line_close=True,
    markers=True,
    title=f"Player Comparison ({agg_method})"
)

# Cosmetic updates
fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 1] if use_normalization else None
        )
    ),
    legend=dict(title=player_col)
)

st.plotly_chart(fig, use_container_width=True)

# --- 6. Raw Data Table ---
with st.expander("View Raw Aggregated Numbers"):
    st.write(agg_df)