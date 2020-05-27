# Guidelines for correcting the dataset

The dataset has undergone automatic Optical Character Recognition (OCR), customised for Fraktur script. This works well, but numerous inconsistencies remain.

The goal of making the corrections is to make a digitised version of the dataset that is as consistent as possible, so that it may be processed further with natural language processing tools, and the results analysed.

For this to work, corrections need to follow a set of guidelines. These are laid out below.

## Spelling errors

Spelling errors should simply be corrected, wherever possible.

## Non-standard spelling

If the source text has a non-standard or outdated spelling, you can correct to its modern equivalent.

## Line breaks

If a word is broken over two lines by a hyphen, this can remain so in the corrected version. However, the first line *must* end with a hyphen character. If no word is broken across lines, you can leave the text as is.

## Headings

Use markdown heading syntax (prefacing lines with `#` for first-level, `##` for second-level headings)

You can hit the Preview button to see that your headings are recognised.

## Non-alphanumeric content

Vertical and horizontal lines are not to be represented in the corrections

## Section titles

At the top of pages, sometimes the current section title is printed. This should be handled as a second-level header:

## Page numbers

Can be removed, or turned into metadata with a first line reading:

> `<meta page=6/>`

For page numbers in tables of contents, see below.

## Tables of contents

Tables of contents (TOC) do not provide much value to us, so do not assign them much priority. However, the best way to handle a TOC is to use the following representation for each section and its accompanying page number(s):

> <meta representation="toc">Section text here (page-number)></meta>

## Bold and italic text

If text appears to be bold or italic in the source texts, you can represent this using standard markdown asterisk syntax. Surround a word with an asterisk on each side for italics, and two asterisks on each side for bold.

You can hit the Preview button to see that your italics and markdown match the source tet.

## Blank pages

If a page has no text, the ideal text to enter is:

```
<meta blank="true"/>
```

This helps us be sure that content was not accidentally deleted from a page.

## Misc. chracters and symbols

Sometimes, the parser interprets a spot on a page as a letter or number. When this has happened, simply delete the unwanted characters.

## Tables or figures

If legible sentence-like text can be extracted from a table, you can include it in the correction like this:

<meta representation="table">Text within table here</meta>

Do not try to copy the layout of the table; we are only interested in any sentence-like text it contains.

If legible sentence-like text can be extracted from a figure, you can include it in the correction like this:

<meta representation="figure">Text of figure here</meta>

## Adding searchable metadata

By using the HTML meta tag, you can create fields that will be searchable in the corpus built from the manually corrected material.

You can invent your own `keys`, which become searchable features, and usethese to tag entire documents, spand of words, or single words.

As an example:

## Complete examples

The source texts below, using the above rules, should be corrected to look something like this:

