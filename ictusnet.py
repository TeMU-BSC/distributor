'''
Script to assign massively all the documents to a given list of annotators.
Project: ICTUSnet
Version: 2
Date: 2019-10-08
Author: Alejandro Asensio <alejandro.asensio@bsc.es>
Credits for the overlapping algorithm: Ankush Rana <ankush.rana@bsc.es>
'''

import os
import random
import shutil
from typing import Dict, List
import click

# -----------------------------------------------------------------------------
# Modify these CONSTANTS if needed
TOTAL_RUNS = 10
RUNS = {
    'training': [1],
    'regular': [2, 3, 5, 6, 8, 9],
    'audit': [4, 7, 10]
}
TRAINING_BUNCH = 25
REGULAR_BUNCH = 50
AUDIT_BUNCH = 50
# -----------------------------------------------------------------------------


@click.command()
@click.option('-d', '--docs-path', default='dummy_docs/',
              help='Path that contains EXCLUSIVELY the documents to annotate.')
@click.option('-a', '--annotators-names', nargs=4,
              default=('annotator1', 'annotator2', 'annotator3', 'annotator4'),
              help='Names of the annotators.')
@click.option('--training-bunch', default=TRAINING_BUNCH,
              help='Number of documents for the Training run.')
@click.option('--regular-bunch', default=REGULAR_BUNCH,
              help='Number of documents for the Regular runs.')
@click.option('--audit-bunch', default=AUDIT_BUNCH,
              help='Number of documents for the Audit runs.')
def assign_ictusnet_documents(docs_path: str, annotators_names: tuple,
                              training_bunch: int, regular_bunch: int, audit_bunch: int):
    '''Assign massively all the documents in the given docs_path to some given annotators.

    This assignment is adapted to the defined runs of the project:
        - Training: The exactly same documents for each annotator.
        - Regular: A certain bunch of documents for each annotator, being the documents different among the annotators.
        - Audit: A certain bunch of documents for each annotator, overlapping some of these documents, so it will be repeated documents among the annotators.
    '''

    def get_filenames(docs_path: str) -> List[str]:
        '''Return the list of all filenames without .txt extension inside the directory given as a command line input.'''
        filenames = list()
        for root, dirs, files in os.walk(docs_path):
            [filenames.append(int(f[:-4])) for f in files]
        return sorted(filenames, key=int)

        # return os.listdir(docs_path)

    def create_annotators_dirs(annotators_names: tuple):
        '''Create one directory for each annotator in the working directory.'''
        for annotator in annotators_names:
            for run in range(1, TOTAL_RUNS + 1):
                dirname = f'{annotator}/{run}/'
                if run < 10:
                    dirname = f'{annotator}/0{run}/'
                os.makedirs(dirname)

    def training_run(docs_path: str, training_bunch: int, run_dir: str):
        '''Copy the exactly same documents to each annotator training directory.'''

        # Option 1: Deterministic choice
        training_docs = get_filenames(docs_path)[:training_bunch]

        # Option 2: Random choice
        #training_docs = random.choices(get_filenames(docs_path), k=TRAINING_BUNCH)

        for f in training_docs:
            src = f'{docs_path}/{f}.txt'
            for annotator in annotators_names:
                dst = f'{annotator}/{run_dir}'
                shutil.copy2(src, dst)

    def regular_run(regular_bunch: int):
        '''Assign a certain bunch of documents for each annotator, being the documents different among the annotators.'''
        shutil.move('dir_1/', 'backup/')

    def audit_run():
        '''Assign documents to the annotators with some of the documents overlapping, this is,
        some specific documents are present in more than one annotator.'''

        docs = get_filenames(docs_path)

        # Initialize the list for each annotator
        A = list()
        B = list()
        C = list()
        D = list()

        # Assign the bunch of docs per annotator
        bunch = 50

        # Define the overlappings map, regarding the separate bunch of each annotator
        # [Credits to Ankush Rana]
        overlappings = {
            'A': [0, 1, 6, 7, 8],
            'B': [2, 3],
            'C': [4, 5],
            'D': [],
        }

        # First annotator (A)
        A.extend(docs[:audit_bunch])
        overlapping_docs = [docs[o] for o in overlappings.get('A')]

        # Second annotator (B)
        # Append to B only the two first overlapping docs from A
        [B.append(A[i]) for i in overlappings.get('A')[:2]]
        B.extend(docs[audit_bunch:(audit_bunch * 2) - 2])

        # Third annotator (C)
        C.extend(docs[(audit_bunch * 2) - 2: audit_bunch * 3][:2])
        # Append to C all the defined overlapping docs from B
        [C.append(B[i]) for i in overlappings.get('B')]
        C.extend(docs[audit_bunch * 2:(audit_bunch * 3) - 4])

        # Fourth annotator (D)
        D.extend(docs[(audit_bunch * 3) - 4: audit_bunch * 4][:3])
        D.append(B[3])
        # Append to D all the defined overlapping docs from C
        [D.append(C[i]) for i in overlappings.get('C')]
        # Append to D only the three last overlapping docs from A
        [D.append(A[i]) for i in overlappings.get('A')[2:]]
        D.extend(docs[(audit_bunch * 3) - 1:(audit_bunch * 4 - 10)])

        run = {
            'A': A,
            'B': B,
            'C': C,
            'D': D
        }

        print(run)

    # -------------------------------------------------------------------------

    # Preparation

    result = dict()
    # create_annotators_dirs(annotators_names)
    
    # if not annotators_dirs_exist:
    #     create_annotators_dirs(annotators_names)

    # -------------------------------------------------------------------------

    # Execution of the runs

    training_run(docs_path, training_bunch, '01')
    
    # append the accumulative result to the dict...


    # audit_run()
if __name__ == '__main__':
    assign_ictusnet_documents()
