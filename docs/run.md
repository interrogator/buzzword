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

The final part of the configuration process is to add the tool's settings. This can be done using a `.env` file, or by passing in command line options. If you want to use a `.env` file (as system adminstrators likely will), copy `.env.example` to `.env`, and modify settings as per your requirements. Most importantly, make sure `BUZZWORD_CORPORA_FILE` is set to the path for your `corpora.json`.

If a value isn't configured in `corpora.json`, the tool will look to `.env`, or to the provided command line options, for global settings.

Once your configuration files are set up, you can start the tool with:

```bash
python -m buzzword
# or
buzzword
```

With either command, you can also enter any the following options on the command line:

```
# global settings
--corpora-json          : corpora.json : path to corpora.json file used to load corpora
--no-load / -nl         : false        : do not load the full corpus into memory (for very large datasets/small machines, makes searches much slower)
--page-size / -p        : 25           : Rows per page of table
--env / -e              : none         : Use .env for configuration (pass path to .env file)
--debug                 : true         : run flask/dash in debug mode

# settings overridden by corpora.json

--drop-columns / -d     : none         : Comma separated list of corpus columns to drop before loading into tool
--max-dataset-rows / -m : none         : Cut corpus at this many lines before loading into tool
--table-size / -s       : 2000,200     : Max rows,columns to show in tables
--add-governor / -g     : false        : add governor token features to dataset. Slow to load and consumes more memory, but allows searching/showing governor features
```

If you pass a value for `--env`, make sure all these settings are in your `.env` file.
