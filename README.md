# ICTUSnet Document Assignment Script

Requires:
- python3

Run:
```
$ python ictusnet.py
```

Help:
```
$ python ictusnet.py --help

Usage: ictusnet.py [OPTIONS]

  Distribute massively all the documents in the given docs_dir to some given
  annotators.

  This distribution is adapted to the defined runs of the project:     -
  Training: The exactly same documents for each annotator.     - Regular: A
  certain bunch of documents for each annotator, being the documents
  different                among the annotators.     - Audit: A certain
  bunch of documents for each annotator, overlapping some of these
  documents, so it will be repeated documents among the annotators.

Options:
  -d, --docs-dir TEXT             Directory that contains EXCLUSIVELY the
                                  documents to annotate.
  -a, --annotators <TEXT TEXT TEXT TEXT>...
                                  Names of the annotators.
  --training-bunch INTEGER        Number of documents for the Training run.
  --regular-bunch INTEGER         Number of documents for the Regular runs.
  --audit-bunch INTEGER           Number of documents for the Audit runs.
  --backup                        Perform a backup of the docs-dir.
  --dummy                         Create dummy files to test this script.
  --help                          Show this message and exit.
```