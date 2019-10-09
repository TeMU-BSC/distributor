'''
Script to distribute massively all the documents to a given list of annotators.
Project: ICTUSnet
Version: 3
Date: 2019-10-09
Author:
    Alejandro Asensio <alejandro.asensio@bsc.es>
Credits for the overlappings algorithm ('documents_distribution.ods'):
    Ankush Rana <ankush.rana@bsc.es>

TODO hacer variable el numero de overlappings
TODO parameter prompt: How many trainings? How many regular? How many audits?
TODO we have to choose the documents in this proportion: 90% from AQuAS, 10% from SonEspases
'''

import os
import random
import shutil
from typing import Dict, List
import click

# -----------------------------------------------------------------------------
# Modify these CONSTANTS if needed
TOTAL_DUMMY_DOCS = 1500  # 1369 optimal
EXTENSION = '.txt'
DOCS_DIR = 'dummy'
BACKUP_SLUG = '_backup'
ANNOTATORS_DIR = 'annotators'
ANNOTATORS_NAMES = ('A', 'B', 'C', 'D')
RUNS_DIRS = {
    'training': ['01'],
    'regular': [],
    'audit': ['02', '03', '04', '05', '06', '07']
}
TRAINING_BUNCH = 25
REGULAR_BUNCH = 50
AUDIT_BUNCH = 50

# Documents overlapping map. This is a list of lists, which each list is made
# of tuples that follow the structure: (document_index, destination_annotator_index).

# Note: With 8 overlappings, each annotator has 4 documents that are equally compared with other annotators.
OVERLAPPINGS = [
    [(0, 1), (1, 1), (2, 3)],
    [(0, 2), (1, 2)],
    [(0, 3), (1, 3)],
    [(0, 1)]
]
# -----------------------------------------------------------------------------


@click.command()
@click.option('-d', '--docs-dir', default=DOCS_DIR,
              help='Directory that contains EXCLUSIVELY the documents to annotate.')
@click.option('--annotators', nargs=4, default=ANNOTATORS_NAMES,
              help='Names of the annotators.')
