'''
Script to assign massively all the documents to a given list of annotators.
Project: ICTUSnet
Version: 1
Date: 2019-10-08
Algorithm idea: Ankush Rana -- ankush.ran13@gmail.com
Author: Alejandro Asensio -- github.com/aasensios

TODO add click decorator to accept a directory name that contain the document files and the new directory name for this run (e.g. '03')
'''

import click


@click.command()
# @click.option('--docs', default=list(range(1, 201)), prompt='Documents path', help='Path that exclusively contains the documents to annotate.')
@click.option('--docs', default=list(range(1, 251)))
@click.option('--annotators', default=['A', 'B', 'C', 'D'], help='Names of the annotators.')
def overlapping_run(docs, annotators):
    '''Function that chooses the documents to provide to the annotators in the overlapping run.'''

    # Define the bunch of docs per annotator
    bunch = 50

    # First annotator (A)
    A = docs[bunch:bunch * 2]
    # overlapping_indexes = [0, 1, 6, 7, 8]
    overlapping_indexes = [50, 51, 56, 57, 58]
    overlapping_docs = [docs[i] for i in overlapping_indexes]
    print(A)
    print(len(A))
    print('---')


    # Second annotator (B)
    B = overlapping_docs[:2]
    next_docs = docs[bunch * 2:bunch * 3][:-2]
    overlapping_docs = next_docs[:2]
    B.extend(next_docs)
    print(B)
    print(len(B))
    print('---')


    # Third annotator (C)
    C = docs[(bunch * 3) - 2:(bunch * 4 - 4)][:2]
    C.extend(overlapping_docs)
    next_docs = docs[bunch * 3:(bunch * 4) - 4]
    overlapping_docs = next_docs[:2]
    C.extend(next_docs)
    print(C)
    print(len(C))
    print('---')

    # Fourth annotator (D)
    
    D = docs[(bunch * 4) - 4:(bunch * 5 - 10)][:3]
    D.append(B[3])
    D.extend(overlapping_docs)
    D.extend(A[6:9])
    next_docs = docs[(bunch * 4) - 1:(bunch * 5 - 10)]
    D.extend(next_docs)

    print(D)
    print(len(D))
    print('---')


if __name__ == '__main__':
    overlapping_run()
