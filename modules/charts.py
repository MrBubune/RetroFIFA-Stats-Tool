import plotly.express as px
import altair as alt
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

def render_chart(df, chart_type, lib="Plotly", x=None, y=None, group_col=None):
    try:
        if lib == "Plotly":
            return _plotly_chart(df, chart_type, x, y, group_col)
        if lib == "Altair":
            return _altair_chart(df, chart_type, x, y, group_col)
        return _matplotlib_chart(df, chart_type, x, y, group_col)
    except Exception:
        return None

# Plotly implementations
def _plotly_chart(df, chart_type, x, y, group):
    if chart_type == "Scatter":
        if x and y:
            return px.scatter(df, x=x, y=y, color=group)
    if chart_type == "Line":
        if x and y:
            return px.line(df, x=x, y=y, color=group)
    if chart_type == "Bar":
        if x and y:
            if group:
                agg = df.groupby([x, group])[y].mean().reset_index()
                return px.bar(agg, x=x, y=y, color=group)
            return px.bar(df, x=x, y=y)
    if chart_type == "Histogram":
        if x:
            return px.histogram(df, x=x, nbins=30)
    if chart_type == "Box":
        if x and y:
            return px.box(df, x=x, y=y, color=group)
    if chart_type == "Violin":
        if x and y:
            return px.violin(df, x=x, y=y, color=group, box=True)
    if chart_type == "Heatmap (corr)":
        corr = df.select_dtypes(include='number').corr()
        return px.imshow(corr, text_auto=True, aspect="auto", title="Correlation matrix")
    if chart_type == "Area":
        if x and y:
            return px.area(df, x=x, y=y, color=group)
    if chart_type == "Pie":
        if x and y:
            agg = df.groupby(x)[y].sum().reset_index()
            return px.pie(agg, names=x, values=y)
    if chart_type == "Parallel Categories":
        # needs categorical columns
        cats = df.select_dtypes(exclude='number').columns.tolist()[:4]
        if cats:
            return px.parallel_categories(df[cats])
    return px.scatter(df, x=x or df.columns[0], y=y or df.select_dtypes('number').columns[0])

# Altair implementations
def _altair_chart(df, chart_type, x, y, group):
    if chart_type == "Scatter" and x and y:
        return alt.Chart(df).mark_circle(size=60).encode(x=x, y=y, color=group).interactive()
    if chart_type == "Histogram" and x:
        return alt.Chart(df).mark_bar().encode(x=alt.X(x, bin=True), y='count()').interactive()
    if chart_type == "Line" and x and y:
        return alt.Chart(df).mark_line().encode(x=x, y=y, color=group).interactive()
    return alt.Chart(df).mark_point().encode(x=df.columns[0], y=df.select_dtypes('number').columns[0]).interactive()

# Matplotlib / seaborn implementations
def _matplotlib_chart(df, chart_type, x, y, group):
    fig, ax = plt.subplots(figsize=(8,5))
    if chart_type == "Scatter" and x and y:
        sns.scatterplot(data=df, x=x, y=y, hue=group, ax=ax)
    elif chart_type == "Line" and x and y:
        sns.lineplot(data=df, x=x, y=y, hue=group, ax=ax)
    elif chart_type == "Histogram" and x:
        ax.hist(df[x].dropna(), bins=30)
    elif chart_type == "Box" and x and y:
        sns.boxplot(data=df, x=x, y=y, ax=ax)
    elif chart_type == "Heatmap (corr)":
        corr = df.select_dtypes(include='number').corr()
        sns.heatmap(corr, annot=True, ax=ax, cmap="coolwarm")
    else:
        # fallback: simple table plot
        ax.text(0.5,0.5,"No preview", ha="center")
    return fig
