# Distributor for Documents to Annotate

This script distributes a given list of files (plain text documents) among 4
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
git clone https://github.com/TeMU-BSC/distributor.git
cd distributor
```

2. Install the exact version of the packages listed in `Pipfile.lock`
(deterministic installation), including the ones for development:
```bash
pipenv install --ignore-pipfile --dev
```

3. Activate the virtual environment:
```bash
pipenv shell
```

After that, you will see `(distributor)` prepended to your prompt.

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

## Usage help
```
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

## Exit the virtual environment
```bash
exit
```

## System requirements testing using Docker

For system consistency purposes, we have prepared two dockerfiles to test the system requirements to run this script successfully.

Make sure you have Docker installed: https://docs.docker.com/install/linux/docker-ce/ubuntu/

Python3.7 (based on alpine) container:
```bash
docker build . --file Dockerfile-python-alpine --tag distributor-python-alpine
docker run distributor-python-alpine --name distributor-python-alpine-container
```

Ubuntu 18.04 container:
```bash
docker build . --file Dockerfile-ubuntu --tag distributor-ubuntu
docker run distributor-ubuntu --name distributor-ubuntu-container
```

Finally, you can remove the previous containers and images:
```bash
docker container rm distributor-python-alpine-container distributor-ubuntu-container 
docker image rm distributor-python-alpine distributor-ubuntu
```
