import streamlit as st
import pandas as pd
from modules.utils import load_sample_df, preprocess_uploaded_df
from modules.charts import render_chart
from io import StringIO

st.title("📈 Data Explorer")

# upload or sample
uploaded = st.file_uploader("Upload match-level CSV", type=["csv"])
if uploaded:
    df = pd.read_csv(uploaded)
else:
    if st.checkbox("Use sample dataset"):
        df = load_sample_df()
    else:
        st.info("Upload a CSV or check 'Use sample dataset'.")
        st.stop()

# basic cleaning
df = preprocess_uploaded_df(df)

st.sidebar.header("Filters & Sorting")

# filtering
filter_col = st.sidebar.selectbox("Filter column (optional)", ["None"] + list(df.columns))
if filter_col != "None":
    vals = sorted(df[filter_col].dropna().unique().tolist())
    chosen = st.sidebar.multiselect(f"Pick {filter_col} values", vals, default=vals[:5])
    df = df[df[filter_col].isin(chosen)]

# numeric range filters
num_cols = df.select_dtypes(include='number').columns.tolist()
if num_cols:
    st.sidebar.subheader("Numeric range filters")
    for c in num_cols:
        mn = float(df[c].min())
        mx = float(df[c].max())
        lo, hi = st.sidebar.slider(f"{c}", mn, mx, (mn, mx))
        df = df[(df[c] >= lo) & (df[c] <= hi)]

# sorting
sort_col = st.sidebar.selectbox("Sort by (optional)", ["None"] + list(df.columns))
if sort_col != "None":
    asc = st.sidebar.checkbox("Ascending", value=False)
    df = df.sort_values(by=sort_col, ascending=asc)

st.subheader("Preview")
st.dataframe(df.head(50))

# chart controls
st.sidebar.header("Chart settings")
lib = st.sidebar.selectbox("Library", ["Plotly", "Altair", "Matplotlib"])
chart = st.sidebar.selectbox("Chart type", [
    "Scatter", "Line", "Bar", "Histogram", "Box", "Violin",
    "Heatmap (corr)", "Area", "Pie", "Parallel Categories"
])
x = st.sidebar.selectbox("X axis", ["None"] + list(df.columns))
y = st.sidebar.selectbox("Y axis", ["None"] + list(df.columns))

group_col = None
if chart in ("Bar", "Pie", "Box", "Violin", "Parallel Categories"):
    group_col = st.sidebar.selectbox("Group / Category column (optional)", ["None"] + list(df.columns))
    if group_col == "None":
        group_col = None

# render chart
st.subheader(f"{chart} chart")
fig_or_chart = render_chart(df, chart_type=chart, lib=lib, x=x if x!="None" else None,
                            y=y if y!="None" else None, group_col=group_col)
if fig_or_chart is None:
    st.warning("Could not render chart with current selection. Try different columns.")
else:
    if lib == "Plotly":
        st.plotly_chart(fig_or_chart, use_container_width=True)
    elif lib == "Altair":
        st.altair_chart(fig_or_chart, use_container_width=True)
    else:
        st.pyplot(fig_or_chart, use_container_width=True)

# show limited table
st.subheader("Filtered rows (first 200)")
st.dataframe(df.head(200))
