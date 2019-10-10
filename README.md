# ICTUSnet Annotation Documents Assignment Script

Script to automatic distribute the documents to a given list of annotators.

Requires:
- python3
- pip

Run:
```
$ cd ictusnet
$ pip install -U pipenv
$ pipenv shell
$ python ictusnet.py
```

Help:
```
$ python ictusnet.py --help

Usage: ictusnet.py [OPTIONS]

  Distribute plain text documents into different directories regarding the
  following criteria.

  This script has two modes:     [1] Individual mode (default): Distribute
  the documents ONLY for a concrete run,         specificating the type of
  run: `training`, `regular` or `audit`.     [2] Complete mode (`--complete-
  run` option): Distribute massively all the documents in the         given
  docs_dir to some given annotators.

  The distribution of the documents depends on the defined run types defined
  for the project:     [1] Training run: The exactly same documents for each
  annotator.     [2] Regular run: A certain bunch of documents for each
  annotator, being the documents         different among the annotators.
  [3] Audit run: A certain bunch of documents for each annotator,
  overlapping some of these         documents, so it will be repeated
  documents among the annotators.

Options:
  -d, --docs-dir TEXT             Directory that contains EXCLUSIVELY the
                                  documents to annotate.
  --annotators <TEXT TEXT TEXT TEXT>...
                                  Names of the annotators.
  --backup                        Perform a backup of the docs-dir.
  --dummy                         Create dummy files to test this script.
  --help                          Show this message and exit.
```

