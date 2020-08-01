"""
english-german translations for explorer are stored in this file.

The dict structure is {(component-id, component-property): [eng-text, de-text]}.
If the component-property is none, this means that the component-id isn't really
an html id, and the language switch needs to be coded another way.
"""


LANGUAGES = {
    ("dataset-tab-label", "label"): ["DATASET", "Datensätze".upper()],
    ("freq-tab-label", "label"): ["FREQUENCIES", "Frequenzen".upper()],
    ("chart-tab-label", "label"): ["CHART", "Diagramm".upper()],
    ("conc-tab-label", "label"): ["CONCORDANCE", "Begriff und seine Umgebung".upper()],
    ("table-button", "children"): ["Generate table", "Tabelle erstellen"],
    ("relative-for-table", "placeholder"): ["Relative/keyness calculation", "Relativ/Schlüssigkeit Berechnung"],
    ("subcorpora-for-table", "placeholder"): ["Features for index", "Merkmal für Index"],
    ("sort-for-table", "placeholder"): ["Sort columns by...", "Spalten sortieren nach"],
    ("show-for-table", "placeholder"): ["Features to show", "anzuzeigende Attribute"],
    ("clear-history", "children"): ["CLEAR HISTORY", "Verlauf löschen".upper()],
    #("regex-text", "children"): ["exact match", "genaue Übereinstimmung"],  # not working because used in another output
    #("input-box", "placeholder"): ["Enter search query...", "Suchabfrage eingeben..."],
    ("search-default", None): ["Search entire corpus: ", "Durchsuche den gesamten Korpus"],
    ("show-this-dataset", "children"): ["SHOW", "anzeigen".upper()],
    ("update-conc", "children"): ["UPDATE", "aktualisieren".upper()],
    ("figure-button-1", "children"): ["UPDATE", "aktualisieren".upper()],
    ("figure-button-2", "children"): ["UPDATE", "aktualisieren".upper()],
    ("figure-button-3", "children"): ["UPDATE", "aktualisieren".upper()],
    ("figure-button-4", "children"): ["UPDATE", "aktualisieren".upper()],
    ("figure-button-5", "children"): ["UPDATE", "aktualisieren".upper()],
    ("show-for-conc", "placeholder"): ["Features to show", "anzuzeigende Attribute"],
    ("search-button", "children"): ["SEARCH", "SUCHE"],
    #("chart-num-1", "children"): ["Chart # 1", "Diagramm 1"],  # bug in dash makes these not work
    #("chart-num-2", "children"): ["Chart # 2", "Diagramm 2"],  # bug in dash makes these not work
    #("chart-num-3", "children"): ["Chart # 3", "Diagramm 3"],  # bug in dash makes these not work
    #("chart-num-4", "children"): ["Chart # 4", "Diagramm 4"],  # bug in dash makes these not work
    #("chart-num-5", "children"): ["Chart # 5", "Diagramm 5"],  # bug in dash makes these not work
    #("component-name", "field"): ["en", "de"],
    #("component-name", "field"): ["en", "de"],
    #("component-name", "field"): ["en", "de"],
}
