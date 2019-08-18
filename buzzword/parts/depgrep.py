import dash_core_components as dcc
import dash_html_components as html
from buzzword.parts.nav import navbar
import os
import buzzword

root = os.path.dirname(os.path.dirname(buzzword.__file__))

with open(os.path.join(root, "docs/depgrep.md"), "r") as fo:
    text = fo.read()

layout = html.Div([navbar, dcc.Markdown(className="documentation", children=text)])
