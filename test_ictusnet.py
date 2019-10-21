'''Tests for ictusnet.py script'''

from click.testing import CliRunner
from ictusnet import distribute_documents


def test_execution():
    runner = CliRunner()
    result = runner.invoke(distribute_documents,
                           ['--clusters-file', 'labels_sup_umap_emb_8.tsv',
                            '--create-empty-corpus'])
    assert result.exit_code == 0
