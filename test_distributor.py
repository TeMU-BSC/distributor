'''Tests for distributor.py script'''

from click.testing import CliRunner
from distributor import distribute_documents, EMPTY_FILES_DIR

runner = CliRunner()

def test_create_empty_corpus():
    result = runner.invoke(distribute_documents,
                           ['clusters/labels_sup_umap_emb_8.tsv', 'i_dont_exist_dir', 'A', 'B', 'C', 'D'])
    assert result.exit_code == 0


def test_distribute_real_corpus():
    result = runner.invoke(distribute_documents, [
                           'clusters/labels_sup_umap_emb_8.tsv', EMPTY_FILES_DIR, 'A', 'B', 'C', 'D'])
    assert result.exit_code == 0
