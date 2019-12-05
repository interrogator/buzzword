"""
buzzword explorer: collection of reusable CSS styles
"""

FRONT = {'position': 'relative', 'zIndex': '999'}
NEAR_FRONT = {'position': 'relative', 'zIndex': '900'}
VERTICAL_MARGINS = {"marginBottom": 15, "marginTop": 15}
HORIZONTAL_PAD_5 = {"paddingLeft": 5, "paddingRight": 5}
CELL_MIDDLE_35 = {"display": "table-cell", "verticalAlign": "middle", "height": "35px"}
BLOCK_MIDDLE_35 = {
    "display": "inline-block",
    "verticalAlign": "middle",
    "height": "35px",
}
BLOCK = {
    "display": "inline-block",
    "verticalAlign": "middle",
    "height": "35px",
    "paddingLeft": "5px",
    "paddingRight": "5px",
}
INLINE = {"display": "inline-block", "paddingLeft": "5px", "paddingRight": "5px"}
NAV_HEADER = {
    "display": "inline-block",
    "verticalAlign": "middle",
    "color": "#555555",
    "textDecoration": "none",
    "fontSize": 32,
    "paddingTop": "12px",
}
TSTYLE = {**CELL_MIDDLE_35, **{"width": "25%", "display": "inline-block"}}
MARGIN_5_MONO = {"marginLeft": 5, "marginRight": 5, "fontFamily": "monospace"}
BOLD_DARK = {"fontWeight": "bold", "color": "#555555"}
CHART_SUMMARY = {
    "fontWeight": "bold",
    "fontSize": "11pt",
    "paddingBottom": "10px",
    "paddingTop": "10px",
    **BOLD_DARK,
}
STRIPES = [{"if": {"row_index": "odd"}, "backgroundColor": "rgb(248, 248, 248)"}]
LEFT_ALIGN = [
    {"if": {"column_id": c}, "textAlign": "left", "paddingLeft": "5px"}
    for c in ["file", "w", "l", "x", "p", "f", "speaker", "setting"]
]
LEFT_ALIGN_CONC = [
    {"if": {"column_id": c}, "textAlign": "left", "paddingLeft": "5px"}
    for c in ["file", "match", "right", "speaker", "setting"]
]
FILE_INDEX = {
    "if": {"column_id": "file"},
    "backgroundColor": "#fafafa",
    "color": "#555555",
    "fontWeight": "bold",
    "width": "20%"
}
INDEX = [
    {
        "if": {"column_id": c},
        "backgroundColor": "#fafafa",
        "color": "#555555",
        "fontWeight": "bold",
    }
    for c in ["file", "s", "i"]
]
CONC_LMR = [
    {"if": {"column_id": "match"}, "fontWeight": "bold", "width": "140px"},
    {
        "if": {"column_id": "left"},
        "whiteSpace": "no-wrap",
        "overflow": "hidden",
        "textOverflow": "ellipsis",
        "width": "35%",
        "maxWidth": 0,
        "direction": "rtl",
    },
    {
        "if": {"column_id": "right"},
        "whiteSpace": "no-wrap",
        "overflow": "hidden",
        "textOverflow": "ellipsis",
        "width": "35%",
        "maxWidth": 0,
    },
]
