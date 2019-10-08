from os import makedirs, path

dirname = 'dummy_docs'
docs = list(range(1, 201))

if not path.exists(dirname):
    makedirs(dirname)

for (index, doc) in enumerate(docs):
    f = open(f'{dirname}/{index + 1}.txt', 'w')
