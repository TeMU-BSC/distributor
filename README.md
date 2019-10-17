# ICTUSnet Annotation Documents Assignment Script

Script that distributes automatically the documents to some annotators.

The expected output is the creation of several nested directories with the
documents ditributed as defined in CONSTANTS inside the `ictusnet.py`
command-line script made with [Click](https://click.palletsprojects.com/en/7.x/).

The documents are not moved to the new nested directories, they are copied
instead, preserving the original documents directory.

## Requirements:
- python3
- pip (or pip3)

## Set up the environment:

- Clone the repo and enter the project directory (`IctusNET` by default)
```bash
$ git clone https://github.com/TeMU-BSC/IctusNET.git
$ cd IctusNET
```

- Install pipenv - a wonderful package dependency managing tool
```bash
$ pip install --user --upgrade pipenv
```

- Install required dependencies listed in `Pipfile`
```bash
$ pipenv install
```

- Activate the virtual environment using pipenv
```bash
$ pipenv shell
```

## Run the script:

- Example for creating empty files in a dummy_docs directory
```bash
$ python ictusnet.py --clusters-file labels_sup_umap_emb_8.tsv --test-mode
```

- Example for executing the real distribution of the documents
```bash
$ python ictusnet.py --clusters-file labels_sup_umap_emb_8.tsv --corpus-dir /path/to/corpus/
```

## Test:
```
$ pytest
```

## Usage syntax:
```bash
$ python ictusnet.py --help
```
