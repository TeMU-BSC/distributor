# Distributor -- for Documents to Annotate

This script distributes a given list of files (plain text documents) among
**4 annotators**.

It is a command-line script callable by python3 interpreter, build with
[Click](https://click.palletsprojects.com/en/7.x/).

The expected output is the creation of a main directory named `annotators` with
4 subdirectories, one for each annotator. The documents are randomly picked
from a clustered spool of documents, defined in `clusters/labels_sup_umap_emb_8.tsv`.
In order to get a successful run if this script, the filanames listed in that
TSV file must exist in the further "real_corpus" directory.

In order to preserve the reproducibility, a seed is set before each call of `random.sample()`.

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

## Set up the environment

Clone this github repo, enter the project directory and simply run the
`setup.sh` bash script to set up all the requirements:

```bash
git clone https://github.com/TeMU-BSC/distributor.git
cd distributor
source ./setup.sh
```

## Run the main script

### For final users

- Install, using the system `python3` interpreter, the exact version of the packages listed in `Pipfile.lock` (deterministic installation):

```bash
pipenv install --three --ignore-pipfile
```

- Activate the virtual environment:

```bash
pipenv shell
```

After that, you will see `(distributor)` prepended to your prompt.

- Run the script

```bash
python distributor.py clusters.tsv /path/to/real/corpus/ carmen eugenia isabel victoria
```

- Check the new directories and files created inside `annotators` directory:

```bash
tree -d annotators
```

- Exit the virtual environment managed by pipenv

```bash
exit
```

### For developers

- Install, using the system `python3` interpreter, the latest version of the packages listed in `Pipfile` (non-deterministic installation), including the packages for development:

```bash
pipenv install --three --dev
```

- Activate the virtual environment:

```bash
pipenv shell
```

After that, you will see `(distributor)` prepended to your prompt.

- Test the script using pytest

```bash
pytest
```

- Check the new dummy directories and files created inside `annotators` directory:

```bash
tree -d annotators
rm -rf annotators empty_corpus
```

- Exit the virtual environment managed by pipenv

```bash
exit
```

## Usage

```bash
python distributor.py --help
Usage: distributor.py [OPTIONS] CLUSTERS_FILE CORPUS ANNOTATORS...

  Distribute plain text documents into subdirectories the CONSTANTS defined
  at the beggining of this function.

  The pickings of the documents depend on the percentages calculated
  dynamically regarding the representativeness of previously clustered
  SonEspases and AQuAS documents.

Options:
  --help  Show this message and exit.
```

## (Optional) Testing of system requirements using Docker

For consistency purposes, we have prepared two dockerfiles to test the system
requirements in order to run this script successfully.

Make sure you have Docker installed: <https://docs.docker.com/install/linux/docker-ce/ubuntu/>

Python3.7 (based on alpine) container:

```bash
docker build . --file Dockerfile-python-alpine --tag distributor-python-alpine
docker run --name distributor-python-alpine-container distributor-python-alpine
```

Ubuntu 18.04 container:

```bash
docker build . --file Dockerfile-ubuntu --tag distributor-ubuntu
docker run --name distributor-ubuntu-container distributor-ubuntu
```

Finally, you can remove the previous containers and images:

```bash
docker container rm distributor-python-alpine-container distributor-ubuntu-container
docker image rm distributor-python-alpine distributor-ubuntu
```
