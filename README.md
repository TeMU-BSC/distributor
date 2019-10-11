# ICTUSnet Annotation Documents Assignment Script

Script to automatic distribute the documents to a given list of annotators.

The expected output is the creation of several nested directories with the
documents ditributed as defined inside the `RUNS_DIRS` and `AUDIT_OVERLAPPINGS`
contants of the `ictusnet.py` command-line script.

The documents are not moved to the new nested directories, they are copied
instead, preserving the original documents directory.

Requirements:
- python3
- pip

Run:
```
# Enter the project directory (IctusNET by default)
$ cd IctusNET

# Install pipenv - a wonderful package dependency managing tool
$ pip install --user --upgrade pipenv

# Install requried dependencies listed in `Pipfile`
$ pipenv install

# Activate virtual environment with pipenv
$ pipenv shell

# Run the script
$ python ictusnet.py
```

Test:
```
$ pytest
```

Help:
```
$ python ictusnet.py --help
Usage: ictusnet.py [OPTIONS]

  Distribute plain text documents into different directories regarding the
  following criteria.

  This script has two modes: (i) Individual mode (default) distributes the
  documents ONLY for a concrete run, specificating the type of run:
  `training`, `regular` or `audit`; (ii) Complete mode (`--complete-run`
  option flag) distributes massively all the documents in the given
  source_dir to some given annotators.

  The distribution of the documents depends on the run types defined for the
  project: (i) Training type assigns the exactly same amount of documents to
  each annotator; (ii) Regular run assigns a certain bunch of documents for
  each annotator, being all the documents different among the annotators.
  (iii) Audit run assigns a certain bunch of documents for each annotator,
  overlapping some of them, so some documents will be annotated more than
  once.

Options:
  --source-dir TEXT               Directory that contains EXCLUSIVELY the
                                  plain text documents to annotate.
  -a, --annotators <TEXT TEXT TEXT TEXT>...
                                  Names of the 4 annotators separated by
                                  whitespace.
  --backup                        Create a backup of the --source-dir.
  --dummy                         Create dummy empty files to quickly test
                                  this script.
  --help                          Show this message and exit.
```

