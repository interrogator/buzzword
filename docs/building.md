# Creating corpora

> On this page, you will learn how to build the metadata-rich corpora that work best with *buzzword*.

## Basics: an unannotated corpus

At the very minimum, *buzzword* can accept a single file of plain text. For example, you could create a file, `joke.txt`, containing the following text:

```xml
A lion and a cheetah decide to race.      
The cheetah crosses the finish line first.
"I win!"
"You're a cheetah!"
"You're lion!"
```

Once you upload it, the file will be run through a processing pipeline, which will split the text into sentences and tokens, and then annotate with POS tags, wordclasses, and dependency grammar annotations. This is already a good start: you can do all kinds of frequency calculation, concordancing and visualisation with just this plain text. However, where *buzzword* really excels is in handling large, metadata-rich datasets. So, let's go through the process of building such a corpus now.

## Multiple files

**buzzword** accepts multiple files as input. Using multiple files is a quick and easy way to add metadata into your corpus: once uploaded, you will be able to explore language use by file, or filter data by file to dynamically create subcorpora.

Therefore, the best way to use files is to give them a name that is both sequential and categorical. So, let's rename `joke.txt` to `001-joke-lion-pun.txt`. Just by doing this, we will later be able to filter by pun jokes, by lion jokes, or visualise language change from our first to our last joke.

```xml
jokes
├── 001-joke-lion-pun.txt
├── 002-joke-soldier-knock-knock.txt
└── ... etc.
```

## Adding metadata: speaker names

Now, let's add some metadata within our corpus files in a format that *buzzword* can understand. First (and simplest), we add speaker names at the start of lines. Like filenames, any like other annotations we may add, these speaker names will end up in the parsed corpus, allowing us to filter the corpus, calculate stats, and visualise data by speaker.

```xml
A lion and a cheetah decide to race. 
The cheetah crosses the finish line first.
CHEETAH: I win!
LION: You're a cheetah!
CHEETAH: You're lion!
```

Speaker names should be provided in capital letters, using underscores or hyphens instead of spaces. Not all lines need speaker names.

### File-level metadata

Next, we can begin adding metadata in XML format. XML is much richer and better structured than plain text, allowing a great deal of precision. To add metadata that applies to an entire file, you need to create an XML element `<meta>` on the first line of the file:

```xml
<meta doc-type="joke" rating=6.50 speaker="NARRATOR"/>
A lion and a cheetah decide to race. 
The cheetah crosses the finish line first.
CHEETAH: I win!
LION: You're a cheetah!
CHEETAH: You're lion!
```

Best practice here is to use lower-cased names and hyphens, and to use quotation marks for string values. 

File-level metadata will be applied to every single sentence (and therefore, every token) in the file. Therefore, though we've defined `speaker` both in XML and in script-style, that's no problem: `NARRATOR` will be applied to every line, but overwritten by `CHEETAH` and `LION` where they appear. This means that in general, you can use the file-level metadata to provide overwritable defaults, rather than adding the value to each line.

### Span annotation

we can also add metadata to spans of text using XML elements, in a format similar to file-level metadata.

```xml
<meta doc-type="joke" rating=6.50 speaker="NARRATOR"/>
<meta move="setup" dialog=false punchline=false some-schema=9>A lion and a cheetah decide to race.</meta>
<meta move="setup" dialog=false punchline=false>The cheetah crosses the finish line first.</meta>
CHEETAH:<meta move="middle" dialog=true some-schema=2>I win!</meta>
LION:<meta move="punchline" funny=true dialog=true some-schema=3>You're a cheetah!</meta>
CHEETAH:<meta move="punchline" funny=true dialog=true some-schema=4 rating=7.8>You're lion!</meta>
```

Text within a span will be annotated with the metadata tributes inside the XML tag. This more fine-grained metadata is great for discourse-analytic work, such as counting frequencies by genre stages of a text (i.e. joke setup vs. punchline). Note that you should not create nested XML annotations. Instead, wrap each span separately.

### Summary

Available metadata formats are:

1. File level metadata (XML on the first line)
2. Span/token level metadata (XML elements containing one or more tokens)
3. Speaker names in script style

Important things to remember when building your unparsed dataset:

