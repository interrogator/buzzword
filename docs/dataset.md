# buzz datasets: exploring parsed corpora

Once you have loaded a corpus into memory, or queried a corpus without loading, you are left with a `Dataset`---a DataFrame like object with each token as a row, and its features as columns.

This object can be manipulated in a number of ways.

First, let's load in our corpus. This time, we'll use the metadata-rich script from [Spike Lee](https://en.wikipedia.org/wiki/Spike_Lee)'s [Do the Right Thing](https://en.wikipedia.org/wiki/Do_the_Right_Thing).

```python
from buzz import Corpus
dtrt = Corpus('dtrt/do-the-right-thing-parsed')
```

## Dataset attributes

Features of the token, as determined by the parser, are all available for you to work with.

You can also use any metadata features that were included in your original texts.

| Feature | Valid accessors
|-------|---------------------------|
| file  | `file`            |
| sentence # | `s`, `sentence` | 
| word  | `w`, `word`, `words`            |
| lemma | `l`, `lemma`, `lemmas`, `lemmata` |
| speaker | `speaker` | 


## Dataset.just

`Dataset.just` is equivalent to a simple search of the corpus.

If we want to see the nouns in the corpus, we could do any of the below, depending on exactly what we want to capture, and how we prefer to express it:

```python
dtrt.just.wordclass.NOUN.head().to_html()
```

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th></th>
      <th>w</th>
      <th>l</th>
      <th>x</th>
      <th>p</th>
      <th>g</th>
      <th>f</th>
    </tr>
    <tr>
      <th>file</th>
      <th>s</th>
      <th>i</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">01-we-love-radio-station-storefront</th>
      <th rowspan="2" valign="top">1</th>
      <th>6</th>
      <td>teeth</td>
      <td>tooth</td>
      <td>NOUN</td>
      <td>NNS</td>
      <td>2</td>
      <td>dobj</td>
    </tr>
    <tr>
      <th>13</th>
      <td>lips</td>
      <td>lip</td>
      <td>NOUN</td>
      <td>NNS</td>
      <td>9</td>
      <td>appos</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">10</th>
      <th>2</th>
      <td>voice</td>
      <td>voice</td>
      <td>NOUN</td>
      <td>NN</td>
      <td>0</td>
      <td>ROOT</td>
    </tr>
    <tr>
      <th>4</th>
      <td>choice</td>
      <td>choice</td>
      <td>NOUN</td>
      <td>NN</td>
      <td>3</td>
      <td>pobj</td>
    </tr>
    <tr>
      <th>11</th>
      <th>2</th>
      <td>world</td>
      <td>world</td>
      <td>NOUN</td>
      <td>NN</td>
      <td>8</td>
      <td>poss</td>
    </tr>
  </tbody>
</table>

You could get similar results in slightly different ways:
```python
# when your query needs to be a string
dtrt.just.wordclass('NOUN') 
# if you wanted to use pos rather than wordclass
dtrt.just.pos('^N')
```

Using the bracket syntax, you can pass in some keyword arguments:

* `case`: case sensitivity (default True)


Because Datasets are subclasses of pandas DataFrames, we could also do this using pandas syntax:

```python
dtrt[dtrt.p.str.startswith('N')]
```

Because metadata attributes are treated in the same way as token features, we could get all words spoken by a specific character with:

```python
dtrt.just.speaker.MOOKIE.to_html()
```

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th></th>
      <th>w</th>
      <th>l</th>
      <th>x</th>
      <th>p</th>
      <th>g</th>
      <th>f</th>
    </tr>
    <tr>
      <th>file</th>
      <th>s</th>
      <th>i</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">04-jade's-bedroom</th>
      <th rowspan="2" valign="top">12</th>
      <th>1</th>
      <td>Wake</td>
      <td>wake</td>
      <td>PROPN</td>
      <td>NNP</td>
      <td>0</td>
      <td>ROOT</td>
    </tr>
    <tr>
      <th>2</th>
      <td>up!.</td>
      <td>up!.</td>
      <td>PROPN</td>
      <td>NNP</td>
      <td>1</td>
      <td>acomp</td>
    </tr>
    <tr>
      <th rowspan="3" valign="top">15</th>
      <th>1</th>
      <td>It</td>
      <td>-PRON-</td>
      <td>PRON</td>
      <td>PRP</td>
      <td>3</td>
      <td>nsubj</td>
    </tr>
    <tr>
      <th>2</th>
      <td>'s</td>
      <td>be</td>
      <td>VERB</td>
      <td>VBZ</td>
      <td>3</td>
      <td>aux</td>
    </tr>
    <tr>
      <th>3</th>
      <td>gon</td>
      <td>go</td>
      <td>VERB</td>
      <td>VBG</td>
      <td>0</td>
      <td>ROOT</td>
    </tr>
  </tbody>
</table>


## Dataset.skip

`Dataset.skip` is the inverse of `Dataset.just`, helping you quickly cut down your corpus to remove unwanted information. One common task is to remove punctuation tokens from our corpus:

```python
dtrt.skip.wordclass.PUNCT
```

## Chaining operations

Remember that in `buzz`, search results are simply subsets of your corpus. This means that it's always possible to further refine your searches, often eliminating the need to write complex queries.

For example, if we wanted to find the most common verbs used by Mookie's boss, Sal, we could do:

```python
dtrt.just.speaker.SAL.just.wordclass.VERB
```

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th></th>
      <th>w</th>
      <th>l</th>
      <th>x</th>
      <th>p</th>
      <th>g</th>
      <th>f</th>
    </tr>
    <tr>
      <th>file</th>
      <th>s</th>
      <th>i</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">05-sal's-famous-pizzeria</th>
      <th rowspan="2" valign="top">8</th>
      <th>3</th>
      <td>get</td>
      <td>get</td>
      <td>VERB</td>
      <td>VB</td>
      <td>0</td>
      <td>ROOT</td>
    </tr>
    <tr>
      <th>7</th>
      <td>sweep</td>
      <td>sweep</td>
      <td>VERB</td>
      <td>VB</td>
      <td>3</td>
      <td>conj</td>
    </tr>
    <tr>
      <th>14</th>
      <th>6</th>
      <td>shaddup</td>
      <td>shaddup</td>
      <td>VERB</td>
      <td>VB</td>
      <td>2</td>
      <td>acl</td>
    </tr>
    <tr>
      <th>19</th>
      <th>1</th>
      <td>Watch</td>
      <td>watch</td>
      <td>VERB</td>
      <td>VB</td>
      <td>0</td>
      <td>ROOT</td>
    </tr>
    <tr>
      <th>22</th>
      <th>1</th>
      <td>Can</td>
      <td>can</td>
      <td>VERB</td>
      <td>MD</td>
      <td>3</td>
      <td>aux</td>
    </tr>
  </tbody>
</table>

If the value you want to search by is not a valid Python name (i.e. it contains spaces, hyphens, etc.) you can use an alternative syntax:

```python
dtrt.just.setting('FRUIT-N-VEG DELIGHT')
```

## Dataset.see

with `Dataset.see`, you can pivot your data into a table of frequencies. To see a distribution of dependency function label by part-of-speech, you can simply do:

```python
dtrt.see.function.by.pos.to_html()
```

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>p</th>
      <th>nn</th>
      <th>.</th>
      <th>nnp</th>
      <th>prp</th>
      <th>dt</th>
      <th>in</th>
      <th>vbz</th>
      <th>rb</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>ROOT</th>
      <td>114</td>
      <td>0</td>
      <td>120</td>
      <td>9</td>
      <td>2</td>
      <td>11</td>
      <td>527</td>
      <td>18</td>
    </tr>
    <tr>
      <th>acl</th>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
    </tr>
    <tr>
      <th>acomp</th>
      <td>5</td>
      <td>0</td>
      <td>4</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>3</td>
    </tr>
    <tr>
      <th>advcl</th>
      <td>4</td>
      <td>0</td>
      <td>4</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>51</td>
      <td>1</td>
    </tr>
    <tr>
      <th>advmod</th>
      <td>2</td>
      <td>0</td>
      <td>4</td>
      <td>0</td>
      <td>3</td>
      <td>14</td>
      <td>0</td>
      <td>602</td>
    </tr>
    <tr>
      <th>agent</th>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>11</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>amod</th>
      <td>18</td>
      <td>0</td>
      <td>7</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>3</td>
    </tr>
    <tr>
      <th>appos</th>
      <td>45</td>
      <td>0</td>
      <td>39</td>
      <td>3</td>
      <td>12</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
    </tr>
  </tbody>
</table>


## Putting it all together

With a parsed and metadata-rich text, you can find, well, whatever you could possibly want. Let's say we're really interested in verb lemmata spoken inside Sal's Famous Pizzeria by anyone except Sal.

```python
verbs = dtrt.just.wordclass.VERB.just.setting("SAL'S FAMOUS PIZZERIA").skip.speaker.SAL
verbs.see.speaker.by.lemma.to_html()
```

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>speaker/verb</th>
      <th>be</th>
      <th>do</th>
      <th>get</th>
      <th>go</th>
      <th>have</th>
      <th>look</th>
      <th>see</th>
      <th>want</th>
      <th>will</th>
      <th>can</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>AHMAD</th>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>BUGGIN' OUT</th>
      <td>10</td>
      <td>3</td>
      <td>4</td>
      <td>1</td>
      <td>2</td>
      <td>0</td>
      <td>2</td>
      <td>2</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>CROWD</th>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>DA MAYOR</th>
      <td>7</td>
      <td>4</td>
      <td>1</td>
      <td>3</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>2</td>
      <td>0</td>
    </tr>
    <tr>
      <th>JADE</th>
      <td>12</td>
      <td>3</td>
      <td>2</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
    </tr>
  </tbody>
</table>

This is really just the basics, however. If you want to do more advanced kinds of frequency calculations, you'll want to use the `Dataset.table()` method, with documentation available [here](/en/latest/table).
