'''Tests for ictusnet.py script'''

from click.testing import CliRunner
from ictusnet import distribute_documents
import re


def test_execution_without_errors():
    runner = CliRunner()
    result = runner.invoke(distribute_documents,
                           ['--clusters-file', 'labels_sup_umap_emb_8.tsv'])
    assert result.exit_code == 0
    # assert result.output == 'Number of distinct annotations: 1202\n...'
