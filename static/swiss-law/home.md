<br><br>

## Swiss legal history: a collaborative digitisation effort

This site provides an interface for exploring the **Swiss Legal Texts** corpus, which contains Swiss laws written in German between (YEARS).

**(Table of 2x2 visualisations here for some visual appeal)**

### Browse the collection?

The texts have undergone [Optical Character Recognition](https://en.wikipedia.org/wiki/Optical_character_recognition), so that the data can be explored using digital methods. The OCR process is never perfect, expecially when dealing with older texts. Therefore, while browsing, you can see the current OCR results, and submit corrections if you see any mistakes.

### Improve the collection?

Using the [Guide for corrections](/guide.html), you can learn best practices for submitting corrections to the dataset. With some help from the community, we hope to eventually develop a high-quality searchable database of historical Swiss law, including not just German, but French and Italian documents as well.

### Analyse the data?

The corrected OCR is periodically run through a linguistic processing pipeline, which makes possible novel ways of searching and visualising search results. You can use the [Explore](/explore/swiss-law) interface for this.

### A sample analysis?

You can visit [the example page](/example/swiss-law.html) to see a sample analysis made possible by this software. This provides a practical introduction to the Explore interface.

### About the project

The project has been conceptualised by Martin Kurz at the University of Zurich, with software carried out by S3IT.

The project makes use of numerous state-of-the-art tools, including:

* [*Django*](https://github.com/django/django) (the website's framework)
* [*Martor*](https://github.com/agusmakmun/django-markdown-editor) (for submitting corrections)
* [*Tesseract*](https://github.com/tesseract-ocr/tesseract) (for OCR)
* [*buzzword*](https://github.com/interrogator/buzzword), an open-source tool designed for browser-based analysis of language texts