* XML annotations values can be strings, integers, floats and booleans
* Metadata is always inherited, from file-level to span-level. In the example above, the `rating` for the whole file will be replaced for the final sentence with `7.8`.
* If a field is missing in one of the metadata, it will end up with a value of `None` in the parsed corpus.
* Make sure your metadata key names are alphanumeric. Hyphens will be converted to underscores.

Finally, make sure that you do not use any of the following names as metadata fields, because these are needed for the attributes created by the parser:

* CONLL columns: `w`, `l`, `x`, `p`, `m`, `f`, `g`, `o`, `e`
* Index names: `file`, `s`, `i`
* NER fields: `ent-type`, `ent_iob`, `ent_id`
* Sentiment analysis: `sentiment`
* Other names used internally by the system: `_n`, `sent_len`, `sent_id`, `text`, `parse`

Once parsed, the first sentence of the underlying dataset will modelled as something like:

| File     | Sent   | Token   | Word    | Lemma   | Wordclass   | Part of speech   |   Governor index | Dependency role   | Extra   | dialog   | doc_type   |   ent_id | ent_iob   | being   | funny   | move   | play_on   | punchline   |   rating |   sent_id |   sent_len |   some_schema | Speaker   |
|------|----|----|---------|---------|-------------|------------------|------------------|-------------------|-----|----------|------------|----------|-----------|------------|---------|--------|-----------|-------------|----------|-----------|------------|---------------|-----------|
| 001-joke-lion-pun |  1 |  1 | A       | a       | DET         | DT               |                2 | det               | _   | False    | joke       |        0 | O         | animal     | _       | setup  | _         | False       |      6.5 |         1 |          9 |             9 | NARRATOR  |
| 001-joke-lion-pun |  1 |  2 | lion    | lion    | NOUN        | NN               |                6 | nsubj             | _   | False    | joke       |        0 | O         | animal     | _       | setup  | _         | False       |      6.5 |         1 |          9 |             9 | NARRATOR  |
| 001-joke-lion-pun |  1 |  3 | and     | and     | CCONJ       | CC               |                2 | cc                | _   | False    | joke       |        0 | O         |            | _       | setup  | _         | False       |      6.5 |         1 |          9 |             9 | NARRATOR  |
| 001-joke-lion-pun |  1 |  4 | a       | a       | DET         | DT               |                5 | det               | _   | False    | joke       |        0 | O         | animal     | _       | setup  | _         | False       |      6.5 |         1 |          9 |             9 | NARRATOR  |
| 001-joke-lion-pun |  1 |  5 | cheetah | cheetah | NOUN        | NN               |                2 | conj              | _   | False    | joke       |        0 | O         | animal     | _       | setup  | _         | False       |      6.5 |         1 |          9 |             9 | NARRATOR  |
| 001-joke-lion-pun |  1 |  6 | decide  | decide  | VERB        | VBP              |                0 | ROOT              | _   | False    | joke       |        0 | O         |            | _       | setup  | _         | False       |      6.5 |         1 |          9 |             9 | NARRATOR  |
| 001-joke-lion-pun |  1 |  7 | to      | to      | PART        | TO               |                8 | aux               | _   | False    | joke       |        0 | O         |            | _       | setup  | _         | False       |      6.5 |         1 |          9 |             9 | NARRATOR  |
| 001-joke-lion-pun |  1 |  8 | race    | race    | VERB        | VB               |                6 | xcomp             | _   | False    | joke       |        0 | O         |            | _       | setup  | _         | False       |      6.5 |         1 |          9 |             9 | NARRATOR  |
| 001-joke-lion-pun |  1 |  9 | .       | .       | PUNCT       | .                |                6 | punct             | _   | False    | joke       |        0 | O         |            | _       | setup  | _         | False       |      6.5 |         1 |          9 |             9 | NARRATOR  |

## Next steps

Once you have a corpus, be it one or many files, annotated or unannotated, you are ready to feed it to *buzzword*. Simply drag and drop or click to upload your files, give your corpus a name, select a language, and hit `Upload and parse`. 

Once the parsing is finished, a link to the new corpus will appear. Click it to explore the corpus in the `Explore` page. Click [here](guide.md) for instructions on how to use the *Explore* page.
