'''
Script to assign massively all the documents to a given list of annotators.
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
TOTAL_RUNS = 10
RUNS_DIRS = {
    'training': ['01'],
    'regular': ['02', '03', '05', '06', '08', '09'],
    'audit': ['04', '07', '10']
}
TRAINING_BUNCH = 25
REGULAR_BUNCH = 50
AUDIT_BUNCH = 50
# For more details, see the spreadsheet representation made by Ankush Rana
OVERLAPPINGS = {
    'A': [0, 1, 6, 7, 8],
    'B': [2, 3],
    'C': [4, 5],
    'D': [],
}
# -----------------------------------------------------------------------------


@click.command()
@click.option('-d', '--docs-dir', default='dummy_docs',
              help='Directory that contains EXCLUSIVELY the documents to annotate.')
@click.option('-a', '--annotators-names', nargs=4,
              default=('annotator1', 'annotator2', 'annotator3', 'annotator4'),
              help='Names of the annotators.')
@click.option('--training-bunch', default=TRAINING_BUNCH,
              help='Number of documents for the Training run.')
@click.option('--regular-bunch', default=REGULAR_BUNCH,
              help='Number of documents for the Regular runs.')
@click.option('--audit-bunch', default=AUDIT_BUNCH,
              help='Number of documents for the Audit runs.')
@click.option('--backup', is_flag=True, help='Perform a backup of the docs-dir.')
@click.option('--dummy', is_flag=True, help='Create some dummy files.')
def assign_ictusnet_documents(docs_dir: str, annotators_names: tuple,
                              training_bunch: int, regular_bunch: int, audit_bunch: int,
                              backup: bool,  dummy: bool):
    '''Assign massively all the documents in the given docs_dir to some given annotators.

    This assignment is adapted to the defined runs of the project:
        - Training: The exactly same documents for each annotator.
        - Regular: A certain bunch of documents for each annotator, being the documents different
                   among the annotators.
        - Audit: A certain bunch of documents for each annotator, overlapping some of these
                 documents, so it will be repeated documents among the annotators.
    '''

    def _create_dummy_docs(docs=list(range(1, 1200 + 1)), extension='txt'):
        '''Create some empty files to test this script.'''
        if not os.path.exists(docs_dir):
            os.makedirs(docs_dir)
        for (index, doc) in enumerate(docs):
            f = open(f'{docs_dir}/{index + 1}.{extension}', 'w')

    def backup_docs():
        '''Create a complete backup of the documents directory.'''
        backup_dir = f'{docs_dir}_backup'
        if os.path.exists(backup_dir):
            return
        shutil.copytree(docs_dir, backup_dir)

    def get_filenames(docs_dir: str) -> List[str]:
        '''Return the list of all filenames without .txt extension inside the directory given as
        a command line input.'''
        filenames = list()
        for root, dirs, files in os.walk(docs_dir):
            [filenames.append(int(f[:-4])) for f in files]
        return sorted(filenames, key=int)

        # return os.listdir(docs_dir)  # Simple alternative with extensions

    def create_annotators_dirs():
        '''Create one directory for each annotator in the working directory.'''
        flat_runs_dirs = [item for sublist in RUNS_DIRS.values()
                          for item in sublist]
        for annotator in annotators_names:
            for run_dir in flat_runs_dirs:
                dirname = f'{annotator}/{run_dir}/'
                if not os.path.exists(dirname):
                    os.makedirs(dirname)

    def training_run(run_dir: str):
        '''Copy exactly the same documents to each annotator training directory.'''
        # Option 1: Deterministic choice
        training_docs = get_filenames(docs_dir)[:training_bunch]

        # Option 2: Random choice
        #training_docs = random.choices(get_filenames(docs_dir), k=TRAINING_BUNCH)

        for f in training_docs:
            src = f'{docs_dir}/{f}.txt'
            for annotator in annotators_names:
                dst = f'{annotator}/{run_dir}'
                shutil.copy2(src, dst)
            os.remove(src)

    def regular_run(run_dir: str):
        '''Assign a certain bunch of documents for each annotator, being the documents different
        among the annotators.'''
        # Option 1: Deterministic choice
        regular_docs = get_filenames(docs_dir)[:regular_bunch]

        # Option 2: Random choice
        #regular_docs = random.choices(get_filenames(docs_dir), k=REGULAR_BUNCH)

        for f in regular_docs:
            src = f'{docs_dir}/{f}.txt'
            for annotator in annotators_names:
                dst = f'{annotator}/{run_dir}'
                shutil.move(src, dst)

    def audit_run():
        '''Assign documents to the annotators with some of the documents overlapping, this is,
        some specific documents are present in more than one annotator.'''

        docs = get_filenames(docs_dir)

        # Initialize the list for each annotator
        A = list()
        B = list()
        C = list()
        D = list()

        # First annotator (A)
        A.extend(docs[:audit_bunch])

        # Second annotator (B)
        # Append to B only the two first overlapping docs from A
        [B.append(A[i]) for i in OVERLAPPINGS.get('A')[:2]]
        B.extend(docs[audit_bunch:(audit_bunch * 2) - 2])

        # Third annotator (C)
        C.extend(docs[(audit_bunch * 2) - 2: audit_bunch * 3][:2])
        # Append to C all the defined overlapping docs from B
        [C.append(B[i]) for i in OVERLAPPINGS.get('B')]
        C.extend(docs[audit_bunch * 2:(audit_bunch * 3) - 4])

        # Fourth annotator (D)
        D.extend(docs[(audit_bunch * 3) - 4: audit_bunch * 4][:3])
        D.append(B[3])
        # Append to D all the defined overlapping docs from C
        [D.append(C[i]) for i in OVERLAPPINGS.get('C')]
        # Append to D only the three last overlapping docs from A
        [D.append(A[i]) for i in OVERLAPPINGS.get('A')[2:]]
        D.extend(docs[(audit_bunch * 3) - 1:(audit_bunch * 4 - 10)])

        audit_run = {
            'A': A,
            'B': B,
            'C': C,
            'D': D
        }

        return audit_run

    # -------------------------------------------------------------------------

    # Preparation
    if dummy:
        _create_dummy_docs()
    if backup:
        backup_docs()
    create_annotators_dirs()

    # -------------------------------------------------------------------------

    # Execution of the runs using list comprehensions
    [training_run(run_dir) for run_dir in RUNS_DIRS.get('training')]
    [regular_run(run_dir) for run_dir in RUNS_DIRS.get('regular')]
    [audit_run(run_dir) for run_dir in RUNS_DIRS.get('audit')]

    # print(audit_run())


if __name__ == '__main__':
    assign_ictusnet_documents()