| # | Source image                                                                                                 | OCR output              | Ideal transcription     | Rules followed                                                |
|---|--------------------------------------------------------------------------------------------------------------|-------------------------|-------------------------|---------------------------------------------------------------|
| 1 | ![Source image](https://github.com/interrogator/buzzword/raw/master/docs/images/example-01.jpg "Example 1")  | `TO` <br> `" Art. XxL` <br> `Die Verfassunggewåhret die Befugniß- Zehnten und` <br> `Grundzinse loszukaufen Das Gesetz bestimmt die Art` <br> `des Loskauss nach dem gerechten Werth-.` <br> `Bandes-Akte-` <br> `- « Erster Titel.` <br> `. Allgemeine Verfügungen` <br> `« Art 1.` <br> `Die neunzehn SchweizerKantone, nemliche Appenzell,` <br> `Argnn, Basel, Bern, Freyburg, Glarus, Granhündtem` <br> `Luzern, St- Gallen, Schashausen,-Schwyz, Solothurn,` <br> `Tessim Thurgau, Unterwalden, uri, Waadt, Zug und` <br> `«· Züricl), sind untereinander, gemäß den in ihren wech-` <br> `selseitigen Verfassungen aufgestellten Grundsätzen, ver-` <br> `bündet. Sie garantiren einander gegenseitig ihre Ver-` <br> `fassung, ihr Gebiet, ihre Freyheit und ihre Unabhän-` <br> `gigkeit, sowohl gegen fremde Mächte, als gegen Ein-` <br> `grisse anderer Kantone, oder besondrer Faktionen "` <br> `- Art 11.` <br> `Die Kontingente an Truppen oder Geld , welche zur` <br> `Vollziehung dieser Garantie nothwendig werden können,` <br> `werden Von jedem Kanten in folgendem Berhältniß ge-` <br> `leistet: - » . »- | `<meta page=10></meta>` <br> `### Art. XXI` <br> `Die Verfassung gewähret die Befugniß- Zehnten und` <br> `Grundzinse loszukaufen. Das Gesetz bestimmt die Art` <br> `des Loskaufs nach dem gerechten Berth.` <br> `## Bundes-Akte` <br> `### Erster Titel.` <br> `#### Allgemeine Verfügungen` <br> `#### Art II` <br> `Die neunzehn SchweizerKantone, nemlich: Appenzell,` <br> `Argau, Basel, Bern, Frenburg, Glarus, Graubündten,` <br> `Luzern, St. Gallen, Schaffhausen,Schwyz, Solothurn,` <br> `Tessim, Thurgau, Unterwalden, Uri, Wandt, Zug und` <br> `Zürich), sind untereinander, gemäß den in ihren wech-` <br> `selseitigen Verfassungen aufgestellten Grundsätzen, ver-` <br> `bündet. Sie garantiren einander gegenseitig ihre Ver-` <br> `fassung, ihr Gebiet, ihre Freiheit und ihre Unabhän-` <br> `gigkeit, sowohl gegen fremde Mächte, als gegen Ein-` <br> `grisse anderer Kantone, oder besondrer Faktionen.` <br> `#### Art II` <br> `Die Kontingente an Truppen oder Geld, welche zur` <br> `Vollziehung dieser Garantie nothwendig werden können,` <br> `werden Von jedem Kanton in folgendem Berhältniß ge-` <br> `leistet:    | Header, Page numbers, Line breaks                             |
| 2 | ![Source image](https://github.com/interrogator/buzzword/raw/master/docs/images/example-02.jpg "Example 2")  | `K u n d m a ch u n g` <br> `der provisorischen RegierungsKommissioni` <br> `(Vom,15Merz1803.) « (` <br> `Da in Folge des von dem frankischen Conful erlassenen` <br> `VermittlungsAkts die verfassungsmåfsige Regierung un-` <br> `feres Kantons mit dem Anfang künftigen Monats er-—` <br> `wählet werden sollez zu diesem Ende aber erforderlich` <br> `ist , bestimmt zu wissen, welchen unter densBürgern des` <br> `Kantons nach dem IV. Artikel desselben das Stimmrecht` <br> `in den Zünften zustehe, und welche die nöthigen Eigen-` <br> `schaften besitzen, umfowohl auf ihren Zünften als Mit-` <br> `glieder des grossen Raths ernannt, als auch in andern` <br> `Distrikten auf die KandidatenListe nach Ausweis des` <br> `F 17. gesetzt zu werden. Als wird hiemit bekannt ge-` <br> `macht, daß nächsttånftige Woche, und zwar Montags,` <br> `Dienstags nnd Mittwochen den 21, 22 und zzten` <br> `dieses, in, der Stadt Basel in den Verschiedenen Sek-` <br> `tionen, und in den DistrltteuLiestal und Wallenburg` <br> `in sämtlichen Gemeinden- durch Veranstaltung der Mu-` <br> `uicipalitåten,—Register werden eröffnet werden , wo die` <br> `daselbst wohnenden Bürger des Kantons sowohl ihre` <br> `Taus- Geschlechts-, und Zunamen, ihre Heimat, Stand-` <br> `Alter und Beruf angeben, als auch sich in diejenige` <br> `Klasse von soo- 2000 und ewqu Franken einsehen-.-` <br> `hen werden« wozu sie ihre besitzende Liegenschaften oder` <br> `ihre hypothecirten SchuldScheine berechtigen-` <br> `Zu Bestimmung des Werths der Liegenschaften sollen` <br> ` | 1<meta page=27 date="1803.03.16" section="Kundmachung der provisorischen Regierungskommission"></meta>` ` <br> `# Kundmachung der provisorischen Regierungskommission` <br> `## Vom,16 Merz 1803.` <br> `Da in Folge des von dem frankischen Conful erlassenen` <br> `VermittlungsAkts die verfassungsmäfsige Regierung un-` <br> `feres Kantons mit dem Anfang künftigen Monats er-` <br> `wählet werden solle; zu diesem Ende aber erforderlich` <br> `ist , bestimmt zu wissen, welchen unter den Bürgern des` <br> `Kantons nach dem IV. Artikel desselben das Stimmrecht` <br> `in den Zünften zustehe, und welche die nöthigen Eigen-` <br> `schaften besitzen, umsowohl auf ihren Zünften als Mit-` <br> `glieder des grossen Raths ernannt, als auch in andern` <br> `Distrikten auf die KandidatenListe nach Ausweis des` <br> `S 17. gesetzt zu werden. Als wird hiemit bekannt ge-` <br> `macht, daß nächstfünftige Woche, und zwar Montags,` <br> `Dienstags und Mittwochen den 21, 22 und 23ten` <br> `dieses, in der Stadt Basel in den Verschiedenen Sek-` <br> `tionen, und in den Distrikten Liestal und Wallenburg` <br> `in sämtlichen Gemeinden, durch Veranstaltung der Mu-` <br> `uicipalitåten, Register werden eröffnet werden, wo die` <br> `daselbst wohnenden Bürger des Kantons sowohl ihre` <br> `Taus- Geschlechts- und Zunamen, ihre Heimat, Stand,` <br> `Alter und Beruf angeben, als auch sich in diejenige` <br> `Klasse von 500, 3000 und 10,000 Franken einschrei-` <br> `ben werden, wozu sie ihre besitzende Liegenschaften oder` <br> `ihre hypothecirten SchuldScheine berechtigen.` <br> `Zu Bestimmung des Werths der Liegenschaften sollen...    | Metadata additions (whole page, text spans, single word)      |
| 3 | ![Source image](https://github.com/interrogator/buzzword/raw/master/docs/images/example-03.jpg "Example 3")  | `xs` <br> ` ` <br> `Aste Xxxll` <br> `Sie allein schließt HandelsTraktate und Kapitnlatws` <br> `nen für auswartige KriegsDiensie Sie bevollmächtiget` <br> `die Kantone, wenn es Statt sinden kann, über andere` <br> `Gegenstände mit fremden Mächten besonders zu unter-` <br> `handeln` <br> `Art. Xxx111.·` <br> `Ohne ihre Einwillignng kann in keinem Kanton für` <br> `eine fremde Macht geworden werden.` <br> `Art. xxxIv.` <br> `Die Tagsatznng befiehlt die Aufstellung des laut dem` <br> `zwevten Artikel für jeden Kanton bestimmten TruvpenKoni` <br> `tingents. Sie ernennt den General, der sie komman-` <br> `dieren soll , und nimmt alle für die Sieheiheit der Schweiz-` <br> `und fnr die Ausführung der in dem ersten Artikel enthal-` <br> `tenen Verfngnngen nöthigen Maßnahmen Das nemlis` <br> `che Recht hat s e, wenn Unruhen in einem Kanten die` <br> `Sicherheit der andern Kantone bedrohen-` <br> `. » Art. Xxxv.` <br> `Die ansserotdentlichen Abgesandten werden von ihr-«` <br> `ernennt nnd abgeordnet. «` <br> `, Art-Xxxv1.` <br> `Sie entscheidet über die Zwistigkeiten- welche zwischen` <br> `Kantonen entstehen, wenn sie nicht durch Schiedsrichter` <br> `beygelegt werden können- Zu diesem Ende bildet sie sich` <br> `Ends ihrer Sitzungen in einSyndikatz in diesem Fall hat` <br> `jeder Depntirte nur eine Stimme, nnd es kamt ihm` <br> `keine Jnsirnktion derhalben mitgegeben werden. | `<meta page=18></meta>` ### Art `<meta art=34>XXXII</meta>`` <br> `Sie allein schließt HandelsTraktate und Kapitulatio-` <br> `nen für auswärtige KriegsDienste. Sie bevollmächtiget` <br> `die Kantone, wenn es Statt sinden kann, über andere` <br> `Gegenstände mit fremden Mächten besonders zu unter-` <br> `handeln` <br> `### Art <meta art=33>XXXIII</meta>` <br> `Ohne ihre Einwillignng kann in keinem Kanton für` <br> `eine fremde Macht geworden werden.` <br> `### Art <meta art=34>XXXIV</meta>` <br> `Die Tagsatzung befiehlt die Aufstellung des laut dem` <br> `zwenten Artikel für jeden Kanton bestimmten TruppenKon-` <br> `tingents. Sie ernennt den General, der sie komman-` <br> `dieren soll; und nimmt alle für die Sicherheit der Schweiz,` <br> `und für die Ausführung der in dem ersten Artikel enthal-` <br> `tenen Verfügungen nöthigen Maßnahmen. Das nemli-` <br> `che Recht hat sie, wenn Unruhen in einem Kanton die` <br> `Sicherheit der andern Kantone bedrohen.` <br> `### Art <meta art=35>XXXV</meta>` <br> `Die ausserordentlichen Abgesandten werden von ihr` <br> `ernennt nnd abgeordnet.` <br> `### Art <meta art=36>XXXVI</meta>` <br> `Sie entscheidet über die Zwistigkeiten- welche zwischen` <br> `Kantonen entstehen, wenn sie nicht durch Schiedsrichter` <br> `beygelegt werden können. Zu diesem Ende bildet sie sich` <br> `Ends ihrer Sitzungen in ein Syndikat; in diesem Fall hat` <br> `jeder Deputirte nur eine Stimme, und es kann ihm` <br> `keine Instruktion derhalben mitgegeben werden.` <br> `    | Empty file                                                    |
| 4 | ![Source image](https://github.com/interrogator/buzzword/raw/master/docs/images/example-03.jpg "Example 3")  | `II` <br> ` ` <br> `- Auf ein Korps von 15203 Mann, und auf eine` <br> `Summe von 490507 SchweizerFranken giebt der` <br> `— Mann- Franken-.` <br> `Kantvn Beim 2292. 9169 5.` <br> `——s- Zürich F · I 929. 7715;.` <br> `—- Waadt 1482- 5927 Z.` <br> `— St. Gallen 1315, 39451.` <br> `——s Argau 1205. « 52212.` <br> `-—-- Graubündten 1 zoo. 12200, ·` <br> `-—-—- Tessin 902. I 8039,` <br> `—-—— Luzern - 8674 — » zgoea` <br> `—- Thurgau 8352 2505 2- .` <br> `———·· Freyburg sm. 18 591.` <br> `——s Apvenzell 486,. « 9728.` <br> `—- Solothnrn 452. -1 8097,` <br> `——-« Basel · 409. « 20450p` <br> `—-—-· Schwyz zo 1 . 3012,..` <br> `s-——-— Glaris 241 . 482;.` <br> `—-—- . Schafhausm — 2»; ;. 9327,` <br> `— Unterwalden » 19 l . x»907.` <br> `s——·——— Zug XIV-. 2497».` <br> `-———— Ury 1 1 8. 1 1 84.` <br> `A r t. I I I. ·` <br> `Jn der Schweiz findet kein Unterthanenland«, kein` <br> `Orts- noch Geburts- noch Personal- uoch FamilienVor-` <br> `zug mehr Statt.` <br> `Art. IV.` <br> `Jedem SchweizerBürgev steht frev, sich in einem an-` <br> `dern Kanton niederzulassen, und dorten feine Jndustriex` <br> `frey auszuüben Er erwirbt die politischen Rechte nach« »` <br> ` | <meta page=11></meta> ` <br> ` ` <br> `Auf ein Korps von 15203 Mann, und auf eine ` <br> `Summe von 490507 SchweizerFranken giebt der | <meta page=11></meta> 

Auf ein Korps von 15203 Mann, und auf eine 
Summe von 490507 SchweizerFranken giebt der 

### Art <meta art=3>III</meta> 

In der Schweiz findet kein Unterthanenland, fein 
Orts- noch Geburts- noch Personal- uoch FamilienVor- 
zug mehr Statt. 

### Art <meta art=4>IV</meta> 

Jedem SchweizerBürget steht frey, sich in einem an- 
dern Kanton niederzulassen, und dorten deine Industrie 
frey auszuüben Er erwirbt die poltischen Rechte nach... | Empty file                                                    |