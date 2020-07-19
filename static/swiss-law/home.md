<br><br>

# Swiss Digital Law Discovery (**Sdilaw**)

*Inwiefern kann *Sdilaw* für Sie nützlich sein?*

* Sind Sie an Gesetzesmaterialien der Schweizer Kantone interessiert, die Sie zum grössten Teil bisher nicht digital vorgefunden haben?
* Stellen Sie sich transkantonale oder gar transnationale Forschungsfragen?
* Möchten Sie Comparative Legal History betreiben?
* Oder rechtsdogmatischen Fragen nachgehen?
* Oder der Wirkungsgeschichte oder Vorgeschichte von Gesetzen?
* Möchten Sie neben der Suche und dem Browsen in den Texten weitere computerbasierte Analysen vornehmen können? d.h. Sie sind an Corpus- oder Computerlinguistik interessiert.
* Wären das Visualisieren und das Parsen von Text für Sie eine spannende Option?
* Oder möchten Sie die Frequenz eines Begriffes dargestellt bekommen? 
* Oder würde es Sie über die blosse Anzeige eines Suchbegriffes hinaus interessieren, in welchem Zusammenhang dieser jeweils vorkommt? (Keyword-in-context)

**Die Plattform *SdiLaw* bietet Ihnen all dies.**

Sie ist auch besonders geeignet für interdisziplinäre respektive kollaborative digitale Projekte, wie sie z.B. im Zusammenhang der Digital Humanities oder der Digital (Legal) History vorkommen. Wenn Sie im Rahmen der Rechtsprechung respektive Rechtsanwendung rechtsvergleichend und die  historische Tiefenperspektive miteinbeziehen möchten, da kann *Sdilaw* ideal zum Zug kommen. 
 
Nicht zu vergessen sind die Möglichkeiten, die Sie durch das Hinzufügen von eigenen Datensets haben, die Sie separat oder im Zusammenhang mit den angebotenen Materialien durchsuchen oder digital analysieren können. 

Das Portal ist als ausbaubares konzipiert. Es wird laufend erweitert mit Gesetzestexten über die Landesgrenzen hinaus sowie mit innerschweizerischen Materialien, die zu den Gesetzestexten in Verbindung gesetzt werden können, wie z.B. Ratsprotokolle. Es können auch neue nützliche Features und Interfaces implementiert werden.

