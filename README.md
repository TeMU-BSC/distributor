# ICTUSnet Annotation Documents Distribution Script

This script distributes a given list of files (plain text documents) for 4
annotators.

It is a command-line script callable by python3 interpreter, build with
[Click](https://click.palletsprojects.com/en/7.x/).

The expected output is the creation of a main directory named `annotators` with
4 subdirectories, one for each annotator. The documents are randomly picked
from a clustered spool of documents, defined in a TSV file. In order to
preserve the reproducibility, before each call of `random.sample()` a seed is
set.

The distribution has 3 different bunch types:
- **Training**: The same documents are assigned to all annotators, so each
document will be annotated 4 times.
- **Regular**: A different bunch of documents are assigned to each annotator,
so each document will be annotated only once.
- **Audit**: A different bunch of documents are assigned to each annotator,
and some of these documents are deliberately repeated for other annotator, so
some documents will be annotated twice.

In order to preserve the original corpus directory, the documents are copied
(instead of moved).

The following steps are tested on **Ubuntu 18.04** operatig system.

## Requirements

- python3.7
- pip3
- pipenv - a wonderful package dependency and virtualenv managing tool

To ensure that your system has pip3 installed and updated, run the following commands:
```bash
sudo apt update && sudo apt install -y python3.7 python3-pip
python3.7 -m pip install --user --upgrade pip
python3.7 -m pip install --user --upgrade pipenv
```

## Set up the environment

1. Clone this repo and enter the project directory:
```bash
git clone https://github.com/TeMU-BSC/docs-distributor.git
cd docs-distributor
```

2. **A. Deterministic:** Install the explicit version of the packages listed in `Pipfile.lock`:
```bash
pipenv install --ignore-pipfile
```

2. **B. Development:** Alternatively, install the latest version of all packages as well as the development packages with `--dev` option:
```bash
pipenv install --dev
```

3. Activate the virtual environment:
```bash
pipenv shell
```

After that, you will see `(docs-distributor)` prepended to your prompt.

## Test the script
```bash
pytest
```

## Run the script
```bash
rm -rf annotators empty_corpus
python distributor.py clusters.tsv /path/to/real/corpus/ carmen eugenia isabel victoria
ls annotators
```

## Usage syntax options
```bash
python distributor.py --help
```

## Exit the virtual environment
```bash
exit
```
