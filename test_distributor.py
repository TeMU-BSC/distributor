'''Tests for distributor.py script'''

from click.testing import CliRunner
from distributor import distribute_documents, TEST_DIR

runner = CliRunner()

def test_create_empty_corpus():
    result = runner.invoke(distribute_documents,
                           ['clusters.tsv', 'i_dont_exist', 'A', 'B', 'C', 'D'])
    assert result.exit_code == 0


def test_distribute_real_corpus():
    result = runner.invoke(distribute_documents, [
                           'clusters.tsv', TEST_DIR, 'A', 'B', 'C', 'D'])
    assert result.exit_code == 0
