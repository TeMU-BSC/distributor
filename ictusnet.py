'''
Script to automatic distribute the documents to a given list of annotators.
Project: ICTUSnet
Version: 0.4
Date: 2019-10-10
Author of this script:
    Alejandro Asensio <alejandro.asensio@bsc.es>
Credits for the initial 10-overlappings algorithm ('documents_distribution.ods'):
    Ankush Rana <ankush.rana@bsc.es>

TODO Pick the documents in this proportion: 90% from AQuAS, 10% from SonEspases.
TODO Make this script able to be usable for each run (create options --complete-run and --individual-run).
'''

import os
import re
import random
import shutil
from collections import Counter
from typing import List
import click

# -----------------------------------------------------------------------------
# Modify these CONSTANTS if needed

EXTENSION = '.txt'
DOCS_DIR = 'dummy_docs'
BACKUP_SLUG = '_backup'
ANNOTATORS_DIR = 'annotators'
ANNOTATORS_NAMES = ('A', 'B', 'C', 'D')
RUNS_DIRS = {
    'training': ['01', '08'],
    'regular': [],
    'audit': ['02', '03', '04', '05', '06', '07']
}
TRAINING_BUNCH = 25
REGULAR_BUNCH = 50
AUDIT_BUNCH = 50

# The minimum amount of docs should be:
# (trainings * TRAINING_BUNCH) + (regulars * REGULAR_BUNCH) + (audits * AUDIT_BUNCH)
TOTAL_DUMMY_DOCS = 1400

# Documents overlapping map. This is a list of lists, which each list is made
# of tuples that follow the structure: (document_index, destination_annotator_index).
# Note: With 8 overlappings, each annotator has 4 documents that are equally compared with other annotators.
AUDIT_OVERLAPPINGS = [
    [(0, 1), (1, 1), (2, 3)],
    [(0, 2), (1, 2)],
    [(0, 3), (1, 3)],
    [(0, 0)]
]

# Percentage of document pickings by organization
PICKING = {
    'AQuAS': 0.9,
    'SonEspases': 0.1
}
# -----------------------------------------------------------------------------


@click.command()
@click.option('-d', '--docs-dir', default=DOCS_DIR,
              help='Directory that contains EXCLUSIVELY the documents to annotate.')
@click.option('--annotators', nargs=4, default=ANNOTATORS_NAMES,
              help='Names of the annotators.')
