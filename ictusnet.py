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

TODO
    Two modes: (i) Individual mode (default) distributes the
    documents ONLY for a concrete run, specificating the type of run:
    `training`, `regular` or `audit`; (ii) Complete mode distributes massively
    all the documents in the given corpus_dir to some given annotators.

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

# CONSTANTS (modify them to adjust this script)
# =============================================

ANNOTATORS = {
    'root_dir': 'annotators',
    'default': ('A', 'B', 'C', 'D'),
}

BUNCHES = {
    'training': {
        'dirs': ['08'],
        'amount': 25
    },
    'regular': {
        'dirs': [],
        'amount': 50
    },
    'audit': {
        'dirs': ['02', '03', '04', '05', '06', '07'],
        'amount': 50
    }
}

# If bunch 01 is included in BUNCHES['training']['dirs']
# TOTAL_PICKINGS = 1225

# If bunch 01 is not included in BUNCHES['training']['dirs']
TOTAL_PICKINGS = 1300  # len(BUNCHES['training']['dirs']) * len(ANNOTATORS['default']) * BUNCHES['training']['amount']) + 
                       # len(BUNCHES['audit']['dirs']) * len(ANNOTATORS['default']) * BUNCHES['audit']['amount'])

# Number of documents per audit bunch that are annotated by more than one annotator
OVERLAPPINGS = 8

# Seed for random reproducibility purposes (the value can be whatever integer)
SEED = 777

# Directory to put some empty files for testing
TEST_DIR = 'empty_corpus'

# SonEspases is the only balearic representative in the documents spool
# CATALONIA_POPULATION = 7.6  # millions of people in 2018
# BALEARIC_ISLANDS_POPULATION = 1.150  # millions of people in 2017
# SONESPASES_REPRESENTATIVENESS = BALEARIC_ISLANDS_POPULATION / CATALONIA_POPULATION
SONESPASES_REPRESENTATIVENESS = 0.13

# -----------------------------------------------------------------------------


@click.command()
@click.option('--clusters-file',
              help='CSV file with `file,cluster` format rows; it can have any delimiter (tabs for TSV or spaces for TXT).')
@click.option('--corpus-dir', default=TEST_DIR,
              help='Directory that contains EXCLUSIVELY the plain text documents to annotate.')
