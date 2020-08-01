<br><br>

# **Über das Projekt**:
### *Impressum/Team*

**Swiss Digital Law Discovery Sdilaw**
**Universität Zürich UZH, Rechtswissenschaftliches Institut, Zentrum für rechtsgeschichtliche Forschung, Rämistrasse 74, 8001 Zürich**

Das Portal wurde konzipiert von Martin Kurz, DAS LIS, vom [Zentrum für rechtsgeschichtliche Forschung RWI UZH](https://www.ius.uzh.ch/de/research/units/zrf/altejuristischebibliothek.html). Ihm obliegt auch die Projektleitung.

Programmierung und Entwicklung der Software *buzzword*: Daniel McDonald, [Science IT/S3IT UZH](https://www.zi.uzh.ch/en/teaching-and-research/science-it/about.html).

Projektsteuerung: Prof. Dr. iur. Andreas Thier, Lehrstuhl für Rechtsgeschichte und Privatrecht und Leiter des Zentrums für rechtsgeschichtliche Forschung RWI UZH, Direktor RWI.

Assistierende Mitarbeiterin: Naomi Toren, MLaw.

Input, Beratung: Matteo Romanello, PhD, Walter Boente, Prof. Dr. iur., Annemieke Romein, PhD, Hanno Menges, MLaw, Antonia Hartmann, MLaw.

Copyright: [Zentrum für rechtsgeschichtliche Forschung RWI UZH.](https://www.ius.uzh.ch/de/research/units/zrf/altejuristischebibliothek.html)

## Kontakt

Fragen, Anregungen und Korrekturen jeglicher Art nimmt jederzeit der Projektleiter, [Martin Kurz](mailto:martin.kurz@rwi.uzh.ch), entgegen. Tel. +41 (0)44 634 57 07

## Projekt

Die Entwicklung des Portals sowie Präsentation und Langzeitarchivierung der kantonalen Gesetzestexte bezweckt vorerst einmal, im digitalen Angebot eine zeitliche Lücke zu schliessen – gegenüber den bestehenden Angeboten der SSRQ (*Sammlung Schweizerischer Rechtsquellen*, bis 1798) sowie der für das 20. und 21. Jahrhundert bestehenden Online-Angebote. In Zukunft wird der digitale Corpus laufend mit Kodifikationen, weiteren Gesetzesmaterialien sowie relevanten ausländischen Gesetzen ergänzt – *Sdilaw transnational*.

Das Vorprojekt und die Entwicklung des Prototyps wurde unterstützt von der [Rechts-wissenschaftlichen Fakultät RWF der Universität Zürich](https://www.ius.uzh.ch/de.html), wofür wir uns herzlich bedanken.  

### Methoden, Technik

Wie auf der Startseite erwähnt wird neu ein computerlinguistisches Tool ([*spaCy*](https://spacy.io)/[*buzz*](https://buzz.readthedocs.io/en/latest/)) auf Gesetzestexte angewendet. Es handelt sich um ein Open-source-Tool, welches für Browser-basierte Analyse von Texten hergestellt wurde. Für das Framework der Website wurde [Django](https://www.djangoproject.com/) verwendet. Um Korrekturen an den Transkriptionen zu hinterlegen, wird [Martor](https://github.com/agusmakmun/django-markdown-editor) eingesetzt. 

Das erste Sample von drei Gesetzessammlungen des Kantons Basel Stadt aus dem 19. Jahrhundert wurde vom Digitalisierungszentrum der ZB Zürich gescannt und Bilder im Format TIFF hergestellt. Anschliessend werden die Scans einem Transkriptionsprozess unterzogen mithilfe der HTR-Software [Transkribus](https://transkribus.eu/Transkribus/) (mit Einsatz von künstlichen neuronalen Netzen) sowie parallel zum Vergleich mithilfe [Tesseract](https://opensource.google/projects/tesseract). Die Texterkennung wird weiter verfeinert, nicht zuletzt auch durch das Korrektur-Interface, das die Benutzer des Webtools dazu verwenden können.

Dann wird der Text computerlinguistisch einem Parsingprozess unterzogen. Dabei wird der Text mittels eines Algorithmus einer automatisierten Analyse der Satzstruktur gemäss natürlicher Sprache ausgesetzt, was auch semantische Erschliessung miteinbezieht. 

Des weiteren ist die Anwendung von TEI-Tagging eingeplant, das zumindest teilweise manuell erfolgt und die automatische Analyse ergänzt. Ausserdem wird ein kontrolliertes Vokabular entwickelt werden, das die Abfrage unterstützt.

### Ziel

*Sdilaw* ermöglicht Recherchen innerhalb dieses neu digital erschlossenen geographischen wie zeitlichen Raumes, mittels einer mehrfach optimierten Suche und corpuslinguistischen     Queries, mit anschliessender Weiterverarbeitung der Resultate als Stichworte-im-Zusammenhang (*Keywords in Context*) und interaktiven Wortfrequenzdiagrammen.

*An wen richten wir uns?* Rechtshistoriker, rechtsvergleichend arbeitende Iuristen, Rechtslinguisten, Historiker, auch Sozial- und Wirtschaftsgeschichte, dann die Rechtspraxis sowie alle an Gesetzen Interessierten. 
