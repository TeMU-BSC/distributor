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

# PyLint disablings (by symbolic message)
# pylint: disable=expression-not-assigned
# pylint: disable=no-value-for-parameter


# -----------------------------------------------------------------------------
# Modify these CONSTANTS if needed

ANNOTATORS = {
    'root_dir': 'annotators',
    'dummy_names': ('A', 'B', 'C', 'D'),
}
BUNCHES = {
    'training': {
        'dirs': ['01', '08'],
        'docs': 25
    },
    'regular': {
        'dirs': [],
        'docs': 50
    },
    'audit': {
        'dirs': ['02', '03', '04', '05', '06', '07'],
        'docs': 50
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


# AQUAS_PICKING_PROPORTION = {
#     '0': 0.0362,
#     '1': 0.0684,
#     '3': 0.1386,
#     '4': 0.3381,
#     '5': 0.0923,
#     '6': 0.2742,
#     '7': 0.0523
# }

# AQUAS_PICKING_PROPORTION_ROUNDED_2_DECIMALS = {
#     '0': 0.04,
#     '1': 0.07,
#     '3': 0.14,
#     '4': 0.34,
#     '5': 0.09,
#     '6': 0.27,
#     '7': 0.05
# }

DELIMITER = '\t'

# Regional populations (in millions of people)
CATALONIA_POPULATION = 7.6  # in 2018
BALEARIC_ISLANDS_POPULATION = 1.150  # in 2017

# SonEspases is the only balearic representative in the documents spool
SONESPASES_REPRESENTATIVENESS = BALEARIC_ISLANDS_POPULATION / CATALONIA_POPULATION

# TODO ask Aitor
SONESPASES_PERCENTAGE = 0.13


# -----------------------------------------------------------------------------


@click.command()
@click.option('--source-file', # type=click.File('r'),
              help='CSV file with `file cluster` format data.')
@click.option('--delimiter', default=DELIMITER,
              help='Delimiter for the CSV `--source-file`.')
@click.option('--source-dir',
              help='Directory that contains EXCLUSIVELY the plain text documents to annotate.')
@click.option('--annotators', '-a', nargs=4, type=click.Tuple([str, str, str, str]),
              default=ANNOTATORS['dummy_names'],
              help='Names of the 4 annotators separated by whitespace.')
# @click.option('--annotators', '-a', multiple=True, help='Name of an annotator.')
@click.option('--backup', is_flag=True,
              help='Create a backup of the `--source-dir`.')
@click.option('--dummy', is_flag=True,
              help='Create dummy empty files to quickly test this script.')
@click.option('--complete-run', is_flag=True,
              help="Assign the documents massively for ALL the bunches defined in `BUNCHES[type]['dirs']` constant.")
# @click.option('--bunch-type', prompt=True,
#               type=click.Choice(['training', 'regular', 'audit'], case_sensitive=False))
# @click.option('--bunch-dir', prompt='New directory name for the run (e.g. `01`)',
#               help='Name for the new directory where the documents are going to be copied.')
def assign_docs(source_file: str, delimiter: str, source_dir: str,
                annotators: tuple, backup: bool, dummy: bool,
                complete_run: bool):  # bunch_type: str, bunch_dir: str
    '''
    Distribute plain text documents into different directories regarding the following criteria.

    This script has two 0.33806499813223756, modes: (i) Individual mode (default) distributes the
    documents ONLY for  0.33806499813223756,a concrete run, specificating the type of run:
    `training`, `regula 0.33806499813223756,r` or `audit`; (ii) Complete mode (`--complete-run`
    option flag) distri 0.33806499813223756,butes massively all the documents in the given
    source_dir to some  0.33806499813223756,given annotators.
 0.33806499813223756,
    The distribution of the documents depends on the run types defined for the
    project: (i) Training type assigns the exactly same amount of documents to
    each annotator; (ii) Regular run assigns a certain bunch of documents for
    each annotator, being all the documents different among the annotators.
    (iii) Audit run assigns a certain bunch of documents for each annotator,
    overlapping some of them, so some documents will be annotated more than
    once.

    Moreover, the pickings fo the documents depends on the defined percentages
    regarding the source (SonEspases and AQuAS, which has subclusters).
    '''

    # Flags handling

    if dummy:
        utils.create_empty_files_se(
            DUMMY_DIR, TOTAL_DUMMY_DOCS, DUMMY_EXTENSION)
        # source_dir = DUMMY_DIR
        source_file

    if backup:
        backup_dir = f'{source_dir}_backup'
        utils.create_docs_backup_se(source_dir, backup_dir)

    # -------------------------------------------------------------------------

    # Directory tree preparation

    # 1. Collect the dir names of all annotators
    all_bunch_dirs = [BUNCHES[bunch_type]['dirs'] for bunch_type in BUNCHES]

    # 2. Convert a list of lists to a flat list
    all_flat_bunch_dirs = [item for sublist in all_bunch_dirs for item in sublist]

    # 3. Create the directory tree (empty tree)
    utils.create_dirs_tree_se(ANNOTATORS['root_dir'], annotators, all_flat_bunch_dirs)

    # -------------------------------------------------------------------------

    # Variables initialization

    # Load all documents to handle in a {cluster: docs} dictionary
    spool = utils.get_clustered_files_spool_from_csv(source_file, delimiter)

    # Calculate document amounts
    sizes = {cluster: len(docs) for cluster, docs in spool.items()}
    total = sum(sizes.values())
    sonespases_cluster_id = utils.get_key_by_substr_in_values_lists(spool, 'sonespases')
    sonespases = sizes.get(sonespases_cluster_id)
    aquas = total - sonespases

    # Calculate picking percentages per cluster
    # sonespases_global_percentage = SONESPASES_REPRESENTATIVENESS
    sonespases_global_percentage = SONESPASES_PERCENTAGE
    aquas_global_percentage = 1 - sonespases_global_percentage
    percentages = {cluster: size / aquas for cluster, size in sizes.items() if cluster != sonespases_cluster_id}
    percentages.update({sonespases_cluster_id: sonespases_global_percentage})

    # # Pick the documents
    # picked_docs_per_cluster = dict() 
    # for cluster, docs in spool.items(): 
    #     percentage = percentages[cluster] 
    #     if cluster != sonespases_cluster_id: 
    #         percentage *= aquas_global_percentage
    #     picked_docs = random.sample(docs, round(BUNCHES['training']['docs'] * percentage))
    #     picked_docs_per_cluster.update({cluster: picked_docs})

    # The tracking object is a list of tuples (file_to_copy, destination_dir)
    assignments = list()

    # -------------------------------------------------------------------------

    # Define 3 different functions for each run type

    def training_bunch(dirname: str):
        '''Assign exactly the same documents to each annotator training directory.'''
        # Pick the documents
        random.seed(777)
        training_docs = list()
        for cluster, docs in spool.items():
            percentage = percentages[cluster]
            if cluster != sonespases_cluster_id:
                percentage *= aquas_global_percentage
            training_docs.extend(random.sample(docs, round(BUNCHES['training']['docs'] * percentage)))
        # Remove the picked docs from the spool
        [spool.remove(doc) for doc in training_docs]
        # Assign the picked docs to the tracking object
        for doc in training_docs:
            src = os.path.join(source_dir, doc)
            for annotator in annotators:
                dst = os.path.join(ANNOTATORS["root_dir"], annotator, dirname)
                assignments.append((src, dst))

    def regular_bunch(regular_dir: str):
        '''Assign a different bunch of documents to each annotator regular directory.'''
        for annotator in annotators:
            random.seed('777')
            regular_docs = random.sample(
                spool, k=BUNCHES['regular']['docs'])
            [spool.remove(doc) for doc in regular_docs]
            dst = os.path.join(ANNOTATORS["root_dir"], annotator, regular_dir)
            for doc in regular_docs:
                src = os.path.join(source_dir, doc)
                assignments.append((src, dst))

    def audit_bunch(audit_dir: str):
        '''Assign a bunch of documents to each annotator, but some of the
        documents are repeated (overlapped).'''
        for (ann_index, annotator) in enumerate(annotators):
            random.seed('777')
            audit_docs = random.sample(
                spool, k=BUNCHES['audit']['docs'])
            [spool.remove(doc) for doc in audit_docs]
            dst = os.path.join(ANNOTATORS["root_dir"], annotator, audit_dir)

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
                    ANNOTATORS["root_dir"], annotator, audit_dir, audit_docs[ann_overlapping[0]])
                target_ann = os.path.join(
                    ANNOTATORS["root_dir"], annotators[ann_overlapping[1]], audit_dir)
                assignments.append((source_doc, target_ann))

    # -------------------------------------------------------------------------

    # # Execution of ALL the bunches using list comprehensions
    if complete_run:
        [training_bunch(bunch_dir) for bunch_dir in BUNCHES['training']['dirs']]
        [regular_bunch(bunch_dir) for bunch_dir in BUNCHES['regular']['dirs']]
        [audit_bunch(bunch_dir) for bunch_dir in BUNCHES['audit']['dirs']]
    # else:
        # TODO one run regarding the bunch_type

    # Write to disk: Copy the selected files to the target directories
    [shutil.copy2(src, dst) for (src, dst) in assignments]

    # -------------------------------------------------------------------------

    # Testing - Comment or uncomment the lines to output some stats.

    [print(root, len(files)) for root, dirs, files in os.walk(ANNOTATORS['root_dir'])]
    print('Unused documents:', len(spool))
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