@click.option('--backup', is_flag=True, help='Perform a backup of the docs-dir.')
@click.option('--dummy', is_flag=True, help='Create dummy files to test this script.')
# @click.option('-t', '--training', default=RUNS_DIRS.get('training'), prompt='Training directories',
#               help='Name for the documents of training runs.')
# @click.option('-r', '--regular', default=RUNS_DIRS.get('regular'), prompt='Regular directories',
#               help='Name for the documents of regular runs.')
# @click.option('-a', '--audit', default=RUNS_DIRS.get('audit'), prompt='Audit directories',
#               help='Name for the documents of audit runs.')
def distribute_ictusnet_documents(docs_dir: str, annotators: tuple, backup: bool,  dummy: bool):
    '''Distribute massively all the documents in the given docs_dir to some given annotators.

    This distribution is adapted to the defined runs of the project:
        - Training: The exactly same documents for each annotator.
        - Regular: A certain bunch of documents for each annotator, being the documents different
                   among the annotators.
        - Audit: A certain bunch of documents for each annotator, overlapping some of these
                 documents, so it will be repeated documents among the annotators.
    '''

    backup_dir = f'{docs_dir}{BACKUP_SLUG}'

    # TODO Convert the possible click input options for training, regular and audit to tuples or lists
    # ...

    def backup_docs():
        '''Create a complete backup of the documents directory.'''
        if os.path.exists(backup_dir):
            return
        shutil.copytree(docs_dir, backup_dir)

    def _create_dummy_docs():
        '''Create some empty files to test this script.'''
        if not os.path.exists(docs_dir):
            os.makedirs(docs_dir)
        for dummy_doc in range(1, TOTAL_DUMMY_DOCS + 1):
            open(f'{docs_dir}/{dummy_doc}{EXTENSION}', 'w')

    def get_filenames(docs_dir: str) -> List[str]:
        '''Return the list of all filenames without extension inside the given directory.'''
        filenames = list()
        for root, dirs, files in os.walk(docs_dir):
            [filenames.append(int(f[:-4])) for f in files]
        return sorted(filenames, key=int)

    def create_annotators_dirs():
        '''Create one directory for each annotator in the working directory.'''
        flat_runs_dirs = [item for sublist in RUNS_DIRS.values() for item in sublist]
        for annotator in annotators:
            for run_dir in flat_runs_dirs:
                dirname = f'{ANNOTATORS_DIR}/{annotator}/{run_dir}/'
                if not os.path.exists(dirname):
                    os.makedirs(dirname)

    def training_run(training_dir: str):
        '''Assign exactly the same documents to each annotator training directory.'''
        training_docs = random.sample(docs_spool, k=TRAINING_BUNCH)
        [docs_spool.remove(doc) for doc in training_docs]
        for doc in training_docs:
            src = f'{docs_dir}/{doc}.txt'
            for annotator in annotators:
                dst = f'{ANNOTATORS_DIR}/{annotator}/{training_dir}'
                assignments.append((src, dst))

    def regular_run(regular_dir: str):
        '''Assign a different bunch of documents to each annotator regular directory.'''
        for annotator in annotators:
            regular_docs = random.sample(docs_spool, k=REGULAR_BUNCH)
            [docs_spool.remove(doc) for doc in regular_docs]
            dst = f'{ANNOTATORS_DIR}/{annotator}/{regular_dir}'
            for doc in regular_docs:
                src = f'{docs_dir}/{doc}.txt'
                assignments.append((src, dst))

    def audit_run(run_dir: str):
        '''Assign a bunch of documents to each annotator, but some of the documents are repeated (overlapped).'''
        for (ann_index, annotator) in enumerate(annotators):
            audit_docs = random.sample(docs_spool, k=AUDIT_BUNCH)
            [docs_spool.remove(doc) for doc in audit_docs]
            for (i, doc) in enumerate(audit_docs):
                src = f'{docs_dir}/{doc}.txt'
                dst = f'{ANNOTATORS_DIR}/{annotator}/{run_dir}'

                # Step 1: Assign the initial bunch of docs for each annotator
                assignments.append((src, dst))

            # # Step 2: Remove the defined amount of random docs to make space for the overlappings
            # docs_to_delete = random.sample(
            #     get_filenames(dst), k=OVERLAPPINGS[ann_index][1])
            # [os.remove(f'{dst}/{doc}.txt') for doc in docs_to_delete]

            # # Step 3.1: Select the defined amount of overlapping docs in the defined algorithm based on their index
            # docs_to_overlap = list()
            # [docs_to_overlap.append(get_filenames(dst)[i]) for i in OVERLAPPINGS[ann_index][0]]

            # # Step 3.2: Copy the selected overlapping docs to the defined target annotator
            # for (i, doc) in enumerate(docs_to_overlap):
            #     copy_src = f'{dst}/{doc}.txt'
            #     copy_dst = f'{ANNOTATORS_DIR}/{annotators[TARGET_ANNOTATOR[ann_index][i]]}/{run_dir}'
            #     # print(copy_src, copy_dst)
            #     shutil.copy2(copy_src, copy_dst)

    # -------------------------------------------------------------------------

    # Preparation
    if dummy:
        _create_dummy_docs()
    if backup:
        backup_docs()
    create_annotators_dirs()
    docs_spool = get_filenames(docs_dir)
    assignments = list()

    # Execution of the runs using list comprehensions
    [training_run(run_dir) for run_dir in RUNS_DIRS.get('training')]
    [regular_run(run_dir) for run_dir in RUNS_DIRS.get('regular')]
    [audit_run(run_dir) for run_dir in RUNS_DIRS.get('audit')]

    # Write to disk: Copy the assigned source files to its corresponding target directories
    [shutil.copy2(src, dst) for (src, dst) in assignments]

    # -------------------------------------------------------------------------
    # TESTING

    # Files per annotator run
    [print(root, dirs, len(files))
     for root, dirs, files in os.walk(ANNOTATORS_DIR)]

    # Remaining docs spool
    print(len(docs_spool))


if __name__ == '__main__':
    distribute_ictusnet_documents()
