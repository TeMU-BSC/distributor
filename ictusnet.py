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

from collections import Counter
from itertools import combinations, cycle, islice
import os
import re
import random
import shutil
from typing import List, Tuple

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

BUNCHES = [
    {
        'type': 'training',
        'amount': 25,
        'dirs': ['08']
    },
    {
        'type': 'regular',
        'amount': 50,
        'dirs': []
    },
    {
        'type': 'audit',
        'amount': 50,
        'dirs': ['02', '03', '04', '05', '06', '07']
    }
]

# Number of documents per audit bunch that are annotated by more than one annotator
OVERLAPPINGS_PER_AUDIT = 8

# Seed for random reproducibility purposes (the value can be whatever integer)
SEED = 777

# Directory to put some empty files for testing
TEST_DIR = 'empty_corpus'

# Because SonEspases Hospital is the only balearic representative in the documents spool,
# we considered calculating a fixed percentage for those documents, based on regional
# populations (Wikipedia, on 21th Oct 2019).
CATALONIA_POPULATION = 7543825
BALEARIC_POPULATION = 1150839
TOTAL_POPULTAION = CATALONIA_POPULATION + BALEARIC_POPULATION
SONESPASES_PERCENTAGE = round(BALEARIC_POPULATION / TOTAL_POPULTAION, 2)  # 0.13

# -----------------------------------------------------------------------------


@click.command()
@click.option('--clusters-file',
              help='''TSV file with `file\tcluster` header. It can have any
                   delimiter (commas for CSV or spaces for TXT).''')
@click.option('--corpus-dir', default=TEST_DIR,
              help='Directory that contains EXCLUSIVELY the plain text documents to annotate.')
@click.option('--annotators', nargs=4, type=click.Tuple([str, str, str, str]),
              default=ANNOTATORS['default'],
              help='Names of the 4 annotators separated by whitespace.')
@click.option('--backup', is_flag=True,
              help='Create a backup of the `--corpus-dir`.')
@click.option('--create-empty-corpus', is_flag=True,
              help='Create empty files reading the CSV content to test this script.')
