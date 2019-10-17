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
from collections import Counter


def get_delimiter(csv_file: str) -> str:
    '''Return the field delimiter of the given CSV file.'''
    with open(csv_file) as csvfile:
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(csvfile.readline())
    return dialect.delimiter


# def create_empty_files_se(dirname: str, total_dummy_docs: int, extension: str):
#     '''Create some empty files with incremental numeric filenames in the given
#     new directory name.'''
#     if not os.path.exists(dirname):
#         os.makedirs(dirname)
#     for filename in range(1, total_dummy_docs + 1):
#         open(f'{dirname}/{filename}{extension}', 'w')


def create_empty_files_from_csv_se(dirname: str, csv_file: str, delimiter: str):
    '''Create as many empty files as there are tsv_file rows inside dirname.'''
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(csv_file) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delimiter)
        for row in reader:
            open(f"{dirname}/{row['file']}", 'w')


def create_docs_backup_se(source_dir: str, backup_dir: str):
    '''Create a complete backup of the given source directory into a new
    backup_dir, only if backup_dir doesn't exist yet.'''
    if not os.path.exists(backup_dir):
        shutil.copytree(source_dir, backup_dir)


def create_dirs_tree_se(root: str, dirs: Tuple[str, str, str, str],
                        subdirs: List[str]):
    '''Create a directory tree in the working directory.'''
    for directory in dirs:
        for subdir in subdirs:
            dirpath = os.path.join(root, directory, subdir)
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)

# def get_files_spool_old(source_dir: str) -> List[str]:
#     '''Return the list of all filenames without extension inside the given
#     directory.'''
#     filenames = list()
#     for root, dirs, files in os.walk(source_dir):
#         [filenames.append(f) for f in files]
#     return filenames


def get_clustered_dict(clusters_file: str, delimiter: str) -> Dict[str, List[str]]:
    '''Return a dictionary with the clusters id's as keys and the list of
    files as values.'''
    docs_clusters_spool = dict()
    with open(clusters_file) as csvfile:
        # # Write the header TODO
        # fieldnames = ['filename', 'cluster']
        # writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=delimiter)
        # writer.writeheader()

        # Read the rows
        reader = csv.DictReader(csvfile, delimiter=delimiter)
        for row in reader:
            if row['cluster'] not in docs_clusters_spool.keys():
                docs_clusters_spool[row['cluster']] = list()
            docs_clusters_spool[row['cluster']].append(row['file'])
    
    return docs_clusters_spool


def get_key_by_substr_in_values_lists(
        dictionary: Dict[str, List[str]], substr: str) -> str:
    '''Return the key from the given dictionary where the given substring is
    present inside the lists as dict values. If key is not found, return the
    empty string.'''
    found_key = str()
    found_keys = [key for key, value in dictionary.items()
                  for item in value if substr in item]
    if len(set(found_keys)) == 1:
        found_key = found_keys[0]
    return found_key


def count_element_in_list_of_tuples(
        list_of_tuples: List[Tuple[int, int]], element) -> int:
    '''Return the number of times that an element is present in the
    outter_list, that is a list of lists of tuples (src, tgt). For the IctusNET
    project, this is extremely useful in order to find out how many times an
    specific annotator is a target for copying an overlapped document in an
    audit run type.'''
    target_annotators = list()
    for (src, tgt) in list_of_tuples:
        target_annotators.append(tgt)
    return Counter(target_annotators)[element]
