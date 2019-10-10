'''Tests for ictusnet.py script'''

from click.testing import CliRunner
from ictusnet import main
import re

def test_remaining_docs_spool():
    '''remaining_docs_spool = TOTAL_DUMMY_DOCS - (trainings * TRAINING_BUNCH + regulars * REGULAR_BUNCH + audits * AUDIT_BUNCH)'''
    # TODO
    assert True
    
def test_without_any_option():
    runner = CliRunner()
    result = runner.invoke(main, ['--dummy'])
    result = runner.invoke(main)
    assert result.exit_code == 0
    assert result.output == '1202\n'
