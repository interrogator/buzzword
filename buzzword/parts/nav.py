"""
buzzword: navigation bar
"""

import dash_core_components as dcc
import dash_html_components as html
from buzzword.parts import style

LINKS = [
    ("User guide", "https://buzzword.readthedocs.io/en/latest/guide/"),
    ("Creating corpora", "https://buzzword.readthedocs.io/en/latest/building/"),
    ("Depgrep query syntax", "https://buzzword.readthedocs.io/en/latest/depgrep/"),
    ("About", "https://buzzword.readthedocs.io/en/latest/about/"),
]

hrefs = [html.Li([html.A(name, target="_blank", href=url)]) for name, url in LINKS]

navbar = html.Div(
    [
        html.Img(src="../assets/bolt.jpg", height=42, width=38, style=style.NAV_HEADER),
        dcc.Link("buzzword", href="/", style=style.NAV_HEADER),
        html.Div(html.Ul(hrefs, className="nav navbar-nav"), className="pull-right"),
    ],
    className="navbar navbar-default navbar-static-top",
)
