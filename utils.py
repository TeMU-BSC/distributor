'''
Module with useful functions for the ictusnet command-line script.

WARNING: Some functions have `_se` at the end of their names, indicating that
this funcion has a Side Effect (SE), for example, writing to disk. Use those
functions with caution.

Author of this utils module:
    Alejandro Asensio <alejandro.asensio@bsc.es>
'''

import os
import shutil
from typing import List, Tuple
from collections import Counter


def create_empty_files_se(dirname: str, total_dummy_docs: int, extension: str):
    '''Create some empty files with incremental numeric filenames in the given
    new directory name.'''
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    for filename in range(1, total_dummy_docs + 1):
        open(f'{dirname}/{filename}{extension}', 'w')


def create_docs_backup_se(source_dir: str, backup_dir: str):
    '''Create a complete backup of the given source directory into a new
    backup_dir, only if backup_dir doesn't exist yet.'''
    if not os.path.exists(backup_dir):
        shutil.copytree(source_dir, backup_dir)


def get_files(source_dir: str) -> List[str]:
    '''Return the list of all filenames without extension inside the given directory.'''
    filenames = list()
    for root, dirs, files in os.walk(source_dir):
        [filenames.append(f) for f in files]
    return filenames


def create_dirs_tree_se(root: str, dirs: Tuple[str, str, str, str],
                        subdirs: List[str]):
    '''Create a directory tree in the working directory.'''
    for directory in dirs:
        for subdir in subdirs:
            # dirpath = f'{root}/{directory}/{subdir}/'
            dirpath = os.path.join(root, directory, subdir)
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)

def count_occurrences_in_list_of_list_of_tuples(
    outter_list: List[List[tuple]], element) -> int:
    '''Return the number of times that an element is present in the
    outter_list, that is a list of lists of tuples (src, tgt).
    For the IctusNET project, this is extremely useful in order to find out how
    many times an specific annotator is a target for copying an overlapped
    document in an audit run type.'''
    target_annotators = list()
    for inner_list in outter_list:
        for (src, tgt) in inner_list:
            target_annotators.append(tgt)
    return Counter(target_annotators)[element]
