## Running your own *buzzword*

*buzzword* is open-source, and designed to be shared. Server administrators are welcome to host their own instance of the tool. Individual users can also run the tool on their local machines, just like they would any other corpus tool.

If you want to run the tool with pre-existing datasets, you'll first need to have one parsed and ready to go. The *buzz* backend provides numerous ways of getting corpora parsed from your terminal, with comprehensive documentation available [here](https://buzz.readthedocs.io/en/latest/corpus/). In short, however, you can parse a dataset in your terminal with:

```bash
# because buzzword does not use constituencies, turn them off
python -m buzz.parse --cons-parser none ./path/to/data
# or
parse -cons-parser none ./path/to/data
```

Parsing will leave you with `./path/to/data-parsed`, a directory that mimics the original corpus, but with CONLL-U files instead of plain text.

Next, you need to configure *buzzword* to load this corpus (and potentially others) on startup. To do this, you should create a `corpora.json`, which tells the tool which corpora will be loaded into the tool. Copy `corpora.json.example` as `corpora.json`, and modify it to contain the corpora you want to show in the app.

The final part of the configuration process is to add the tool's settings. This can be done by modifying `buzzword/settings.py`. Most importantly, make sure `CORPORA_FILE` is set to the path for your `corpora.json`.

Once your configuration files are set up, you can start the tool with:

```bash
python -m buzzword
# or
buzzword
```
