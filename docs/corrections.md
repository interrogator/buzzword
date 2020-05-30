# Guidelines for correcting datasets

Datasets that have undergone automatic Optical Character Recognition (OCR), are rarely perfect. While most words are successfully recognised, numerous inconsistencies always remain.

For *buzzword* corpora, the main goal of making the corrections is to make a digitised version of the dataset that is as consistent as possible, so that it may be processed further with natural language processing tools. This makes it possible to use the *buzzword explorer* to analyse the digitised, (hopefully metadata-rich) corpus.

For this to work, corrections need to follow a set of guidelines. These are laid out below. All steps are designed to do one or more of the following:

* Increase the accuracy of the parser that will eventually be run over the corrected dataset
* Remove unuseful information
* Add metadata features that can later be used when searching

## Spelling errors and non-standard spellings.

How to handle spelling errors and non-standard spellings depends on whether or not these are important features of your corpus (i.e. you have a corpus of learners' English). If you want to retain information about the error, use a metadata tag like so:

> `Please send me your <meta sic="adress">address</meta>`

The name of the metadata field is up to you, as is whether you'd like to put the original or the corrected text inside the metadata tag. Generally speaking, it is better to have the error/non-standard text inside the metadata tag, because later steps like part-of-speech tagging and parsing will work better with text that resembles standard language. Consistency, however, is key: whatever convention you choose, stick to it throughout the correction phase.

## Line breaks

OCR will generally not put paragraphs on one line. Instead, line breaks are made at the end of each line of text in the source document. This poses challenges for parsers, which treat line breaks as sentence boundaries.

Best practice is as follows. If a word is broken over two lines by a hyphen:

```
I am thinking of go-
ing away this weekend
```

then this can remain the same in the corrected version (the tool will automatically fix this during post-processing). However, the first line *must* end with a hyphen character.

If no word is broken across lines, you can leave the text as is. During post-processing, the lines will be joined with a space as a separator, so:

```
I am thinking of going
away this weekend
```

will simply become `I am thinking of going away this weekend` for the purposes of parsing.

## Paragraphs

Do not use indentation to mark new paragraphs. Instead, use two line breaks. So, if your OCR result looks like this:

```
After a long journey on the train,
Zurich was to be the final stop.
    When we reached our destination,
we got out and stretched our legs
```

Convert it into this:

```
After a long journey on the train,
Zurich was to be the final stop.

When we reached our destination,
we got out and stretched our legs
```

## Non-alphanumeric content

OCR struggles with things like horizontal lines on a page, blemishes, and other sorts of marking. It may turn a horizontal line into a series of hyphens, for example, which will not parse well.

Therefore, vertical and horizontal lines are not to be represented in the corrections. Other random characters, like a `.` that has appeared due to a blemish on the page, should also be removed, or it will be interpreted as a full-stop.

## Headings

Use markdown heading syntax (prefacing lines with `#` for first-level, `##` for second-level headings, and so on). Try to be consistent, as *buzzword* will attempt to group texts using these heading labels.

During the writing of corrections, note that you can hit the Preview button to see that your headings are recognised, and that their size makes sense, semantically speaking.

## Section titles in page borders

At the top of pages, sometimes the current section title is printed. This should be handled as a second-level header:

```
## Chapter two

The following day, we ...
```

If you need to be more precise, use a `<meta>` tag. If you don't want the text to be parsed, put it inside the XML tag like so:

```xml
<meta section="Chapter two"></meta>

Text continues here...
```

If you do want the text to be parsed, make sure it is outside of the tags:

```xml
<meta section=2>Chapter 2</meta>

Text continues here...
```

If a `<meta>` tag is the first line of the file, all subsequent data in the file will be tagged with its contents (i.e. it is taken to be a file-level tag). Later, this will aid in the process of limiting searches to, or excluding, particular sections.

## Page numbers

The best way to deal with page numbers is to include them inside a `<meta>` tag to the top of the page. In the example below, we add both a page feature and a section feature, both of which will be searchable in the resulting corpus.

```xml
<meta page="6" section="Chapter two" />

Text continues here...
```

Putting the page number inside the XML means that it won't actually get parsed, which is good, as it isn't part of the language content of the document.

By default, the tool tries to automatically locate page numbers and create the `<meta>` tag as the first line. However, it isn't perfect, especially when dealing with things like roman numerals. Feel free to correct any tags that may have been automatically generated.

For page numbers in tables of contents, see below.

## Tables of contents

Tables of contents (TOC) generally do not provide much value to us, so do not assign them much priority. They can even do some damage, artificially inflating word counts and so on. So, you may choose to delete TOCs entirely. In this case, replace all the OCR result with simply:

```xml
<meta blank=true/>
```

If you want to include the TOC in your corpus, you will need to make decisions about whether or not you want the TOC labels to qualify as regular text for the purpose of frequency counting. If you want TOC words to be counted, you might want to structure `<meta>` tags around them:

```xml
<meta format="toc">Section text here (page-number)></meta>
```

Later on, when searching/counting words, your search can easily skip any text marked with a `format` value of `toc`.

## Bold and italic text

If text appears to be bold or italic in the source texts, and if you think this information is important enough to go into your final corpus, you can represent this using standard markdown asterisk syntax. Surround a word with an asterisk on each side for italics, and two asterisks on each side for bold.

You can hit the Preview button to see that your italics and markdown match the source text. During parsing, *buzzword* will automatically tag these sections with metadata features of `bold` and `italic` respectively.

## Blank pages

Generally, a handful of pages in any book are blank, or contain only an image that cannot be parsed as natural language. If a page has no meaningful text, the ideal thing to enter is:

```xml
<meta blank="true"/>
```

This helps the software be sure that good content was not accidentally deleted from a page. Some pages may be marked like this automatically; if this is a mistake, you should correct it.

## Misc. chracters and symbols

Sometimes, the parser interprets a spot on a page as a letter or number. When this has happened, simply delete the unwanted characters, since they will only complicate things down the line.

## Tables and figures

If *useful* text can be extracted from a table/figure, you can devise some kind of scheme for inclusion in the correction document, like this:

```xml
<meta representation="graphic">Text within table here</meta>
```

The metadata field names and values are up to you. Keep them consistent throughout the document. Do not try to copy the layout of the table; the parser is only interested in any sentence-like text it contains.

If there is nothing of linguistic value in the table or figure, there is generally little problem with simply excluding it from the corrected text entirely. If it has a caption, you may want to include just that, with or without a `<meta>` label

## Complete examples

The source texts below, using the above rules, should be corrected to look something like this:

| # | Source image                                                                                                 | OCR output              | Ideal transcription     | Rules followed                                                |
|---|--------------------------------------------------------------------------------------------------------------|-------------------------|-------------------------|---------------------------------------------------------------|
| 1 | ![Source image](https://github.com/interrogator/buzzword/raw/master/docs/images/example-01.jpg "Example 1")  | `TO` <br> `" Art. XxL` <br> `Die Verfassunggewåhret die Befugniß- Zehnten und` <br> `Grundzinse loszukaufen Das Gesetz bestimmt die Art` <br> `des Loskauss nach dem gerechten Werth-.` <br> `Bandes-Akte-` <br> `- « Erster Titel.` <br> `. Allgemeine Verfügungen` <br> `« Art 1.` <br> `Die neunzehn SchweizerKantone, nemliche Appenzell,` <br> `Argnn, Basel, Bern, Freyburg, Glarus, Granhündtem` <br> `Luzern, St- Gallen, Schashausen,-Schwyz, Solothurn,` <br> `Tessim Thurgau, Unterwalden, uri, Waadt, Zug und` <br> `«· Züricl), sind untereinander, gemäß den in ihren wech-` <br> `selseitigen Verfassungen aufgestellten Grundsätzen, ver-` <br> `bündet. Sie garantiren einander gegenseitig ihre Ver-` <br> `fassung, ihr Gebiet, ihre Freyheit und ihre Unabhän-` <br> `gigkeit, sowohl gegen fremde Mächte, als gegen Ein-` <br> `grisse anderer Kantone, oder besondrer Faktionen "` <br> `- Art 11.` <br> `Die Kontingente an Truppen oder Geld , welche zur` <br> `Vollziehung dieser Garantie nothwendig werden können,` <br> `werden Von jedem Kanten in folgendem Berhältniß ge-` <br> `leistet: - » . »- | `<meta page=10></meta>` <br> `### Art. XXI` <br> `Die Verfassung gewähret die Befugniß- Zehnten und` <br> `Grundzinse loszukaufen. Das Gesetz bestimmt die Art` <br> `des Loskaufs nach dem gerechten Berth.` <br> `## Bundes-Akte` <br> `### Erster Titel.` <br> `#### Allgemeine Verfügungen` <br> `#### Art II` <br> `Die neunzehn SchweizerKantone, nemlich: Appenzell,` <br> `Argau, Basel, Bern, Frenburg, Glarus, Graubündten,` <br> `Luzern, St. Gallen, Schaffhausen,Schwyz, Solothurn,` <br> `Tessim, Thurgau, Unterwalden, Uri, Wandt, Zug und` <br> `Zürich), sind untereinander, gemäß den in ihren wech-` <br> `selseitigen Verfassungen aufgestellten Grundsätzen, ver-` <br> `bündet. Sie garantiren einander gegenseitig ihre Ver-` <br> `fassung, ihr Gebiet, ihre Freiheit und ihre Unabhän-` <br> `gigkeit, sowohl gegen fremde Mächte, als gegen Ein-` <br> `grisse anderer Kantone, oder besondrer Faktionen.` <br> `#### Art II` <br> `Die Kontingente an Truppen oder Geld, welche zur` <br> `Vollziehung dieser Garantie nothwendig werden können,` <br> `werden Von jedem Kanton in folgendem Berhältniß ge-` <br> `leistet:    | Header, Page numbers, Line breaks                             |
| 2 | ![Source image](https://github.com/interrogator/buzzword/raw/master/docs/images/example-02.jpg "Example 2")  | `K u n d m a ch u n g` <br> `der provisorischen RegierungsKommissioni` <br> `(Vom,15Merz1803.) « (` <br> `Da in Folge des von dem frankischen Conful erlassenen` <br> `VermittlungsAkts die verfassungsmåfsige Regierung un-` <br> `feres Kantons mit dem Anfang künftigen Monats er-—` <br> `wählet werden sollez zu diesem Ende aber erforderlich` <br> `ist , bestimmt zu wissen, welchen unter densBürgern des` <br> `Kantons nach dem IV. Artikel desselben das Stimmrecht` <br> `in den Zünften zustehe, und welche die nöthigen Eigen-` <br> `schaften besitzen, umfowohl auf ihren Zünften als Mit-` <br> `glieder des grossen Raths ernannt, als auch in andern` <br> `Distrikten auf die KandidatenListe nach Ausweis des` <br> `F 17. gesetzt zu werden. Als wird hiemit bekannt ge-` <br> `macht, daß nächsttånftige Woche, und zwar Montags,` <br> `Dienstags nnd Mittwochen den 21, 22 und zzten` <br> `dieses, in, der Stadt Basel in den Verschiedenen Sek-` <br> `tionen, und in den DistrltteuLiestal und Wallenburg` <br> `in sämtlichen Gemeinden- durch Veranstaltung der Mu-` <br> `uicipalitåten,—Register werden eröffnet werden , wo die` <br> `daselbst wohnenden Bürger des Kantons sowohl ihre` <br> `Taus- Geschlechts-, und Zunamen, ihre Heimat, Stand-` <br> `Alter und Beruf angeben, als auch sich in diejenige` <br> `Klasse von soo- 2000 und ewqu Franken einsehen-.-` <br> `hen werden« wozu sie ihre besitzende Liegenschaften oder` <br> `ihre hypothecirten SchuldScheine berechtigen-` <br> `Zu Bestimmung des Werths der Liegenschaften sollen` <br> ` | `<meta page=27 date="1803.03.16" section="Kundmachung der provisorischen Regierungskommission"></meta>` <br> `# Kundmachung der provisorischen Regierungskommission` <br> `## Vom,16 Merz 1803.` <br> `Da in Folge des von dem frankischen Conful erlassenen` <br> `VermittlungsAkts die verfassungsmäfsige Regierung un-` <br> `feres Kantons mit dem Anfang künftigen Monats er-` <br> `wählet werden solle; zu diesem Ende aber erforderlich` <br> `ist , bestimmt zu wissen, welchen unter den Bürgern des` <br> `Kantons nach dem IV. Artikel desselben das Stimmrecht` <br> `in den Zünften zustehe, und welche die nöthigen Eigen-` <br> `schaften besitzen, umsowohl auf ihren Zünften als Mit-` <br> `glieder des grossen Raths ernannt, als auch in andern` <br> `Distrikten auf die KandidatenListe nach Ausweis des` <br> `S 17. gesetzt zu werden. Als wird hiemit bekannt ge-` <br> `macht, daß nächstfünftige Woche, und zwar Montags,` <br> `Dienstags und Mittwochen den 21, 22 und 23ten` <br> `dieses, in der Stadt Basel in den Verschiedenen Sek-` <br> `tionen, und in den Distrikten Liestal und Wallenburg` <br> `in sämtlichen Gemeinden, durch Veranstaltung der Mu-` <br> `uicipalitåten, Register werden eröffnet werden, wo die` <br> `daselbst wohnenden Bürger des Kantons sowohl ihre` <br> `Taus- Geschlechts- und Zunamen, ihre Heimat, Stand,` <br> `Alter und Beruf angeben, als auch sich in diejenige` <br> `Klasse von 500, 3000 und 10,000 Franken einschrei-` <br> `ben werden, wozu sie ihre besitzende Liegenschaften oder` <br> `ihre hypothecirten SchuldScheine berechtigen.` <br> `Zu Bestimmung des Werths der Liegenschaften sollen...    | Metadata additions (whole page, text spans, single word)      |
| 3 | ![Source image](https://github.com/interrogator/buzzword/raw/master/docs/images/example-03.jpg "Example 3")  | `xs` <br> ` ` <br> `Aste Xxxll` <br> `Sie allein schließt HandelsTraktate und Kapitnlatws` <br> `nen für auswartige KriegsDiensie Sie bevollmächtiget` <br> `die Kantone, wenn es Statt sinden kann, über andere` <br> `Gegenstände mit fremden Mächten besonders zu unter-` <br> `handeln` <br> `Art. Xxx111.·` <br> `Ohne ihre Einwillignng kann in keinem Kanton für` <br> `eine fremde Macht geworden werden.` <br> `Art. xxxIv.` <br> `Die Tagsatznng befiehlt die Aufstellung des laut dem` <br> `zwevten Artikel für jeden Kanton bestimmten TruvpenKoni` <br> `tingents. Sie ernennt den General, der sie komman-` <br> `dieren soll , und nimmt alle für die Sieheiheit der Schweiz-` <br> `und fnr die Ausführung der in dem ersten Artikel enthal-` <br> `tenen Verfngnngen nöthigen Maßnahmen Das nemlis` <br> `che Recht hat s e, wenn Unruhen in einem Kanten die` <br> `Sicherheit der andern Kantone bedrohen-` <br> `. » Art. Xxxv.` <br> `Die ansserotdentlichen Abgesandten werden von ihr-«` <br> `ernennt nnd abgeordnet. «` <br> `, Art-Xxxv1.` <br> `Sie entscheidet über die Zwistigkeiten- welche zwischen` <br> `Kantonen entstehen, wenn sie nicht durch Schiedsrichter` <br> `beygelegt werden können- Zu diesem Ende bildet sie sich` <br> `Ends ihrer Sitzungen in einSyndikatz in diesem Fall hat` <br> `jeder Depntirte nur eine Stimme, nnd es kamt ihm` <br> `keine Jnsirnktion derhalben mitgegeben werden. | `<meta page=18></meta>` ### Art `<meta art=34>XXXII</meta>` <br> `Sie allein schließt HandelsTraktate und Kapitulatio-` <br> `nen für auswärtige KriegsDienste. Sie bevollmächtiget` <br> `die Kantone, wenn es Statt sinden kann, über andere` <br> `Gegenstände mit fremden Mächten besonders zu unter-` <br> `handeln` <br> `### Art <meta art=33>XXXIII</meta>` <br> `Ohne ihre Einwillignng kann in keinem Kanton für` <br> `eine fremde Macht geworden werden.` <br> `### Art <meta art=34>XXXIV</meta>` <br> `Die Tagsatzung befiehlt die Aufstellung des laut dem` <br> `zwenten Artikel für jeden Kanton bestimmten TruppenKon-` <br> `tingents. Sie ernennt den General, der sie komman-` <br> `dieren soll; und nimmt alle für die Sicherheit der Schweiz,` <br> `und für die Ausführung der in dem ersten Artikel enthal-` <br> `tenen Verfügungen nöthigen Maßnahmen. Das nemli-` <br> `che Recht hat sie, wenn Unruhen in einem Kanton die` <br> `Sicherheit der andern Kantone bedrohen.` <br> `### Art <meta art=35>XXXV</meta>` <br> `Die ausserordentlichen Abgesandten werden von ihr` <br> `ernennt nnd abgeordnet.` <br> `### Art <meta art=36>XXXVI</meta>` <br> `Sie entscheidet über die Zwistigkeiten- welche zwischen` <br> `Kantonen entstehen, wenn sie nicht durch Schiedsrichter` <br> `beygelegt werden können. Zu diesem Ende bildet sie sich` <br> `Ends ihrer Sitzungen in ein Syndikat; in diesem Fall hat` <br> `jeder Deputirte nur eine Stimme, und es kann ihm` <br> `keine Instruktion derhalben mitgegeben werden.` <br> `    | ... file                                                    |