@click.option('--annotators', nargs=4, type=click.Tuple([str, str, str, str]),
              default=ANNOTATORS['default'],
              help='Names of the 4 annotators separated by whitespace.')
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

    # Result accumulative list of (src_file, dst_dir) that will be written to disk
    distributions = list()

    # Load all documents in a {cluster: docs} dictionary
    delimiter = utils.get_delimiter(clusters_file)
    all_clustered_docs = utils.get_clustered_dict(clusters_file, delimiter)

    # Calculate document amounts
    sizes = {cluster: len(docs)
             for cluster, docs in all_clustered_docs.items()}
    total = sum(sizes.values())
    sonespases_cluster_id = utils.get_key_by_substr_in_values_lists(
        all_clustered_docs, 'sonespases')
    sonespases = sizes.get(sonespases_cluster_id)
    aquas = total - sonespases

    # Order dict by its values, return a list of tuples
    sizes = sorted(sizes.items(), key=lambda kv: kv[1])
    # sorted_dict = collections.OrderedDict(sorted_sizes)

    # Calculate picking percentages per clusterANNOTATORS['default']
    aquas_global_percentage = 1 - SONESPASES_REPRESENTATIVENESS
    percentages = dict()
    for cluster, size in sizes:
        if cluster == sonespases_cluster_id:
            percentage = SONESPASES_REPRESENTATIVENESS
        else:
            percentage = (size / aquas) * aquas_global_percentage
        percentages.update({cluster: percentage})

    # Documents overlapping map. This is a list of lists, which each sublist is
    # made of tuples (annotator_to_copy_from, annotator_to_paste_to).
    comb_list = list(combinations(ANNOTATORS['default'], 2))
    intertagging_seq = [list(islice(cycle(comb_list), i, i + OVERLAPPINGS))
                        for i in range(0, 5, 2)]

    # Pick all documents ensuring the percentages
    spool = list()
    for cluster, docs in all_clustered_docs.items():
        random.seed(SEED)
        units = round(TOTAL_PICKINGS * percentages[cluster])
        sample = random.sample(docs, k=units)
        spool.extend(sample)
        [docs.remove(picked_doc) for picked_doc in sample]
    diff = TOTAL_PICKINGS - len(spool)
    less_representative_cluster_id = sizes[0][0]
    less_representative_cluster_docs = all_clustered_docs[less_representative_cluster_id]
    random.seed(SEED)
    extra_docs = random.sample(less_representative_cluster_docs, diff)
    spool.extend(extra_docs)

    def pick_random_bunch_se(amount: int) -> List[str]:
        '''Pick a bunch of random documents from the spool.'''
        random.seed(SEED)
        bunch = random.sample(spool, amount)
        [spool.remove(doc) for doc in bunch]
        # # Check the difference, because in training bunch only 24 (out of 25) are selected
        # difference = len(bunch) - bunch_amount
        # if difference == -1:
        #     random.seed(SEED)
        #     units = 1
        #     bunch.extend(random.sample(spool, units))
        #     [spool.remove(docs)
        #      for docs in spool if docs in bunch]
        return bunch

    # Functions for each type of bunch
    # ================================

    def training_bunch(bunch_dir: str) -> List[Tuple[str, str]]:
        '''Assign exactly the same documents to each annotatorclusters_file, for training
        purposes.'''
        amount = BUNCHES['training']['amount']
        picked_docs = pick_random_bunch_se(amount)
        for doc in picked_docs:
            src = os.path.join(corpus_dir, doc)
            # Repeat the same destination for every annotator
            for annotator in annotators:
                dst = os.path.join(
                    ANNOTATORS["root_dir"], annotator, bunch_dir)
                distributions.append((src, dst))

    def regular_bunch(bunch_dir: str) -> List[Tuple[str, str]]:
        '''Assign different pickings with the same amount of documents to each
        annotator, for regular annotation purposes. '''
        for annotator in annotators:
            picked_docs = pick_random_bunch_se(BUNCHES['regular']['amount'])
            dst = os.path.join(ANNOTATORS["root_dir"], annotator, bunch_dir)
            # Assign different pickings with the same amount of docs to each annotator
            for doc in picked_docs:
                src = os.path.join(corpus_dir, doc)
                distributions.append((src, dst))

    def audit_bunch(bunch_dir: str, overlappings_list: List[List[Tuple[str, str]]]):
        '''Assign a bunch of documents to each annotator, but some of the
        documents are repeated (overlapped).'''
        for annotator in annotators:

            # Step 1: Remove as many documents as ann_index appear in the
            # AUDIT_OVERLAPPINGS, in order to make space for the further
            # overlappings, maintaining constant the bunch of docs per
            # directory.
            number_of_discards = utils.count_element_in_list_of_tuples(
                overlappings_list, annotator)

            # Step 2: Pick the audit docs and add the bunch of docs to this annotator
            amount = BUNCHES['audit']['amount'] - number_of_discards
            picked_docs = pick_random_bunch_se(amount)
            srcs = [os.path.join(corpus_dir, doc) for doc in picked_docs]
            dst = os.path.join(ANNOTATORS["root_dir"], annotator, bunch_dir)
            [distributions.append((src, dst)) for src in srcs]

            # Step 3: Duplicate some docs
            for index, (src, dst) in enumerate(overlappings_list):
                if annotator == src:
                    doc_to_copy = os.path.join(corpus_dir, picked_docs[index])
                    destination = os.path.join(ANNOTATORS["root_dir"], dst, bunch_dir)
                    distributions.append((doc_to_copy, destination))

    # -------------------------------------------------------------------------

    # Execution of the training and regular bunches (using list comprehensions)
    [training_bunch(training_dir)
     for training_dir in BUNCHES['training']['dirs']]
    [regular_bunch(regular_dir) for regular_dir in BUNCHES['regular']['dirs']]

    # Before audit bunches pickings, get each overlappings list (copy certain doc from one annotator to another)
    for index, audit_dir in enumerate(BUNCHES['audit']['dirs']):
        for overlappings_list in islice(cycle(intertagging_seq), index, index+1):
            audit_bunch(audit_dir, overlappings_list)

    # Flags checking before writing to disk
    if test_mode:
        utils.create_empty_files_from_csv_se(
           TEST_DIR, clusters_file, delimiter)
    if backup:
        backup_dir = f'{corpus_dir}_backup'
        utils.create_docs_backup_se(corpus_dir, backup_dir)

    def write_to_disk():
        '''Copy files from source path to destinations, creating the needed
        directory tree.'''
        for (src, dst) in distributions:
            if not os.path.exists(dst):
                os.makedirs(dst)
            shutil.copy2(src, dst)
    write_to_disk()

    def testing_printings():
        '''Testing - Comment or uncomment the lines to output some stats.'''
        # print(distributions)
        [print(root, len(files))
            for root, dirs, files in os.walk(ANNOTATORS['root_dir'])]
        print('Sum of percentages:', sum([p for p in percentages.values()]))
        print('Number of annotations:', len(distributions))

        # Distinct documents to annotate
        regex = r'(sonespases_)?(\d+)(\.utf8)?\.txt'
        pattern = re.compile(regex)
        filenames = re.findall(pattern, str(distributions))
        print('Number of distinct annotations:', len(set(filenames)))
    testing_printings()

    # -------------------------------------------------------------------------


if __name__ == '__main__':
    distribute_documents()
