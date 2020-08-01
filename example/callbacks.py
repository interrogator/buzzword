from django.conf import settings
from dash.dependencies import Input, Output, State
from explorer.helpers import _get_corpus
from explorer.chart import _df_to_figure
import dash_core_components as dcc
import dash_html_components as html


def add_callbacks(app, slug, _quick_concordance, _quick_freq):

    @app.expanded_callback(
        [Output("example-conc", "columns"), Output("example-conc", "data")],
        [Input("do-conc", "n_clicks")],
        [State("conc-query-string", "value")],
    )
    def _simple_concordance(do_conc, query, **kwargs):
        if not do_conc:
            return no_update, no_update
        try:
            corpus = _get_corpus(slug)
        # migrate handling
        except TypeError:
            return [], []
        columns, data = _quick_concordance(corpus, query.strip())
        return columns, data


    @app.expanded_callback(
        [Output("example-freq", "columns"), Output("example-freq", "data")],
        [Input("example-wordclass-dropdown", "value")],
        [],
    )
    def _simple_freq(wordclass, **kwargs):
        from time import sleep
        if not wordclass:
            return no_update
        sleep(2)
        try:
            corpus = _get_corpus(slug)
        # migrate handling
        except TypeError:
            return [], []
        _, columns, data = _quick_freq(corpus, wordclass=wordclass)
        return columns, data


    @app.expanded_callback(
        Output("chart-holder-1", "children"),
        [Input("figure-button-1", "n_clicks")],
        [
            State("chart-type-1", "value"),
            State("chart-top-n-1", "value"),
            State("chart-transpose-1", "on"),
            State("example-wordclass-dropdown", "value"),
        ],
    )
    def _new_chart(
        n_clicks, chart_type, top_n, transpose, wordclass, **kwargs,
    ):
        """
        Make new chart by kind. Do it 5 times, once for each chart space
        """
        # before anything is loaded, do nothing
        if n_clicks is None:
            return no_update

        try:
            corpus = _get_corpus(slug)
        # migrate handling
        except TypeError:
            return [], []

        df, _, _ = _quick_freq(corpus, wordclass=wordclass)

        # transpose and cut down items to plot
        if transpose:
            df = df.T
        df = df.iloc[:, :top_n]

        # generate chart
        figure = _df_to_figure(df, kind=chart_type, width="100%")
        chart_data = dict(id="chart-1", figure=figure, style=dict(width="100%", height="400px"),)
        chart = dcc.Graph(**chart_data)
        return chart

    return app
