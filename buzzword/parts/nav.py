import dash_core_components as dcc
import dash_html_components as html
from buzzword.parts import style

LINKS = [
    ("User guide", "https://buzzword.readthedocs.io/en/latest/guide/"),
    ("Creating corpora", "https://buzzword.readthedocs.io/en/latest/building/"),
    ("Depgrep query syntax", "https://buzzword.readthedocs.io/en/latest/depgrep/"),
    ("About", "https://buzzword.readthedocs.io/en/latest/about/"),
]

navbar = html.Div(
    [
        html.Img(
            src="../assets/bolt.jpg", height=42, width=38, style=style.BLOCK_MIDDLE_35
        ),
        dcc.Link("buzzword", href="/", style=style.NAV_HEADER),
        html.Div(
            html.Ul(
                [
                    html.Li([html.A(name, target="_blank", href=url)])
                    for name, url in LINKS
                ],
                className="nav navbar-nav",
            ),
            className="pull-right",
        ),
    ],
    className="navbar navbar-default navbar-static-top",
)
