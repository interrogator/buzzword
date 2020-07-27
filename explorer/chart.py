import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go

CHART_TYPES = {
    "line",
    "bar",
    "heatmap",
    "area",
    "stacked_bar",
    "distplot",
    "stacked_distplot",
}  # "pie"


def _bar_chart(row):
    if row.index.name == "year":
        index = [f"{y}" for y in row.index]
    else:
        index = list(row.index)
    return dict(x=index, y=list(row), type="bar", name=str(row.name))


def _line_chart(row):
    return go.Scatter(
        x=list(row.index), y=list(row), mode="lines+markers", name=str(row.name)
    )


def _area_chart(row):
    return go.Scatter(
        x=list(row.index),
        y=list(row),
        hoverinfo="x+y",
        mode="lines",
        stackgroup="one",
        name=str(row.name),
    )


def _distplot(df):
    data = df.T.values
    labels = [str(i) for i in df.columns]
    result = ff.create_distplot(data, labels)
    return result["data"], result["layout"]


def _heatmap(df):
    # todo: better interpolation handling
    cols = [str(i) for i in df.columns]
    if df.columns.names and df.columns.names[0] == "year":
        cols = [f"year: {y}" for y in cols]
    index = [str(i) for i in df.index.values]
    if df.index.names and df.index.names[0] == "year":
        index = [f"year: {y}" for y in index]
    return [go.Heatmap(z=df.T.values, x=index, y=cols)]


def _df_to_figure(df, kind="bar", width=1300):
    """
    Helper to generate charts
    """
    plotters = dict(
        line=_line_chart,
        bar=_bar_chart,
        heatmap=_heatmap,
        area=_area_chart,
        stacked_bar=_bar_chart,
        distplot=_distplot,
        stacked_distplot=_distplot,
    )
    plotter = plotters[kind]

    layout = {}
    if kind == "heatmap":
        datapoints = plotter(df)
    elif kind.endswith("distplot"):
        datapoints, layout = plotter(df)
    else:
        if df.index.name == "year":
            df = df.copy()
            df.index = pd.to_datetime(df.index, format='%Y')
        datapoints = df.apply(plotter)

    layout["width"] = width
    # layout["height"] = 600
    layout["margin"] = {"t": 40}

    if kind.startswith("stacked"):
        layout["barmode"] = "stack"

    if df.index.name == "year":
        layout["xaxis"] = {"tickformat": "%Y", "tickvals": list(df.index)}


    return dict(data=datapoints, layout=layout)
