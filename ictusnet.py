'''
Script to automatic distribute the documents to a given list of annotators.

Project: ICTUSnet
Version: 0.4
Date: 2019-10-10
Author of this script:
    Alejandro Asensio <alejandro.asensio@bsc.es>
Credits for the initial 10-overlappings algorithm:
    Ankush Rana <ankush.rana@bsc.es>

TODO Make this script able to be usable for each run (create options
--complete-run and --individual-run).
TODO Pick the documents in this proportion: 90% from AQuAS, 10% from SonEspases.
'''

import os
import re
import random
import shutil

import click

import utils

# Pylint disables

# By codes


# Or by symbolic message
# pylint: disable=expression-not-assigned
# pylint: disable=no-value-for-parameter


# -----------------------------------------------------------------------------
# Modify these CONSTANTS if needed

ANNOTATORS = {
    'root': 'annotators',
    'dummy_names': ('A', 'B', 'C', 'D'),
}
RUN_TYPES = {
    'training': {
        'dirs': ['01', '08'],
        'bunch': 25
    },
    'regular': {
        'dirs': [],
        'bunch': 50
    },
    'audit': {
        'dirs': ['02', '03', '04', '05', '06', '07'],
        'bunch': 50
    }
}

# Constants for dummy data

# The minimum amount of dummy docs should be:
# (trainings * TRAINING_BUNCH) + (regulars * REGULAR_BUNCH) + (audits * AUDIT_BUNCH)
TOTAL_DUMMY_DOCS = 1400
DUMMY_EXTENSION = '.txt'
DUMMY_DIR = 'dummy_docs'

# Documents overlapping map. This is a list of lists, which each list is made
# of tuples that follow the structure: (document_index, destination_annotator_index).
# Note: With 8 overlappings, each annotator has 4 documents that are equally
# compared with other annotators.
AUDIT_OVERLAPPINGS = [
    [(0, 1), (1, 1), (2, 3)],
    [(0, 2), (1, 2)],
    [(0, 3), (1, 3)],
    [(0, 0)]
]

# Percentage of document pickings by organization
# Marta dice que 0.98, 0.02 (sonespases estan muy mal escritos)
PICKING = {'AQuAS': 0.9, 'SonEspases': 0.1}
# -----------------------------------------------------------------------------


@click.command()
@click.option('--source-dir',
              help='Directory that contains EXCLUSIVELY the plain text documents to annotate.')
@click.option('--annotators', '-a', nargs=4, default=ANNOTATORS['dummy_names'],
              help='Names of the 4 annotators separated by whitespace.')
# @click.option('--annotators', '-a', multiple=True, help='Name of an annotator.')
@click.option('--backup', is_flag=True,
              help='Create a backup of the `--source-dir`.')
@click.option('--dummy', is_flag=True,
              help='Create dummy empty files to quickly test this script.')
