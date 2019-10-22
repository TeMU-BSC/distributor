'''
Module with useful functions for the ictusnet command-line script.

WARNING: Some functions have `_se` at the end of their names, indicating that
this funcion has a Side Effect (SE), for example, writing to disk. Use those
functions with caution.

Author of this utils module:
    Alejandro Asensio <alejandro.asensio@bsc.es>
'''

import csv
import os
import shutil
from typing import Dict, List, Tuple


def get_delimiter(csv_file: str) -> str:
    '''Return the field delimiter of the given CSV file.'''
    with open(csv_file) as csvfile:
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(csvfile.readline())
    return dialect.delimiter


def create_empty_files_from_csv_se(
        dirname: str, csv_file: str, delimiter: str):
    '''Create as many empty files as there are tsv_file rows inside dirname.'''
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(csv_file) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delimiter)
        for row in reader:
            open(f"{dirname}/{row['file']}", 'w')


def get_clustered_dict(
        clusters_file: str, delimiter: str) -> Dict[str, List[str]]:
    '''Return a dictionary with the clusters id's as keys and the list of
    files as values.'''
    docs_clusters_spool = dict()
    with open(clusters_file) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delimiter)
        for row in reader:
            if row['cluster'] not in docs_clusters_spool.keys():
                docs_clusters_spool[row['cluster']] = list()
            docs_clusters_spool[row['cluster']].append(row['file'])
    return docs_clusters_spool


def get_key_by_substr_in_values(
        dictionary: Dict[str, List[str]], substr: str) -> str:
    '''Return the key from the given dictionary where the given substring is
    present inside the containing lists (dict values). If key is not found,
    return the empty string.'''
    found_key = str()
    found_keys = [key for key, value in dictionary.items()
                  for item in value if substr in item]
    if len(set(found_keys)) == 1:
        found_key = found_keys[0]
    return found_key


def write_to_disk(distributions: List[Tuple[str, str]]):
    '''Copy files from source path to destinations, creating the needed
    directory tree.'''
    for (src, dst) in distributions:
        if not os.path.exists(dst):
            os.makedirs(dst)
        shutil.copy2(src, dst)
