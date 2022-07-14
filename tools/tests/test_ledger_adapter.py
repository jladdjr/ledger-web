import sys
import unittest
from unittest import mock

sys.path.append('..')

import ledger_adapter



class TestLedgerAdapter(unittest.TestCase):

    @mock.patch('ledger_adapter.open')
    def test_parse_simple_transaction(self, mock_open):
        mock_open.return_value.__enter__.return_value.readlines.return_value = ['one', 'two']
        adapter = ledger_adapter.LedgerAdapter()
        ret = adapter.import_ledger('fake.ledger')
        assert ret == ['one', 'two']

if __name__ == '__main__':
    unittest.main()
