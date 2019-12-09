import plotly.graph_objects as go

CHART_TYPES = {"line", "bar", "heatmap", "area", "stacked_bar"}  # "pie"


def _bar_chart(row):
    return dict(x=list(row.index), y=list(row), type="bar", name=row.name)


def _line_chart(row):
    return go.Scatter(
        x=list(row.index), y=list(row), mode="lines+markers", name=row.name
    )


def _area_chart(row):
    return go.Scatter(
        x=list(row.index),
        y=list(row),
        hoverinfo="x+y",
        mode="lines",
        stackgroup="one",
        name=row.name,
    )


def _heatmap(df):
    return [go.Heatmap(z=df.T.values, x=list(df.index), y=list(df.columns))]


def _df_to_figure(df, kind="bar"):
    """
    Helper to generate charts
    """
    plotters = dict(
        line=_line_chart,
        bar=_bar_chart,
        heatmap=_heatmap,
        area=_area_chart,
        stacked_bar=_bar_chart,
    )
    plotter = plotters[kind]

    datapoints = plotter(df) if kind == "heatmap" else df.T.apply(plotter)

    layout = dict(width=1300)
    if kind == "stacked_bar":
        layout["barmode"] = "stack"
    return dict(data=datapoints, layout=layout)
