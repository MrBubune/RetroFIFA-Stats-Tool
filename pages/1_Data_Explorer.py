import streamlit as st
import pandas as pd
from modules.utils import load_sample_df, preprocess_uploaded_df
from modules.charts import render_chart

st.title("📈 Data Explorer")

# 1. Load Data (Session State Preferred)
if 'explorer_raw_data' in st.session_state and not st.session_state['explorer_raw_data'].empty:
    df = st.session_state['explorer_raw_data']
else:
    uploaded = st.file_uploader("Upload match-level CSV", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
        st.session_state['explorer_raw_data'] = df
    else:
        if st.checkbox("Use sample dataset"):
            df = load_sample_df()
            st.session_state['explorer_raw_data'] = df
        else:
            st.info("Upload a CSV or check 'Use sample dataset'.")
            st.stop()

# Basic cleaning
df = preprocess_uploaded_df(df)

st.sidebar.header("Filters & Sorting")

# Filtering
filter_col = st.sidebar.selectbox("Filter column (optional)", ["None"] + list(df.columns))
if filter_col != "None":
    vals = sorted(df[filter_col].dropna().unique().tolist())
    chosen = st.sidebar.multiselect(f"Pick {filter_col} values", vals, default=vals[:5])
    df = df[df[filter_col].isin(chosen)]

# Numeric range filters
num_cols = df.select_dtypes(include='number').columns.tolist()
# (Optional: Limit numeric filters to avoid sidebar clutter if too many cols)
if num_cols:
    with st.sidebar.expander("Numeric range filters"):
        for c in num_cols:
            col_data = df[c].dropna()
            if col_data.empty: continue
            mn, mx = float(col_data.min()), float(col_data.max())
            if mn == mx: continue
            try:
                lo, hi = st.slider(f"{c}", mn, mx, (mn, mx))
                df = df[(df[c] >= lo) & (df[c] <= hi)]
            except: pass

# Sorting
sort_col = st.sidebar.selectbox("Sort by (optional)", ["None"] + list(df.columns))
if sort_col != "None":
    asc = st.sidebar.checkbox("Ascending", value=False)
    df = df.sort_values(by=sort_col, ascending=asc)

st.subheader("Preview")
st.dataframe(df.head(50))

# --- Chart Controls ---
st.sidebar.header("Chart settings")
lib = st.sidebar.selectbox("Library", ["Plotly", "Altair", "Matplotlib"])

# ADDED "Radar" to the list below
chart = st.sidebar.selectbox("Chart type", [
    "Scatter", "Line", "Bar", "Histogram", "Box", "Violin",
    "Heatmap (corr)", "Area", "Pie", "Parallel Categories", 
    "Radar"
])

# Helper for Radar Charts regarding data shape
if chart == "Radar":
    st.sidebar.info(
        "💡 For standard Radar charts:\n"
        "- **X axis**: Category (e.g., 'Stat Name')\n"
        "- **Y axis**: Value (e.g., 'Count')\n"
        "- **Group**: Color (e.g., 'Player Name')\n"
        "If your data is wide (stats in columns), this will only plot one stat."
    )

x = st.sidebar.selectbox("X axis", ["None"] + list(df.columns))
y = st.sidebar.selectbox("Y axis", ["None"] + list(df.columns))

group_col = None
# Added Radar to the list of charts that accept grouping
if chart in ("Bar", "Pie", "Box", "Violin", "Parallel Categories", "Radar"):
    group_col = st.sidebar.selectbox("Group / Category column (optional)", ["None"] + list(df.columns))
    if group_col == "None": group_col = None

# Render Chart
st.subheader(f"{chart} chart")

# Ensure we don't pass 'None' string to functions
x_val = x if x != "None" else None
y_val = y if y != "None" else None

if df.empty:
    st.warning("No data available with current filters.")
else:
    fig_or_chart = render_chart(df, chart_type=chart, lib=lib, x=x_val, y=y_val, group_col=group_col)

    if fig_or_chart is None:
        st.warning("Could not render chart. Ensure you have selected valid columns for X and Y.")
    else:
        if lib == "Plotly":
            st.plotly_chart(fig_or_chart, use_container_width=True)
        elif lib == "Altair":
            st.altair_chart(fig_or_chart, use_container_width=True)
        else:
            st.pyplot(fig_or_chart, use_container_width=True)