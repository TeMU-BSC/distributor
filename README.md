# ICTUSnet Annotation Documents Assignment Script

Script that distributes automatically the documents to some annotators.

The expected output is the creation of several nested directories with the
documents ditributed as defined in CONSTANTS inside the `ictusnet.py`
command-line script made with [Click](https://click.palletsprojects.com/en/7.x/).

The documents are not moved to the new nested directories, they are copied
instead, preserving the original documents directory.

## System requirements

- python3
- pip3
- pipenv - a wonderful package dependency managing tool

To ensure that your system has python3 and pip installed and updated, run the following commands:
```bash
$ sudo apt update && sudo apt install -y python3 python3-pip && python3 --version
$ pip3 install --user --upgrade pip && pip --version
$ pip3 install --user --upgrade pipenv && pipenv --version
```
## Set up the environment

- Clone this repo and enter the project directory (`IctusNET` by default):
```bash
$ git clone https://github.com/TeMU-BSC/IctusNET.git
$ cd IctusNET
```

- Install the required dependencies (also for development) listed in `Pipfile`:
```bash
$ pipenv install --dev
```

- Activate the virtual environment:
```bash
$ pipenv shell
```

## Run the script

- Example of creating empty files from the TSV clustering file to just test the script:
```bash
$ python ictusnet.py --clusters-file labels_sup_umap_emb_8.tsv --test-mode
```

- Example of running the real distribution of the documents:
```bash
$ python ictusnet.py --clusters-file labels_sup_umap_emb_8.tsv --corpus-dir /path/to/real/corpus/ --annotators carmen eugenia isabel victoria
```

## Tests
```
$ pytest
```

## Usage syntax options
```bash
$ python ictusnet.py --help
```