Wir bieten Ihnen mit dem Portal *Sdilaw* Swiss Digital Law Discovery und der Software [*buzzword*](https://github.com/interrogator/buzzword) einen möglichst idealen Ausgangspunkt, den wir kontinuierlich optimieren und uns über jedwede Rückmeldung, Anregung oder Meldung von Fehlern freuen. Es handelt sich um ein agil konzipiertes Portal, das jederzeit den Bedürfnissen seiner Benutzer angepasst werden kann.

Ob das Ausgangsinteresse eine nicht-digitale (rechts)geschichtliche Fragestellung ist oder eine Erwartung hinsichtlich digital gesteuerter Forschung oder bloss ein vages Forschungsinteresse bezüglich den hier angebotenen Textdaten besteht, wir denken, dass alle diese Ausgangspunkte zielführend sind. Sie verhalten sich zueinander komplementär im Verlaufe eines iterativen Vorgehens.

Swiss Digital Law Discovery ist also ein Webtool (Frontend) für die Suche und Analyse von Textdateien, hier abgestimmt auf Gesetzesmaterialien und ihre Kontexte. Es verwendet corpus- respektive computerlinguistische Methoden und wurde mit [*buzz*](https://github.com/interrogator/buzz) als Backend sowie [*buzzword*](https://github.com/interrogator/buzzword) als Frontend erstellt. Die Text-
erkennung wird grösstenteils mit der Software [*Transkribus*](https://transkribus.eu/Transkribus/) vorgenommen, welche auf Machine Learning basiert – einem Teilgebiet der Artificial Intelligence (AI). Es handelt sich um einen selbstanpassenden Algorithmus, der künstliche neuronale Netze verwendet. Alternativ kommt als Texterkennungssoftware [*Tesseract OCR*](https://github.com/tesseract-ocr/tesseract) zum Einsatz.

*Sdilaw* ermöglicht neben dem Durchsuchen und Visualisieren das Parsen von Text. 
Beim Parsen wird der Text mittels eines Algorithmus einer automatisierten Analyse der Satzstruktur gemäss natürlicher Sprache unterzogen. Dabei werden auch Wortbedeutungen, d.h. semantische Zusammenhänge erschlossen. 

## Wie gehen Sie vor?

Bei *Sdilaw* haben Sie zwei Hauptoptionen – zu finden je auf einer Unterseite:
eine Startseite, bei der Sie einen präsentierten Text auswählen (*search from dataset*) oder einfach in den vorhandenen Texten suchen, browsen und lesen können.$

Auf der Forschungs- oder Explore-Seite haben Sie folgende Optionen:

1. Suche
2. Erstellung von Tabellen, die die Häufigkeit von Begriffen anzeigen (Frequenz-Ansicht)
3. Visualisierung von Resultaten
4. Konkordanzen, d.h. Kookkurrenzen, erstellen, wobei die direkte Umgebung vor und nach einem Wort/Begriff angezeigt wird (Keyword-in-context).

## Zur Startseite

Auf der Hauptseite kann durch Anklicken des Namens eines Textes/Bandes dieser dann durchblättert werden.
Auch hier könnten eigene Texte/Dateien hochgeladen und wie die auf der Webseite vorzufindenden (Gesetzes-)Texte behandelt werden. 

## Explorationsseite

Nach dem Hochladen oder Auswählen eines Textkorpus können Sie über die Explorationsseite zur Schnittstelle gelangen, wo Sie entweder die Dataset-Ansicht wählen oder die vorher erstellten Suchresultate weiter verarbeiten können.

### Dataset-Ansicht

Der ausgewählte Text(korpus) kann mit allen Sprach- und Metadatenmerkmalen betrachtet werden. Es handelt sich um eine interaktive Tabelle. Hier können Sie Textteile filtern, sortieren oder herausnehmen, was natürlich den hinterlegten Originaltext nicht tangiert. Interessant ist die Suchfunktion, womit nach Eingabe eines Begriffes eine Teilmenge von (Text)Daten gebildet wird. Die Teilmenge kann weiter durchsucht oder konkordanziert werden. Bei der Konkordanz sehen Sie die direkte Umgebung vor und nach dem gesuchten Begriff im Text, was Ihnen den Zusammenhang des Begriffes erschliesst. 

### Suche in Textauswahl (Dataset-Ansicht)

Im Dropdown-Menu links wählen Sie zuerst die Art des Begriffes aus, nach dem Sie suchen: 

* Wort(form)
* Lemma
* Part-of-Speech (Wortart gemäss Grammatik)
* usw.

Bei Wahl von «Wort» wird im unbearbeiteten Text Ihre Wortsuchanfrage verglichen mit dem Wort, wie es im originalen, unbearbeiteten Text vorkommt.

### Sucheingabe (*Query Entry*)

Dabei können Sie einen sog. Regulären Ausdruck (regular expression, Abkürzung regex) eingeben – unter Berücksichtigung der Gross- und Kleinschreibung (siehe dazu Wikipedia: «Regulärer Ausdruck»).

## Frequenzansicht (*Frequencies View*)

Bei *buzzword* wird auf neuartige Weise der Prozess des Suchens von der Ansicht der Resultate getrennt. So können Sie mit Resultaten weiterarbeiten und sie unterschiedlich darstellen, ohne dass eine Suche nochmals gestartet werden muss. Von einem Suchresultat, generiert in der Dataset-Ansicht, können Sie verschiedene Ansichten erstellen: Tabellen, Visualisierungen, Konkordanzen.

### Tabellen-Ansicht

1. Wählen Sie zuerst einen Text/Dataset aus – beim Dropdown-Menu «Suche aus» («search from»).
Daraus werden die Kalkulationen erstellt. 
2. Dann gilt es die Spalten der Tabelle zu wählen, z.B. «Wort» («word») und «Wortklasse» («wordclass»). Die Resultate sehen Sie wie im folgenden Beispiel: «happy/adj.».
3. Nach der Auswahl der Spalte wählen Sie ein Merkmal (feature), das als Index der Tabelle dienen soll.
Z.B. «Lemma nach Sprecher».
4. Die Tabelle kann im Anschluss daran noch sortiert werden – auf- oder absteigend.

## Visualisierung der Tabellen-Ansicht

Wählen Sie den Diagrammtyp, die Anzahl Elemente, und ob Sie die Zeilen und Spalten invertieren wollen oder nicht. Die nun entstandenen Diagramme sind sogar interaktiv, d.h. Sie können mit den verfügbaren Tools die Grafiken unterschiedlich erstellen. Die Visualisierungen können für die Verwendung ausserhalb des Portals auf einer Festplatte (Laufwerk) gesichert werden. 

## Konkordanz-Ansicht (*Keyword-in-context*)

«Stichwörter im Kontext» oder Konkordanzen ermöglichen nicht nur die Anzeige von den gesuchten Stichwörtern als solchen, sondern hier werden die Stichwörter zusammen mit dem 
Text vor- oder nachher angezeigt. Über den Reiter «Konkordanz» (concordance) können Sie also das Resultat einer Suche als «Stichwörter im Kontext» anzeigen lassen. 

Vorgehen: Suchresultat selektionieren über «Suche von» (search from) im Dropdown-Menu. Dabei haben Sie verschiedene Kombinationen zur Auswahl, z.B. Wort/Part-of-Speech.

## Über uns

Das Portal *Swiss Digital Law* wird in Kürze online gestellt und von der Universität Zürich UZH gehostet sowie vom Zentrum für rechtsgeschichtliche Forschung ZRF betreut werden, Projektsteuerung Prof. Andreas Thier, Projektleitung Martin Kurz, Softwareengineering [Daniel McDonald](https://twitter.com/interro_gator).

Auf Ihre Rückmeldungen und Fragen sind wir gespannt. Bitte hinterlassen Sie diese als Issue auf dem [Repositorium des Projekts](https://github.com/interrogator/buzzword) (github) oder per [E-Mail](mailto:martin.kurz@uzh.ch). *Besten Dank!*
