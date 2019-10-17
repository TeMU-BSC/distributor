'''
Description: Script that distributes automatically the documents to some
annotators.
Project: IctusNET
Author of this script:
    - Alejandro Asensio <alejandro.asensio@bsc.es>
Credits to:
    - Ankush Rana <ankush.rana@bsc.es> for the initial 10-overlappings
      algorithm, and
    - Aitor Gonzalez <aitor.gonzalez@bsc.es> for the follow-up of
      the entire IctusNET project.
'''

import os
import re
import random
import shutil
from typing import List, Dict

import click

import utils

# Here below there are some PyLint disablings (by symbolic message).
# pylint: disable=expression-not-assigned
# pylint: disable=no-value-for-parameter

# CONSTANTS (modify them if needed to adjust this script)
# =======================================================

ANNOTATORS = {
    'root_dir': 'annotators',
    'dummy_names': ('A', 'B', 'C', 'D'),
}
BUNCHES = {
    'training': {
        'dirs': ['08'],
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

# Documents overlapping map. This is a list of lists, which each list is made
# of tuples with the structure: (document_index, destination_annotator_index).
# Note that with 8 overlappings, each annotator has 4 documents that are
# equally compared with other annotators.
AUDIT_OVERLAPPINGS = [
    [(0, 1), (1, 1), (2, 3)],
    [(0, 2), (1, 2)],
    [(0, 3), (1, 3)],
    [(0, 0)]
]

# Delimiter character of the clusters_file
DELIMITER = '\t'

# Seed for random reproducibility purposes (the value can be whatever integer)
SEED = 777

# Constants for dummy data
# ========================

# The minimum amount of dummy docs should be:
# (trainings * TRAINING_BUNCH) + (regulars * REGULAR_BUNCH) + (audits * AUDIT_BUNCH)
TOTAL_DUMMY_DOCS = 1400
DUMMY_EXTENSION = '.txt'
DUMMY_DIR = 'dummy_docs'

# Regional populations (in millions of people)
# ============================================

CATALONIA_POPULATION = 7.6  # in 2018
BALEARIC_ISLANDS_POPULATION = 1.150  # in 2017

# SonEspases is the only balearic representative in the documents spool
SONESPASES_REPRESENTATIVENESS = BALEARIC_ISLANDS_POPULATION / CATALONIA_POPULATION

# TODO ask Aitor again the source of populations
SONESPASES_PERCENTAGE = 0.13

# -----------------------------------------------------------------------------


@click.command()
@click.option('--clusters-file',  # type=click.File('r'),
              help='CSV file with `file cluster` format data.')
@click.option('--delimiter', default=DELIMITER,
              help='Delimiter for the CSV `--source-file`.')
@click.option('--source-dir', default=DUMMY_DIR,
              help='Directory that contains EXCLUSIVELY the plain text documents to annotate.')
@click.option('--annotators', nargs=4, type=click.Tuple([str, str, str, str]),
              default=ANNOTATORS['dummy_names'],
              help='Names of the 4 annotators separated by whitespace.')
@click.option('--write-to-disk', is_flag=True,
              help='Copy files to the target annotators directories.')
# @click.option('--annotators', '-a', multiple=True, help='Name of an annotator.')
@click.option('--backup', is_flag=True,
              help='Create a backup of the `--source-dir`.')
@click.option('--dummy', is_flag=True,
              help='Create dummy empty files to quickly test this script.')
# @click.option('--complete-distribution', is_flag=True,
#               help="Distribute the documents massively for all bunches in one single execution.")
# @click.option('--bunch-type', prompt=True,
#               type=click.Choice(['training', 'regular', 'audit'], case_sensitive=False))
# @click.option('--bunch-dir', prompt='New directory name for the run (e.g. `01`)',
# help='Name for the new directory where the documents are going to be
# copied.')
def distribute_documents(clusters_file: str, delimiter: str, source_dir: str,
                         annotators: tuple, write_to_disk: bool, backup: bool,
                         dummy: bool):  # complete_distribution: bool, bunch_type: str, bunch_dir: str
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

    Moreover, the pickings fo the documents depends on the defined percentages
    regarding the source (SonEspases and AQuAS, which has subclusters).
    '''

    # Flags handling
    # ==============

    if dummy:
        utils.create_empty_files_se(
            DUMMY_DIR, TOTAL_DUMMY_DOCS, DUMMY_EXTENSION)
        source_dir = DUMMY_DIR

    if backup:
        backup_dir = f'{source_dir}_backup'
        utils.create_docs_backup_se(source_dir, backup_dir)

    # PRE_PRODUCTION TESTING
    utils.create_empty_files_from_tsv_se(DUMMY_DIR, clusters_file, delimiter)

    # Variables initialization
    # ========================

    # Load all documents to handle in a {cluster: docs} dictionary
    spool = utils.get_clustered_files_spool_from_csv(
        clusters_file, delimiter)

    # Calculate document amounts
    sizes = {cluster: len(docs) for cluster, docs in spool.items()}
    total = sum(sizes.values())
    sonespases_cluster_id = utils.get_key_by_substr_in_values_lists(
        spool, 'sonespases')
    sonespases = sizes.get(sonespases_cluster_id)
    aquas = total - sonespases

    # Calculate picking percentages per cluster
    # sonespases_global_percentage = SONESPASES_REPRESENTATIVENESS
    sonespases_global_percentage = SONESPASES_PERCENTAGE
    aquas_global_percentage = 1 - sonespases_global_percentage
    percentages = dict()
    for cluster, size in sizes.items():
        if cluster == sonespases_cluster_id:
            percentage = sonespases_global_percentage
        else:
            percentage = size / aquas * aquas_global_percentage
        percentages.update({cluster: percentage})

    # The tracking object is a list of tuples (file_to_copy, destination_dir)
    distributions = list()

    # Auxiliary funcions
    # ==================

    def pick_documents(bunch_type: str) -> List[str]:
        '''Pick a bunch of documents regarding the percentage for each
        different cluster.'''
        picked_docs = list()
        for cluster, docs in spool.items():
            percentage = percentages[cluster]

            # Pick documents and remove them from the spool
            random.seed(SEED)
            picked_docs.extend(random.sample(docs, round(
                BUNCHES[bunch_type]['docs']*percentage)))
            [docs.remove(doc) for docs in spool.values()
                for doc in docs if doc in picked_docs]

        # Check the difference (because in training bunch only 24 out of 25 are selected)
        difference = len(picked_docs) - BUNCHES[bunch_type]['docs']
        if difference == -1:
            random.seed(SEED)
            picked_docs.extend(random.sample(docs, 1))
            [docs.remove(doc) for docs in spool.values()
                for doc in docs if doc in picked_docs]
        elif difference == 1:
            picked_docs.pop()

        return picked_docs

    def write_to_disk_function():
        '''Create the needed directory tree and copy files to destinations.'''
        # 1. Collect the dir names of all annotators
        all_bunch_dirs = [BUNCHES[bunch_type]['dirs']
                          for bunch_type in BUNCHES]

        # 2. Convert a list of lists to a flat list
        all_flat_bunch_dirs = [
            item for sublist in all_bunch_dirs for item in sublist]

        # 3. Create the directory tree (empty tree)
        utils.create_dirs_tree_se(
            ANNOTATORS['root_dir'], annotators, all_flat_bunch_dirs)

        # 4. Copy the selected files to the target directories
        [shutil.copy2(src, dst) for (src, dst) in distributions]

    def testing_printings():
        '''Testing - Comment or uncomment the lines to output some stats.'''
        # print(distributions)

        [print(root, len(files))
            for root, dirs, files in os.walk(ANNOTATORS['root_dir'])]

        print('Unused documents:', sum([len(docs)
                                        for cluster, docs in spool.items()]))

        destinations = [dst for doc, dst in distributions]
        print('Total ann subdirs:', len(set(destinations)))

        print('Total number of annotations:', len(distributions))

        # Distinct documents to annotate
        regex = r'(sonespases_)?(\d+)(\.utf8)?\.txt'
        pattern = re.compile(regex)
        filenames = re.findall(pattern, str(distributions))
        distinct_annotations = len(set(filenames))
        print('Number of distinct annotations:', distinct_annotations)

        print('Sum of percentages:', sum([p for p in percentages.values()]))

    # Functions for each type of bunch
    # ================================

    def training_bunch(dirname: str):
        '''Assign exactly the same documents to each annotator training directory.'''
        # Pick the documents
        training_docs = pick_documents('training')

        # Add the picked docs to the distributions object
        for doc in training_docs:
            src = os.path.join(source_dir, doc)
            for annotator in annotators:
                dst = os.path.join(ANNOTATORS["root_dir"], annotator, dirname)
                distributions.append((src, dst))

    def regular_bunch(regular_dir: str):
        '''Assign a different bunch of documents to each annotator regular directory.'''
        for annotator in annotators:
            # Pick the documents
            regular_docs = pick_documents('regular')

            # Add the picked docs to the distributions object
            dst = os.path.join(ANNOTATORS["root_dir"], annotator, regular_dir)
            for doc in regular_docs:
                src = os.path.join(source_dir, doc)
                distributions.append((src, dst))

    def audit_bunch(audit_dir: str):
        '''Assign a bunch of documents to each annotator, but some of the
        documents are repeated (overlapped).'''
        for (ann_index, annotator) in enumerate(annotators):
            # Pick the documents
            audit_docs = pick_documents('audit')

            # Step 1: Remove as many documents as ann_index appear in the
            # AUDIT_OVERLAPPINGS, in order to make space for the further
            # overlappings, maintaining constant the bunch of docs per
            # directory.
            number_of_docs_to_remove = utils.count_occurrences_in_list_of_list_of_tuples(
                AUDIT_OVERLAPPINGS, ann_index)
            [audit_docs.pop() for i in range(number_of_docs_to_remove)]

            # Step 2: Add the bunch of docs to this annotator
            dst = os.path.join(ANNOTATORS["root_dir"], annotator, audit_dir)
            for doc in audit_docs:
                src = os.path.join(source_dir, doc)
                distributions.append((src, dst))

            # Step 3: Duplicate the documents defined in AUDIT_OVERLAPPINGS
            # for this ann_index annotator (0, 1, 2 or 3)
            for ann_overlapping in AUDIT_OVERLAPPINGS[ann_index]:
                source_doc = os.path.join(
                    ANNOTATORS["root_dir"], annotator, audit_dir, audit_docs[ann_overlapping[0]])
                target_ann = os.path.join(
                    ANNOTATORS["root_dir"], annotators[ann_overlapping[1]], audit_dir)
                distributions.append((source_doc, target_ann))

    # Execution of ALL bunches (using list comprehensions)
    # ====================================================

    [training_bunch(bunch_dir)
        for bunch_dir in BUNCHES['training']['dirs']]
    [regular_bunch(bunch_dir) for bunch_dir in BUNCHES['regular']['dirs']]
    [audit_bunch(bunch_dir) for bunch_dir in BUNCHES['audit']['dirs']]

    # Execution ONLY of an specific type of bunch
    # =============================================

    # if bunch_type == 'training':
    #     training_bunch(bunch_dir)
    # elif bunch_type == 'regular':
    #     regular_bunch(bunch_dir)
    # elif bunch_type == 'audit':
    #     audit_bunch(bunch_dir)

    if write_to_disk:
        write_to_disk_function()

    testing_printings()

    # -------------------------------------------------------------------------


if __name__ == '__main__':
    distribute_documents()