# @click.option('--complete-distribution', is_flag=True,
#               help="Distribute the documents massively for all bunches in one single execution.")
# @click.option('--bunch-type', prompt=True,
#               type=click.Choice(['training', 'regular', 'audit'], case_sensitive=False))
# @click.option('--bunch-dir', prompt='New directory name for the run (e.g. `01`)',
#               help='Name for the new directory where the documents are going to be copied.')
def distribute_documents(clusters_file: str, corpus_dir: str,
                         annotators: tuple, backup: bool, create_empty_corpus: bool):
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

    def pick_random_bunch_se(amount: int) -> List[str]:
        '''Pick a bunch of random documents from the spool.'''
        random.seed(SEED)
        bunch = random.sample(spool, amount)
        for doc in bunch:
            spool.remove(doc)
        return bunch

    def training_bunch(bunch_dir: str) -> List[Tuple[str, str]]:
        '''Assign exactly the same documents to each annotator.'''
        for bunch in BUNCHES:
            if bunch['type'] == 'training':
                amount = bunch['amount']
        picked_docs = pick_random_bunch_se(amount)
        for doc in picked_docs:
            src = os.path.join(corpus_dir, doc)
            # Repeat the same destination for every annotator
            for annotator in annotators:
                dst = os.path.join(
                    ANNOTATORS["root_dir"], annotator, bunch_dir)
                distributions.append((src, dst))

    def regular_bunch(bunch_dir: str) -> List[Tuple[str, str]]:
        '''Assign the same amount of documents to each annotator being all
        documents different from one annotator to other.'''
        for bunch in BUNCHES:
            if bunch['type'] == 'regular':
                amount = bunch['amount']
        for annotator in annotators:
            picked_docs = pick_random_bunch_se(amount)
            dst = os.path.join(ANNOTATORS["root_dir"], annotator, bunch_dir)
            # Assign different pickings with the same amount of docs to each annotator
            for doc in picked_docs:
                src = os.path.join(corpus_dir, doc)
                distributions.append((src, dst))

    def audit_bunch(bunch_dir: str, overlappings_list: List[List[Tuple[str, str]]]):
        '''Assign a bunch of documents to each annotator, but some of the
        documents are repeated (overlapped).'''
        for annotator in annotators:

            # Step 1: Discard as many documents as this annotator appears in
            # the given overlappings list, in order to make space for the further
            # overlappings, maintaining constant the bunch of docs per
            # directory.
            target_annotators = [tgt for (src, tgt) in overlappings_list]
            discards = Counter(target_annotators)[annotator]

            # Step 2: Pick the audit docs and add the bunch of docs to this annotator
            for bunch in BUNCHES:
                if bunch['type'] == 'audit':
                    amount = bunch['amount'] - discards
            picked_docs = pick_random_bunch_se(amount)
            srcs = [os.path.join(corpus_dir, doc) for doc in picked_docs]
            dst = os.path.join(ANNOTATORS["root_dir"], annotator, bunch_dir)
            for src in srcs:
                distributions.append((src, dst))

            # Step 3: Duplicate some docs
            for index, (src, dst) in enumerate(overlappings_list):
                if annotator == src:
                    doc_to_copy = os.path.join(corpus_dir, picked_docs[index])
                    destination = os.path.join(
                        ANNOTATORS["root_dir"], dst, bunch_dir)
                    distributions.append((doc_to_copy, destination))

    def write_to_disk():
        '''Copy files from source path to destinations, creating the needed
        directory tree.'''
        for (src, dst) in distributions:
            if not os.path.exists(dst):
                os.makedirs(dst)
            shutil.copy2(src, dst)

    def stdout_printings():
        '''Testing - Comment or uncomment the lines to output some stats.'''
        [print(root, len(files))
         for root, dirs, files in os.walk(ANNOTATORS['root_dir'])]
        print('Initial pickings:', total_pickings)
        print('Documents written to disk:', len(distributions))

        # Distinct documents to annotate
        regex = r'(sonespases_)?(\d+)(\.utf8)?\.txt'
        pattern = re.compile(regex)
        filenames = re.findall(pattern, str(distributions))
        print('Distinct annotations:', len(set(filenames)))
        print('Remaining spool:', len(spool))

    # Accumulative distributions list of tuples (src_file, dst_dir), to later write to disk
    distributions = list()

    # Load all documents from clustering TSV file in a dictionary {cluster: docs}
    delimiter = utils.get_delimiter(clusters_file)
    all_clustered_docs = utils.get_clustered_dict(clusters_file, delimiter)

    # Calculate document amounts
    sizes = {cluster: len(docs)
             for cluster, docs in all_clustered_docs.items()}
    total_amount = sum(sizes.values())
    sonespases_cluster_id = utils.get_key_by_substr_in_values(
        all_clustered_docs, 'sonespases')
    sonespases_amount = sizes.get(sonespases_cluster_id)
    aquas_amount = total_amount - sonespases_amount

    # Order dict by its values, return a list of tuples
    sizes = sorted(sizes.items(), key=lambda kv: kv[1])

    # Calculate picking percentages per cluster
    aquas_global_percentage = 1 - SONESPASES_PERCENTAGE
    percentages = dict()
    for cluster, size in sizes:
        if cluster == sonespases_cluster_id:
            percentage = SONESPASES_PERCENTAGE
        else:
            percentage = (size / aquas_amount) * aquas_global_percentage
        percentages.update({cluster: percentage})

    # Documents overlapping map. This is a list of lists, which each sublist is
    # made of tuples (annotator_to_copy_from, annotator_to_paste_to).
    comb_list = list(combinations(annotators, 2))
    intertagging_seq = [list(islice(cycle(comb_list), i, i + OVERLAPPINGS_PER_AUDIT))
                        for i in range(0, 5, 2)]

    # Calculate the total amount of pickings
    pickings = list()
    for bunch in BUNCHES:
        if bunch['type'] == 'training':
            pick = bunch['amount']
        if bunch['type'] == 'regular':
            pick = bunch['amount'] * len(annotators) * len(bunch['dirs'])
        if bunch['type'] == 'audit':
            pick = (bunch['amount'] * len(annotators) - OVERLAPPINGS_PER_AUDIT) * len(bunch['dirs'])
        pickings.append(pick)
    total_pickings = sum(pickings)

    # Pick all documents ensuring the percentages
    spool = list()
    for cluster, docs in all_clustered_docs.items():
        random.seed(SEED)
        units = round(total_pickings * percentages[cluster])
        sample = random.sample(docs, k=units)
        spool.extend(sample)
        for picked_doc in sample:
            docs.remove(picked_doc)

    # # Make sure that the previous rounding effect doesn't affect the final length of spool
    # diff = total_pickings - len(spool)
    # less_representative_cluster_id = sizes[0][0]
    # less_representative_cluster_docs = all_clustered_docs[less_representative_cluster_id]
    # random.seed(SEED)
    # extra_docs = random.sample(less_representative_cluster_docs, diff)
    # spool.extend(extra_docs)

    # Execution of all the bunches pickings
    # (using list comprehensions as shortcuts, not returning any value from them)
    for bunch in BUNCHES:
        [training_bunch(dirname) for dirname in bunch['dirs']
         if bunch['type'] == 'training']
        [regular_bunch(dirname) for dirname in bunch['dirs']
         if bunch['type'] == 'regular']
        # The audit bunch function needs the overlapping list to duplicate documents accordingly
        [audit_bunch(dirname, overlappings_list) for i, dirname in enumerate(bunch['dirs'])
         if bunch['type'] == 'audit'
         for overlappings_list in islice(cycle(intertagging_seq), i, i+1)]

    # Flags checking before writing to disk
    if create_empty_corpus:
        utils.create_empty_files_from_csv_se(
            TEST_DIR, clusters_file, delimiter)
    if backup:
        backup_dir = f'{corpus_dir}_backup'
        utils.create_docs_backup_se(corpus_dir, backup_dir)
    write_to_disk()

    # Printings to give feedback to the user of the script
    stdout_printings()


# -----------------------------------------------------------------------------

if __name__ == '__main__':
    distribute_documents()
