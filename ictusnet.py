'''
Script to distribute massively all the documents to a given list of annotators.
Project: ICTUSnet
Version: 2
Date: 2019-10-08
Author: Alejandro Asensio <alejandro.asensio@bsc.es>
Credits for the overlappings algorithm: Ankush Rana <ankush.rana@bsc.es>
'''

import os
import random
import shutil
from typing import Dict, List
import click

# -----------------------------------------------------------------------------
# Modify these CONSTANTS if needed
TOTAL_DUMMY_DOCS = 2000
EXTENSION = '.txt'
TOTAL_RUNS = 10
RUNS_DIRS = {
    'training': ['01'],
    'regular': ['02', '03', '05', '06', '08', '09'],
    'audit': ['04', '07', '10']
}
TRAINING_BUNCH = 25
REGULAR_BUNCH = 50
AUDIT_BUNCH = 50
# OVERLAPPINGS = {
#     'A': [0, 1, 6, 7, 8],
#     'B': [2, 3],
#     'C': [4, 5],
#     'D': [],
# }
OVERLAPPINGS = {
    'A': [0, 1, 6, 7, 8],
    'B': [0, 1],
    'C': [0, 1],
    'D': [],
}
# For more details, see the spreadsheet representation made by Ankush Rana
# File: 'documents_distribution.ods'
# -----------------------------------------------------------------------------


@click.command()
@click.option('-d', '--docs-dir', default='dummy_docs',
              help='Directory that contains EXCLUSIVELY the documents to annotate.')
@click.option('-a', '--annotators', nargs=4, default=('A', 'B', 'C', 'D'),
              help='Names of the annotators.')
@click.option('--training-bunch', default=TRAINING_BUNCH,
              help='Number of documents for the Training run.')
@click.option('--regular-bunch', default=REGULAR_BUNCH,
              help='Number of documents for the Regular runs.')
@click.option('--audit-bunch', default=AUDIT_BUNCH,
              help='Number of documents for the Audit runs.')
@click.option('--backup', is_flag=True, help='Perform a backup of the docs-dir.')
@click.option('--dummy', is_flag=True, help='Create dummy files to test this script.')
def distribute_ictusnet_documents(docs_dir: str, annotators: tuple,
                                  training_bunch: int, regular_bunch: int, audit_bunch: int,
                                  backup: bool,  dummy: bool):
    '''Distribute massively all the documents in the given docs_dir to some given annotators.

    This distribution is adapted to the defined runs of the project:
        - Training: The exactly same documents for each annotator.
        - Regular: A certain bunch of documents for each annotator, being the documents different
                   among the annotators.
        - Audit: A certain bunch of documents for each annotator, overlapping some of these
                 documents, so it will be repeated documents among the annotators.
    '''

    def _create_dummy_docs():
        '''Create some empty files to test this script.'''
        if not os.path.exists(docs_dir):
            os.makedirs(docs_dir)
        for dummy_doc in range(1, TOTAL_DUMMY_DOCS + 1):
            open(f'{docs_dir}/{dummy_doc}{EXTENSION}', 'w')

    def backup_docs():
        '''Create a complete backup of the documents directory.'''
        backup_dir = f'{docs_dir}_backup'
        if os.path.exists(backup_dir):
            return
        shutil.copytree(docs_dir, backup_dir)

    def get_filenames(docs_dir: str) -> List[str]:
        '''Return the list of all filenames without extension inside the given directory.'''
        # Simple alternative with extensions
        # return os.listdir(docs_dir)

        # Refined version sorting the files by numeric criteria
        filenames = list()
        for root, dirs, files in os.walk(docs_dir):
            [filenames.append(int(f[:-4])) for f in files]
        return sorted(filenames, key=int)

    def create_annotators_dirs():
        '''Create one directory for each annotator in the working directory.'''
        flat_runs_dirs = [item for sublist in RUNS_DIRS.values()
                          for item in sublist]
        for annotator in annotators:
            for run_dir in flat_runs_dirs:
                dirname = f'annotators/{annotator}/{run_dir}/'
                if not os.path.exists(dirname):
                    os.makedirs(dirname)

    def training_run(run_dir: str):
        '''Copy exactly the same documents to each annotator training directory.'''
        training_docs = get_filenames(docs_dir)[:training_bunch]
        # training_docs = random.choices(get_filenames(docs_dir), k=TRAINING_BUNCH)
        for f in training_docs:
            src = f'{docs_dir}/{f}.txt'
            for annotator in annotators:
                dst = f'annotators/{annotator}/{run_dir}'
                shutil.copy2(src, dst)
            os.remove(src)

    def regular_run(run_dir: str):
        '''Distribute a certain bunch of documents for each annotator, being the documents
        different among the annotators.'''
        for annotator in annotators:
            regular_docs = get_filenames(docs_dir)[:regular_bunch]
            # regular_docs = random.choices(get_filenames(docs_dir), k=REGULAR_BUNCH)
            dst = f'annotators/{annotator}/{run_dir}'
            for f in regular_docs:
                src = f'{docs_dir}/{f}.txt'
                shutil.move(src, dst)

    def audit_run(run_dir: str):
        '''Distribute documents to the annotators with some of the documents overlapping, this is,
        some specific documents are present in more than one annotator.'''
        for (index, annotator) in enumerate(annotators):
            audit_docs = get_filenames(docs_dir)[:audit_bunch]

            for (i, f) in enumerate(audit_docs):
                src = f'{docs_dir}/{f}.txt'
                dst = f'annotators/{annotator}/{run_dir}'

                # Move the initial bunch of docs for each annotator
                shutil.move(src, dst)

                # Remove 0 files fron first annotator,
                # remove 2 files from second and third annotator,
                # remove 5 files from fourth annotator.
                docs_to_remove = 0
                if index + 1 == 1:
                    break
                elif index + 1 == 2 or index + 1 == 3:
                    docs_to_remove = 2
                elif index + 1 == 4:
                    docs_to_remove = 5
                # Execute de deletion
                [os.remove(f'{dst}/{f}.txt') for x in range(docs_to_remove)]

    # -------------------------------------------------------------------------

    # Preparation
    if dummy:
        _create_dummy_docs()
    if backup:
        backup_docs()
    create_annotators_dirs()

    # Execution of the runs using list comprehensions
    [training_run(run_dir) for run_dir in RUNS_DIRS.get('training')]
    [regular_run(run_dir) for run_dir in RUNS_DIRS.get('regular')]
    [audit_run(run_dir) for run_dir in RUNS_DIRS.get('audit')]

    # print(get_filenames())


if __name__ == '__main__':
    distribute_ictusnet_documents()
