'''
Script that distributes a corpus of documents among some given annotators.

Author of this script:
    - Alejandro Asensio <alejandro.asensio@bsc.es>

Credits to:
    - Ankush Rana <ankush.rana@bsc.es> for the initial 10-overlappings
      algorithm, and
    - Aitor Gonzalez <aitor.gonzalez@bsc.es> for the follow-up of
      the entire ICTUSnet project.

TODO
    Two modes: (i) Individual mode (default) distributes the
    documents ONLY for a concrete run, specificating the type of run:
    `training`, `regular` or `audit`; (ii) Complete mode distributes massively
    all the documents in the given corpus to some given annotators.

'''

from collections import Counter
from itertools import combinations, cycle, islice
import os
import re
import random
from typing import Generator, List, Tuple

import click

import utils


# === PyLint disablings (by symbolic message) ===
# pylint: disable=no-value-for-parameter
# pylint: disable=invalid-name


# Directory to put created empty files for testing
EMPTY_FILES_DIR = 'empty_files_corpus'

# Directory to put each annotator subdirectory
ANN_DIR = 'annotators'

# CONSTANTS. Modify them to adjust this script to your needs.

# BUNCHES = {
#     'training': {
#         'amount': 25,
#         'dirs': ['08']
#     },
#     'regular': {
#         'amount': 50,
#         'dirs': []
#     },
#     'audit': {
#         'amount': 50,
#         'dirs': ['02', '03', '04', '05', '06', '07']
#     }
# }
BUNCHES = {
    # 'training': {
    #     'amount': 25,
    #     'dirs': []
    # },
    # 'regular': {
    #     'amount': 50,
    #     'dirs': []
    # },
    'audit': {
        'amount': 50,
        'dirs': ['04']
    }
}

# Number of documents per audit bunch that are annotated by more than one
# annotator
# OVERLAPPINGS_PER_AUDIT = 8
# OVERLAPPINGS_PER_AUDIT = 100  # 25 overlappings each annotator (4 annotators)
OVERLAPPINGS_PER_AUDIT = 0

# Seed for random reproducibility purposes (the value can be whatever integer)
SEED = 777

# Because "Hospital Universitari Son Espases" (HUSE) is the only Balearic
# representative in the documents spool, we considered calculating a fixed
# percentage for those documents, based on regional populations (Wikipedia, on
# 21th Oct 2019).
CATALONIA_POPULATION = 7543825  # 7_543_825 underscore separator valid in python3.6+
BALEARIC_POPULATION = 1150839  # 1_150_839 underscore separator valid in python3.6+
TOTAL_POPULTAION = CATALONIA_POPULATION + BALEARIC_POPULATION
SONESPASES_PERCENTAGE = round(
    BALEARIC_POPULATION / TOTAL_POPULTAION, 2)  # 0.13


