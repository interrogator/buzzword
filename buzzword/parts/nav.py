"""
buzzword: navigation bar
"""

import buzzword
import subprocess
import dash_core_components as dcc
import dash_html_components as html
from buzzword.parts import style


def _make_navbar(debug):
    """
    Generate navigation bar. Debug will add version information
    """

    if debug:
        version = buzzword.__version__
        commit = "/usr/bin/git rev-parse --short HEAD"
        commit = subprocess.check_output(commit.split()).decode("utf-8").strip()
        ver_string = "version {}: {}".format(version, commit)
        github = "https://github.com/interrogator/buzzword/tree/" + commit
        git_sty = {**style.NAV_HEADER, **{"fontSize": "12pt", "paddingLeft": "20px"}}

    LINKS = [
        ("User guide", "https://buzzword.readthedocs.io/en/latest/guide/"),
        ("Creating corpora", "https://buzzword.readthedocs.io/en/latest/building/"),
        ("Depgrep query syntax", "https://buzzword.readthedocs.io/en/latest/depgrep/"),
        ("About", "https://buzzword.readthedocs.io/en/latest/about/"),
    ]

    hrefs = [html.Li([html.A(name, target="_blank", href=url)]) for name, url in LINKS]

    components = [
        html.Img(src="../assets/bolt.jpg", height=42, width=38, style=style.NAV_HEADER),
        dcc.Link("buzzword", href="/", style=style.NAV_HEADER),
        html.Div(html.Ul(hrefs, className="nav navbar-nav"), className="pull-right"),
    ]

    if debug:
        ver = html.A(ver_string, target="_blank", href=github, style=git_sty)
        components.insert(2, ver)

    navbar = html.Div(components, className="navbar navbar-default navbar-static-top")
    return navbar