# @click.option('--complete-run', is_flag=True,
#               help='Assign the documents massively for ALL runs directories defined in
#               `RUN_TYPES[<type>]['dirs']` constant.')
# @click.option('--run-type', prompt=True,
#               type=click.Choice(['training', 'regular', 'audit'], case_sensitive=False))
# @click.option('--run-dir', prompt='New directory name for the run (e.g. `01`)',
# help='Name for the new directory where the documents are going to be
# copied.')
def assign_docs(source_dir: str, annotators: tuple, backup: bool, dummy: bool):
    '''
    Distribute plain text documents into different directories regarding the following criteria.

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
    '''

    # Flags handling

    if dummy:
        utils.create_empty_files_se(
            DUMMY_DIR, TOTAL_DUMMY_DOCS, DUMMY_EXTENSION)
        source_dir = DUMMY_DIR

    if backup:
        backup_dir = f'{source_dir}_backup'
        utils.create_docs_backup_se(source_dir, backup_dir)

    # -------------------------------------------------------------------------

    # Directory tree preparation

    # 1. Collect the dir names of all annotators
    all_run_dirs = [RUN_TYPES[run_type]['dirs']
                    for run_type in RUN_TYPES]

    # 2. Convert a list of lists to a flat list
    all_flat_run_dirs = [item for sublist in all_run_dirs for item in sublist]

    # 3. Create the directory tree (empty tree)
    utils.create_dirs_tree_se(
        ANNOTATORS['root'], annotators, all_flat_run_dirs)

    # -------------------------------------------------------------------------

    # Variables initialization

    # Load in memory of all documents to handle
    docs_spool = utils.get_files(source_dir)

    # List of tuples (file_to_copy, destination_dir)
    assignments = list()

    # -------------------------------------------------------------------------

    # Define 3 different functions for each run type

    def training_run(training_dir: str):
        '''Assign exactly the same documents to each annotator training directory.'''
        training_docs = random.sample(
            docs_spool, k=RUN_TYPES['training']['bunch'])
        [docs_spool.remove(doc) for doc in training_docs]
        for doc in training_docs:
            src = os.path.join(source_dir, doc)
            for annotator in annotators:
                dst = os.path.join(ANNOTATORS["root"], annotator, training_dir)
                assignments.append((src, dst))

    def regular_run(regular_dir: str):
        '''Assign a different bunch of documents to each annotator regular directory.'''
        for annotator in annotators:
            regular_docs = random.sample(
                docs_spool, k=RUN_TYPES['regular']['bunch'])
            [docs_spool.remove(doc) for doc in regular_docs]
            dst = os.path.join(ANNOTATORS["root"], annotator, regular_dir)
            for doc in regular_docs:
                src = os.path.join(source_dir, doc)
                assignments.append((src, dst))

    def audit_run(audit_dir: str):
        '''Assign a bunch of documents to each annotator, but some of the
        documents are repeated (overlapped).'''
        for (ann_index, annotator) in enumerate(annotators):
            audit_docs = random.sample(
                docs_spool, k=RUN_TYPES['audit']['bunch'])
            [docs_spool.remove(doc) for doc in audit_docs]
            dst = os.path.join(ANNOTATORS["root"], annotator, audit_dir)

            # Step 1: Remove as many docs as many times ann_index appears in
            # the AUDIT_OVERLAPPINGS, in order to make space for the further
            # overlappings, maintaining regular the bunch amount of docs per
            # directory.
            number_of_docs_to_remove = utils.count_occurrences_in_list_of_list_of_tuples(
                AUDIT_OVERLAPPINGS, ann_index)
            [audit_docs.pop() for i in range(number_of_docs_to_remove)]

            # Step 2: Assign the bunch of docs for each annotator
            for doc in audit_docs:
                src = os.path.join(source_dir, doc)
                assignments.append((src, dst))

            # Step 3: Assign (duplicate) the documents defined by their index
            # to the target annotator
            for ann_overlapping in AUDIT_OVERLAPPINGS[ann_index]:
                source_doc = os.path.join(
                    ANNOTATORS["root"], annotator, audit_dir, audit_docs[ann_overlapping[0]])
                target_ann = os.path.join(
                    ANNOTATORS["root"], annotators[ann_overlapping[1]], audit_dir)
                assignments.append((source_doc, target_ann))

    # -------------------------------------------------------------------------

    # Execution of the runs using list comprehensions
    [training_run(run_dir) for run_dir in RUN_TYPES['training']['dirs']]
    [regular_run(run_dir) for run_dir in RUN_TYPES['regular']['dirs']]
    [audit_run(run_dir) for run_dir in RUN_TYPES['audit']['dirs']]

    # Write to disk: Copy the selected files to the target directories
    [shutil.copy2(src, dst) for (src, dst) in assignments]

    # -------------------------------------------------------------------------

    # Testing - Comment or uncomment the lines to output some stats.

    [print(root, len(files))
     for root, dirs, files in os.walk(ANNOTATORS['root'])]
    print('Unused documents:', len(docs_spool))
    print('Total number of annotations:', len(assignments))

    # Distinct documents to annotate
    regex = r'(\d*)\.txt'
    pattern = re.compile(regex)
    string = str(assignments)
    filenames = re.findall(pattern, string)
    distinct_annotations = len(set(filenames))
    print('Number of distinct annotations:', distinct_annotations)


if __name__ == '__main__':
    assign_docs()
