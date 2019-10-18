# ICTUSnet Annotation Documents Distribution Script

This script distributes automatically a bunch of documents to some annotators.
The way of using it is as a command-line script, made with
[Click](https://click.palletsprojects.com/en/7.x/).

The expected output is the creation of a main directory named `annotators` with
4 subdirectories, one for each annotator. The documents are picked from a spool
of available documents, which are previously separated in clusters.

There are 3 different bunch types:
- **Training**: Assign exactly the same documents to each annotator.
- **Regular**: Assign a bunch of documents to each annotator being all of them
different from one annotator to other.
- **Audit**: Assign a bunch of documents to each annotator, but some of those
documents are repeated (overlapped) for other annotator, so for each audit some
documents will be annotated twice by different annotators.

The documents are copied to the corresponding new nested directories (not
moved from corpus directory), preserving the original corpus directory.

## System requirements

- python3.7
- pip
- pipenv - a wonderful package dependency managing tool

To ensure that your system has python3 and pip installed and updated,
run the following commands:
```bash
sudo apt update && sudo apt install -y python3.7 python3-pip
python3.7 -m pip install --user --upgrade pip
python3.7 -m pip install --user --upgrade pipenv
```
## Set up the environment

- Clone this repo and enter the project directory (`IctusNET` by default):
```bash
git clone https://github.com/TeMU-BSC/IctusNET.git
cd IctusNET
```

- Install the required packages listed in `Pipfile`:
```bash
pipenv install
```

- Alternatively, if you want to keep improving this script, install the
development packages with `--dev` option:
```bash
pipenv install --dev
```

- Activate the virtual environment:
```bash
pipenv shell
```

After that, you will see `(IctusNET)` prepended to your prompt.

## Run the script

- Example of creating empty files based on the filenames from the TSV
clustering file to just test the script:
```bash
python ictusnet.py --clusters-file labels_sup_umap_emb_8.tsv --test-mode
ls annotators
```

- Example of running the real distribution of the documents:
```bash
rm -rf annotators
python ictusnet.py --clusters-file labels_sup_umap_emb_8.tsv --corpus-dir /path/to/real/corpus/ --annotators carmen eugenia isabel victoria
ls annotators
```

## Tests
```
pytest
```

## Usage syntax options
```bash
python ictusnet.py --help
```