@click.command()
@click.argument('clusters_file', default=None)
@click.argument('corpus', default=None)
@click.argument('annotators', nargs=4, default=None)
@click.option('-i', '--individual-bunch')
def distribute_documents(clusters_file: str, corpus: str, annotators: Tuple[str, str], individual_bunch: str):
    '''
    Distribute plain text documents into subdirectories the CONSTANTS defined
    at the beggining of this function.

    The pickings of the documents depend on the percentages calculated
    dynamically regarding the representativeness of previously clustered
    SonEspases and AQuAS documents.
    '''

    def random_bunch_se(amount: int) -> Generator[str, None, None]:
        '''Return a generator of document filenames that is a random bunch
        from the global spool variable.'''
        random.seed(SEED)
        bunch = random.sample(spool, amount)
        for doc in bunch:
            yield doc
            spool.remove(doc)

    def training_bunch(dirname: str):
        '''Assign exactly the same documents to each annotator.'''
        amount = BUNCHES['training']['amount']
        for doc in random_bunch_se(amount):
            src = os.path.join(corpus, doc)

            # Repeat the same destination for every annotator
            for annotator in annotators:
                dst = os.path.join(
                    ANN_DIR, annotator, dirname)
                distributions.append((src, dst))

    def regular_bunch(dirname: str):
        '''Assign the same amount of documents to each annotator being all
        documents different from one annotator to other.'''
        amount = BUNCHES['regular']['amount']
        for annotator in annotators:
            dst = os.path.join(ANN_DIR, annotator, dirname)

            # Assign different pickings with the same amount of docs to each
            # annotator
            for doc in random_bunch_se(amount):
                src = os.path.join(corpus, doc)
                distributions.append((src, dst))

    def audit_bunch(
            dirname: str, overlappings_list: List[List[Tuple[str, str]]]):
        '''Assign a bunch of documents to each annotator, but some of the
        documents are repeated (overlapped).'''
        # Extra info for Siamak
        duplicated_docs = list()

        for annotator in annotators:

            # Step 1: Discard as many documents as this annotator appears in
            # the given overlappings list, in order to make space for the further
            # overlappings, maintaining constant the bunch of docs per
            # directory.
            target_annotators = [tgt for (src, tgt) in overlappings_list]
            discards = Counter(target_annotators)[annotator]

            # Step 2: Pick the audit docs and add the bunch of docs to this
            # annotator
            special_amount = BUNCHES['audit']['amount'] - discards
            picked_docs = list(random_bunch_se(special_amount))
            srcs = (os.path.join(corpus, doc) for doc in picked_docs)
            dst = os.path.join(ANN_DIR, annotator, dirname)
            for src in srcs:
                distributions.append((src, dst))

            # Step 3: Duplicate some docs
            for index, (src, dst) in enumerate(overlappings_list):
                if annotator == src:
                    doc_to_copy = os.path.join(corpus, picked_docs[index])

                    # Extra info for Siamak
                    duplicated_docs.append(picked_docs[index])

                    destination = os.path.join(
                        ANN_DIR, dst, dirname)
                    distributions.append((doc_to_copy, destination))
        
        # Extra info for Siamak
        duplicated_docs_dict[dirname] = duplicated_docs

    # Accumulative distributions list of tuples (src_file, dst_dir), to later
    # write to disk
    distributions = []

    # Load all documents from clustering TSV file in a dictionary {cluster:
    # docs}
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
    percentages = {}
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
    pickings = []
    for bunch_type, props in BUNCHES.items():
        if bunch_type == 'training':
            pick = props['amount']
        if bunch_type == 'regular':
            pick = props['amount'] * len(annotators) * len(props['dirs'])
        if bunch_type == 'audit':
            pick = (props['amount'] * len(annotators) -
                    OVERLAPPINGS_PER_AUDIT) * len(props['dirs'])
        pickings.append(pick)
    total_pickings = sum(pickings)

    # Select the documents spool ensuring the percentages
    spool = []
    for cluster, docs in all_clustered_docs.items():
        random.seed(SEED)
        units = round(total_pickings * percentages[cluster])
        sample = random.sample(docs, k=units)
        spool.extend(sample)
        for picked_doc in sample:
            docs.remove(picked_doc)

    # Execution of all the bunches pickings
    # (using list comprehensions as shortcuts, not returning any value from them)
    
    # Info for Siamak
    duplicated_docs_dict = dict()

    for bunch_type, props in BUNCHES.items():
        if bunch_type == 'training':
            for dirname in props['dirs']:
                training_bunch(dirname)
        if bunch_type == 'regular':
            for dirname in props['dirs']:
                regular_bunch(dirname)
        # The audit bunch function needs the overlapping list to duplicate
        # documents accordingly
        if bunch_type == 'audit':
            for i, dirname in enumerate(props['dirs']):
                for overlappings_list in islice(cycle(intertagging_seq), i, i + 1):
                    audit_bunch(dirname, overlappings_list)
    
    # Info for Siamak
    print('Duplicated documents (for Siamak):', duplicated_docs_dict)

    # Checkings before writing to disk
    if os.path.exists(corpus):
        utils.write_to_disk(distributions)
    else:
        utils.create_empty_files_from_csv_se(
            EMPTY_FILES_DIR, clusters_file, delimiter)

    # Printings to give feedback to the user
    for root, _, files in os.walk(ANN_DIR):
        print(root, len(files))
    print('Documents written to disk:', len(distributions))
    print('Initial pickings:', total_pickings)

    # Find the distinct documents to annotate
    regex = r'(sonespases_)?(\d+)(\.utf8)?\.txt'
    pattern = re.compile(regex)
    filenames = re.findall(pattern, str(distributions))

    print('Distinct annotations:', len(set(filenames)))
    print('Remaining spool:', len(spool))


if __name__ == '__main__':
    distribute_documents()
