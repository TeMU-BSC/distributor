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

TODO This script has two modes: (i) Individual mode (default) distributes the
    documents ONLY for a concrete run, specificating the type of run:
    `training`, `regular` or `audit`; (ii) Complete mode (`--complete-run`
    option flag) distributes massively all the documents in the given
    corpus_dir to some given annotators.

'''

import collections
from itertools import combinations, cycle, islice
import os
import re
import random
import shutil
from typing import List, Dict, Tuple

import click

import utils

# Here below there are some PyLint disablings (by symbolic message).
# pylint: disable=expression-not-assigned
# pylint: disable=no-value-for-parameter

# CONSTANTS (modify them if needed to adjust this script)
# =======================================================

ANNOTATORS = {
    'root_dir': 'annotators',
    'total': 4,
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

# TOTAL_PICKINGS = 1225  # If bunch 01 is included in BUNCHES['training']['dirs']
TOTAL_PICKINGS = 1177  # If bunch 01 is not included in BUNCHES['training']['dirs']

# Documents overlapping map. This is a list of lists, which each sublist is
# made of tuples (annotator_to_copy_from, annotator_to_paste_to).
OVERLAPPINGS = 8
annotators_list = list(range(ANNOTATORS['total']))
comb_list = list(combinations(annotators_list, 2))
intertagger_seq = [list(islice(cycle(comb_list), i, i + OVERLAPPINGS)) for i in range(0, 5, 2)]

# AUDIT_OVERLAPPINGS_OLD = [
#     [(0, 1), (1, 1), (2, 3)],
#     [(0, 2), (1, 2)],
#     [(0, 3), (1, 3)],
#     [(0, 0)]
# ]

# Delimiter character of the clusters_file
DELIMITER = '\t'

# Seed for random reproducibility purposes (the value can be whatever integer)
SEED = 777

# Directory to put some empty files for testing
TEST_DIR = 'empty_corpus'

# Regional populations (in millions of people)
# ============================================

CATALONIA_POPULATION = 7.6  # in 2018
BALEARIC_ISLANDS_POPULATION = 1.150  # in 2017

# SonEspases is the only balearic representative in the documents spool
# SONESPASES_REPRESENTATIVENESS = BALEARIC_ISLANDS_POPULATION / CATALONIA_POPULATION
SONESPASES_REPRESENTATIVENESS = 0.13  # TODO ask Aitor again the source of populations

# -----------------------------------------------------------------------------


@click.command()
@click.option('--clusters-file',
              help='CSV file with `file,cluster` format rows; it can have any delimiter (tabs for TSV or spaces for TXT).')
@click.option('--corpus-dir', default=TEST_DIR,
              help='Directory that contains EXCLUSIVELY the plain text documents to annotate.')
@click.option('--annotators', nargs=4, type=click.Tuple([str, str, str, str]),
              default=ANNOTATORS['dummy_names'],
              help='Names of the 4 annotators separated by whitespace.')
# @click.option('--annotators', '-a', multiple=True, help='Name of an annotator.')
@click.option('--backup', is_flag=True,
              help='Create a backup of the `--corpus-dir`.')
@click.option('--test-mode', is_flag=True,
              help='Create dummy empty files reading the CSV content to test this script without writing to disk.')
# @click.option('--complete-distribution', is_flag=True,
#               help="Distribute the documents massively for all bunches in one single execution.")
# @click.option('--bunch-type', prompt=True,
#               type=click.Choice(['training', 'regular', 'audit'], case_sensitive=False))
# @click.option('--bunch-dir', prompt='New directory name for the run (e.g. `01`)',
#               help='Name for the new directory where the documents are going to be copied.')
def distribute_documents(clusters_file: str, corpus_dir: str,
                         annotators: tuple, backup: bool, test_mode: bool):
                         # complete_distribution: bool, bunch_type: str, bunch_dir: str
    '''
    Distribute plain text documents into different directories regarding the following criteria.

    The distribution of the documents depends on the run types defined for the
    project: (i) Training type assigns the exactly same amount of documents to
    each annotator; (ii) Regular run assigns a certain bunch of documents for
    each annotator, being all the documents different among the annotators.
    (iii) Audit run assigns a certain bunch of documents for each annotator,
    overlapping some of them, so some documents will be annotated more than
    once.

    Moreover, the pickings of the documents depend on the defined percentages
    regarding the source (SonEspases and AQuAS, which has subclusters).
    '''

    # Variables initialization
    # ========================

    # Load all documents to handle in a {cluster: docs} dictionary
    delimiter = utils.get_delimiter(clusters_file)
    spool = utils.get_clustered_dict(clusters_file, delimiter)

    # Calculate document amounts
    sizes = {cluster: len(docs) for cluster, docs in spool.items()}
    total = sum(sizes.values())
    sonespases_cluster_id = utils.get_key_by_substr_in_values_lists(
        spool, 'sonespases')
    sonespases = sizes.get(sonespases_cluster_id)
    aquas = total - sonespases

    # # Order sizes dict by its values
    # sorted_sizes = sorted(sizes.items(), key=lambda kv: kv[1])
    # sorted_dict = collections.OrderedDict(sorted_sizes)

    # Calculate picking percentages per cluster
    sonespases_global_percentage = SONESPASES_REPRESENTATIVENESS
    aquas_global_percentage = 1 - sonespases_global_percentage
    percentages = dict()
    for cluster, size in sizes.items():
        if cluster == sonespases_cluster_id:
            percentage = sonespases_global_percentage
        else:
            percentage = (size / aquas) * aquas_global_percentage
        percentages.update({cluster: percentage})

    # The tracking object is a list of tuples (file_to_copy, destination_dir)
    distributions = list()

    # Auxiliary funcions
    # ==================

    def pick_all_documents() -> List[str]:
        '''Pick all the needed documents for the experiment regarding the
        amount of them for each cluster.'''
        picked_docs = list()
        for cluster, docs in spool.items():
            random.seed(SEED)
            units = round(TOTAL_PICKINGS * percentages[cluster])
            sample = random.sample(docs, k=units)
            picked_docs.extend(sample)
            [docs.remove(doc) for docs in spool.values()
                for doc in docs if doc in picked_docs]
        return picked_docs

    def pick_bunch(bunch_type: str, number_of_discards=0) -> List[str]:
        '''Pick a bunch of documents regarding the percentage for each
        different cluster and remove them from the global picked spool.'''
        bunch_amount = BUNCHES[bunch_type]['docs'] - number_of_discards
        print('current bunch:', bunch_amount)
        bunch = list()
        for cluster, percentage in percentages.items():
            random.seed(SEED)
            units = round(bunch_amount * percentage)
            bunch.extend(random.sample(picked_spool, units))
            [picked_spool.remove(docs) for docs in picked_spool if docs in bunch]

        # Check the difference, because in training bunch only 24 (out of 25) are selected
        difference = len(bunch) - bunch_amount
        if difference == -1:
            random.seed(SEED)
            units = 1
            bunch.extend(random.sample(picked_spool, units))
            [picked_spool.remove(docs) for docs in picked_spool if docs in bunch]

        return bunch

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
        print('Sum of percentages:', sum([p for p in percentages.values()]))
        print('Total documents:', total)
        unused = sum([len(docs) for cluster, docs in spool.items()])
        print('Unused documents:', unused)
        destinations = [dst for doc, dst in distributions]
        print('Total ann subdirs:', len(set(destinations)))
        print('Total distributed:', len(distributions))

        # Distinct documents to annotate
        regex = r'(sonespases_)?(\d+)(\.utf8)?\.txt'
        pattern = re.compile(regex)
        filenames = re.findall(pattern, str(distributions))
        distinct_annotations = len(set(filenames))
        print('Number of distinct annotations:', distinct_annotations)
        print('Remaining docs in picked spool:', picked_spool)
        

    # Functions for each type of bunch
    # ================================

    def training_bunch(dirname: str):
        '''Assign exactly the same documents to each annotator training directory.'''
        # Pick the documents
        training_docs = pick_bunch('training')

        # Add the picked docs to the distributions object
        for doc in training_docs:
            src = os.path.join(corpus_dir, doc)
            for annotator in annotators:
                dst = os.path.join(ANNOTATORS["root_dir"], annotator, dirname)
                distributions.append((src, dst))

    def regular_bunch(regular_dir: str):
        '''Assign a different bunch of documents to each annotator regular directory.'''
        for annotator in annotators:
            # Pick the documents
            regular_docs = pick_bunch('regular')

            # Add the picked docs to the distributions object
            dst = os.path.join(ANNOTATORS["root_dir"], annotator, regular_dir)
            for doc in regular_docs:
                src = os.path.join(corpus_dir, doc)
                distributions.append((src, dst))

    def audit_bunch(audit_dir: str, overlappings_list: List[List[Tuple[int, int]]]):
        '''Assign a bunch of documents to each annotator, but some of the
        documents are repeated (overlapped).'''
        for (ann_index, annotator) in enumerate(annotators):

            # Step 1: Remove as many documents as ann_index appear in the
            # AUDIT_OVERLAPPINGS, in order to make space for the further
            # overlappings, maintaining constant the bunch of docs per
            # directory.
            number_of_discards = utils.count_element_in_list_of_tuples(
                overlappings_list, ann_index)

            # Step 2: Pick the audit docs
            audit_docs = pick_bunch('audit', number_of_discards)

            # Step 3: Add the bunch of docs to this annotator
            dst = os.path.join(ANNOTATORS["root_dir"], annotator, audit_dir)
            for doc in audit_docs:
                src = os.path.join(corpus_dir, doc)
                distributions.append((src, dst))

            # Step 4: Copy the next doc from src_ann to dst_ann
            for map_index, (src_ann, dst_ann) in enumerate(overlappings_list):
                if src_ann == ann_index:
                    src_doc = os.path.join(ANNOTATORS["root_dir"], annotator, audit_dir, audit_docs[map_index])
                    dst_ann = os.path.join(ANNOTATORS["root_dir"], annotators[dst_ann], audit_dir)
                    distributions.append((src_doc, dst_ann))

    # -------------------------------------------------------------------------

    picked_spool = pick_all_documents()

    # Execution of the bunches (using list comprehensions)
    # ====================================================

    # Training
    [training_bunch(bunch_dir) for bunch_dir in BUNCHES['training']['dirs']]
    
    # Regular
    [regular_bunch(bunch_dir) for bunch_dir in BUNCHES['regular']['dirs']]
    
    # Audit. First, get each overlappings list (copy certain doc from one annotator to another)
    for index, bunch_dir in enumerate(BUNCHES['audit']['dirs']):
        for overlappings_list in islice(cycle(intertagger_seq), index, index+1):
            audit_bunch(bunch_dir, overlappings_list)


    # Execution ONLY of an specific type of bunch
    # =============================================

    # if bunch_type == 'training':
    #     training_bunch(bunch_dir)
    # elif bunch_type == 'regular':
    #     regular_bunch(bunch_dir)
    # elif bunch_type == 'audit':
    #     audit_bunch(bunch_dir)

    # Flags handling before writing to disk
    # =====================================

    if test_mode:
        utils.create_empty_files_from_csv_se(TEST_DIR, clusters_file, delimiter)

    if backup:
        backup_dir = f'{corpus_dir}_backup'
        utils.create_docs_backup_se(corpus_dir, backup_dir)
    
    write_to_disk_function()

    testing_printings()

    # -------------------------------------------------------------------------


if __name__ == '__main__':
    distribute_documents()
annotators