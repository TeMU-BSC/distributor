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

Set up the environment:
```
# Enter the project directory (IctusNET by default)
$ cd IctusNET

# Install pipenv - a wonderful package dependency managing tool
$ pip install --user --upgrade pipenv

# Install requried dependencies listed in `Pipfile`
$ pipenv install

# Activate virtual environment with pipenv
$ pipenv shell
```

Run the script:
```
# Example for creating empty files in a dummy_docs directory
$ python ictusnet.py --clusters-file labels_sup_umap_emb_8.tsv --write-to-disk

# Example for executing the real distribution of the documents
$ python ictusnet.py --source-dir /path/to/real/docs/ --clusters-file labels_sup_umap_emb_8.tsv --write-to-disk
```

Test:
```
$ pytest
```

Usage:
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

  Moreover, the pickings of the documents depend on the defined percentages
  regarding the source (SonEspases and AQuAS, which has subclusters).

Options:
  --clusters-file TEXT            CSV file with `file cluster` format data.
  --delimiter TEXT                Delimiter for the CSV `--source-file`.
  --source-dir TEXT               Directory that contains EXCLUSIVELY the
                                  plain text documents to annotate.
  --annotators <TEXT TEXT TEXT TEXT>...
                                  Names of the 4 annotators separated by
                                  whitespace.
  --write-to-disk                 Copy files to the target annotators
                                  directories.
  --backup                        Create a backup of the `--source-dir`.
  --dummy                         Create dummy empty files to quickly test
                                  this script.
  --help                          Show this message and exit.
```