@click.option('--backup', is_flag=True, help='Perform a backup of the docs-dir.')
@click.option('--dummy', is_flag=True, default= True, help='Create dummy files to test this script.')
# @click.option('--complete-run', is_flag=True,
#               help='Assign the documents massively for ALL runs directories defined in `RUNS_DIRS` constant.')
# @click.option('--individual-run', ...,
#               help='')
# @click.option('--run-dir', prompt='New directory name for the run (e.g. `01`)',
#               help='Name for the new directory where the documents are going to be copied.')
def main(docs_dir: str, annotators: tuple, backup: bool,  dummy: bool):
    '''
    Distribute plain text documents into different directories regarding the following criteria.
    
    This script has two modes:
        [1] Individual mode (default): Distribute the documents ONLY for a concrete run,
            specificating the type of run: `training`, `regular` or `audit`.
        [2] Complete mode (`--complete-run` option): Distribute massively all the documents in the
            given docs_dir to some given annotators.

    The distribution of the documents depends on the defined run types defined for the project:
        [1] Training run: The exactly same documents for each annotator.
        [2] Regular run: A certain bunch of documents for each annotator, being the documents
            different among the annotators.
        [3] Audit run: A certain bunch of documents for each annotator, overlapping some of these
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
        '''Create some empty dummy files with numeric filenames to test this script.'''
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

    def count_target_annotator(audit_overlappings: List[List[tuple]], ann_index: int) -> int:
        '''Return the number of times that an annotator (ann_index) is present in the
        audit_overlappings map as a target for copying a document into the directory.'''
        target_annotators = list()
        for annotator_overlappings_list in audit_overlappings:
            for (src, tgt) in annotator_overlappings_list:
                target_annotators.append(tgt)
        return Counter(target_annotators)[ann_index]

    def training_run(training_dir: str):
        '''Assign exactly the same documents to each annotator training directory.'''
        training_docs = random.sample(docs_spool, k=TRAINING_BUNCH)
        [docs_spool.remove(doc) for doc in training_docs]
        for doc in training_docs:
            src = f'{docs_dir}/{doc}.txt'
            for annotator in annotators:
                dst = f'{ANNOTATORS_DIR}/{annotator}/{training_dir}/'
                assignments.append((src, dst))

    def regular_run(regular_dir: str):
        '''Assign a different bunch of documents to each annotator regular directory.'''
        for annotator in annotators:
            regular_docs = random.sample(docs_spool, k=REGULAR_BUNCH)
            [docs_spool.remove(doc) for doc in regular_docs]
            dst = f'{ANNOTATORS_DIR}/{annotator}/{regular_dir}/'
            for doc in regular_docs:
                src = f'{docs_dir}/{doc}.txt'
                assignments.append((src, dst))

    def audit_run(run_dir: str):
        '''Assign a bunch of documents to each annotator, but some of the documents are repeated (overlapped).'''
        for (ann_index, annotator) in enumerate(annotators):
            audit_docs = random.sample(docs_spool, k=AUDIT_BUNCH)
            [docs_spool.remove(doc) for doc in audit_docs]
            dst = f'{ANNOTATORS_DIR}/{annotator}/{run_dir}/'

            # Step 1: Remove as many docs as many times ann_index appears in the AUDIT_OVERLAPPINGS,
            # in order to make space for the further overlappings, maintaining regular the bunch amount of docs per directory.
            number_of_docs_to_remove = count_target_annotator(AUDIT_OVERLAPPINGS, ann_index)
            [audit_docs.pop() for i in range(number_of_docs_to_remove)]
            
            # Step 2: Assign the bunch of docs for each annotator
            for doc in audit_docs:
                src = f'{docs_dir}/{doc}.txt'
                assignments.append((src, dst))

            # Step 3: Assign (duplicate) the documents defined by their index to the target annotator
            for ann_overlapping in AUDIT_OVERLAPPINGS[ann_index]:          
                source_doc = f'{ANNOTATORS_DIR}/{annotator}/{run_dir}/{audit_docs[ann_overlapping[0]]}.txt'
                target_ann = f'{ANNOTATORS_DIR}/{annotators[ann_overlapping[1]]}/{run_dir}'
                assignments.append((source_doc, target_ann))

    # -------------------------------------------------------------------------

    # Preparation
    if dummy:
        _create_dummy_docs()
    
    if backup:
        backup_docs()
    
    if not os.path.exists(ANNOTATORS_DIR):
        create_annotators_dirs()
    
    # Load in memory of all documents to handle
    docs_spool = get_filenames(docs_dir)
    
    # List of tuples (doc_to_copy, destination_dir)
    assignments = list()

    # Execution of the runs using list comprehensions
    [training_run(run_dir) for run_dir in RUNS_DIRS.get('training')]
    [regular_run(run_dir) for run_dir in RUNS_DIRS.get('regular')]
    [audit_run(run_dir) for run_dir in RUNS_DIRS.get('audit')]

    # Write to disk: Copy the assigned source files to its corresponding target directories
    [shutil.copy2(src, dst) for (src, dst) in assignments]

    # -------------------------------------------------------------------------
    # Testing
    # Comment or uncomment the print or click.echo lines to see some stats for testing.

    # List of files per run
    #[print(root, len(files)) for root, dirs, files in os.walk(ANNOTATORS_DIR)]

    # Remaining docs spool
    #click.echo(len(docs_spool))

    # Result in memory
    #click.echo(len(assignments))

    # Distinct documents to annotate
    regex = r'(\d*)\.txt'
    pattern = re.compile(regex)
    string = str(assignments)
    filenames = re.findall(pattern, string)
    distinct_annotations = len(set(filenames))
    click.echo(distinct_annotations)


if __name__ == '__main__':
    main()
