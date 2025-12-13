import plotly.express as px
import altair as alt
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import streamlit as st

def render_chart(df, chart_type, lib="Plotly", x=None, y=None, group_col=None):
    """
    Renders a chart based on the selected library and chart type.
    Returns a Figure object (Plotly/Matplotlib) or Altair Chart object.
    """
    try:
        if lib == "Plotly":
            return _plotly_chart(df, chart_type, x, y, group_col)
        if lib == "Altair":
            return _altair_chart(df, chart_type, x, y, group_col)
        return _matplotlib_chart(df, chart_type, x, y, group_col)
    except Exception as e:
        st.error(f"Error rendering chart: {e}")
        return None

# --- Plotly Implementation ---
def _plotly_chart(df, chart_type, x, y, group):
    if chart_type == "Scatter":
        if x and y:
            return px.scatter(df, x=x, y=y, color=group, hover_data=df.columns)
            
    if chart_type == "Line":
        if x and y:
            # Sort by X usually makes sense for lines (e.g. Dates)
            d_sorted = df.sort_values(x)
            return px.line(d_sorted, x=x, y=y, color=group)
            
    if chart_type == "Bar":
        if x and y:
            # Aggregate if multiple rows per X exist to avoid stacking distinct rows weirdly
            if group:
                agg = df.groupby([x, group])[y].mean().reset_index()
                return px.bar(agg, x=x, y=y, color=group, title=f"Average {y} by {x}")
            else:
                agg = df.groupby(x)[y].mean().reset_index()
                return px.bar(agg, x=x, y=y, title=f"Average {y} by {x}")
                
    if chart_type == "Histogram":
        if x:
            return px.histogram(df, x=x, color=group, nbins=30, barmode="overlay")
            
    if chart_type == "Box":
        if y: # Box usually needs a generic Y (numeric), X is optional (category)
            return px.box(df, x=x, y=y, color=group)
            
    if chart_type == "Violin":
        if y:
            return px.violin(df, x=x, y=y, color=group, box=True)
            
    if chart_type == "Heatmap (corr)":
        # Ignore X/Y selection, compute whole df correlation
        corr = df.select_dtypes(include='number').corr()
        return px.imshow(corr, text_auto=True, aspect="auto", 
                         title="Correlation Matrix (Numeric Columns)",
                         color_continuous_scale='RdBu_r', zmin=-1, zmax=1)
                         
    if chart_type == "Area":
        if x and y:
            return px.area(df, x=x, y=y, color=group)
            
    if chart_type == "Pie":
        if x: # X is the category names
            # If Y is provided, sum it. If not, Count X.
            if y:
                agg = df.groupby(x)[y].sum().reset_index()
                return px.pie(agg, names=x, values=y, title=f"Total {y} by {x}")
            else:
                return px.pie(df, names=x, title=f"Distribution of {x}")

    if chart_type == "Parallel Categories":
        # Auto-select up to 5 categorical columns if X/Y not relevant
        cats = df.select_dtypes(include=['object', 'category']).columns.tolist()
        if len(cats) > 5: cats = cats[:5]
        return px.parallel_categories(df, dimensions=cats, color=group)

    if chart_type == "Radar":
        if x and y:
            # Radar needs aggregation to work cleanly
            # X = Categories (Theta), Y = Values (R), Group = Color
            if group:
                agg = df.groupby([group, x])[y].mean().reset_index()
                return px.line_polar(agg, r=y, theta=x, color=group, line_close=True,
                                     title=f"Radar: Avg {y} by {x}")
            else:
                agg = df.groupby(x)[y].mean().reset_index()
                return px.line_polar(agg, r=y, theta=x, line_close=True,
                                     title=f"Radar: Avg {y} by {x}")
    
    return None

# --- Altair Implementation ---
def _altair_chart(df, chart_type, x, y, group):
    # Altair needs column names, not None
    if not x or not y:
        return None

    base = alt.Chart(df)
    
    if chart_type == "Scatter":
        return base.mark_circle(size=60).encode(
            x=x, y=y, 
            color=group if group else alt.value("steelblue"),
            tooltip=list(df.columns)
        ).interactive()
        
    if chart_type == "Bar":
        return base.mark_bar().encode(
            x=x, y=f"mean({y})", # Aggregation is easy in Altair string syntax
            color=group if group else alt.value("steelblue"),
            tooltip=[x, f"mean({y})"]
        ).interactive()

    if chart_type == "Line":
        return base.mark_line().encode(
            x=x, y=y, 
            color=group if group else alt.value("steelblue")
        ).interactive()
        
    if chart_type == "Histogram":
        # For histogram, X is the binning field, Y is count
        return base.mark_bar().encode(
            x=alt.X(x, bin=True), 
            y='count()',
            color=group if group else alt.value("steelblue")
        ).interactive()

    if chart_type == "Box":
        return base.mark_boxplot().encode(
            x=x, y=y,
            color=group if group else alt.value("steelblue")
        ).interactive()

    if chart_type == "Radar":
        st.warning("Radar charts are not natively supported in the Altair helper yet. Please switch to Plotly.")
        return None

    return None

# --- Matplotlib / Seaborn Implementation ---
def _matplotlib_chart(df, chart_type, x, y, group):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if chart_type == "Radar":
        ax.text(0.5, 0.5, "Radar chart not implemented for Matplotlib.\nUse Plotly.", 
                ha='center', va='center')
        return fig

    if chart_type == "Scatter" and x and y:
        sns.scatterplot(data=df, x=x, y=y, hue=group, ax=ax)
        
    elif chart_type == "Line" and x and y:
        sns.lineplot(data=df, x=x, y=y, hue=group, ax=ax)
        
    elif chart_type == "Bar" and x and y:
        # Seaborn barplot automatically aggregates (mean) with error bars
        sns.barplot(data=df, x=x, y=y, hue=group, ax=ax)
        
    elif chart_type == "Histogram" and x:
        sns.histplot(data=df, x=x, hue=group, kde=True, ax=ax)
        
    elif chart_type == "Box" and x and y:
        sns.boxplot(data=df, x=x, y=y, hue=group, ax=ax)
        
    elif chart_type == "Violin" and x and y:
        sns.violinplot(data=df, x=x, y=y, hue=group, ax=ax)
        
    elif chart_type == "Heatmap (corr)":
        corr = df.select_dtypes(include='number').corr()
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
        
    else:
        ax.text(0.5, 0.5, "Chart type/Axis combination not supported for Matplotlib", ha="center")
        
    plt.tight_layout()
    return fig