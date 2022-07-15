import sys
import unittest
from unittest import mock

sys.path.append('..')

import ledger_adapter



class TestLedgerAdapter(unittest.TestCase):

    @mock.patch('ledger_adapter.open')
    def test_parse_simple_transaction(self, mock_open):
        mock_open.return_value.__enter__.return_value.readlines.return_value = """
2022/01/02 Simple Transaction
    Asset:MyBank:Checking  $123.45
    Income:Nerds, Inc.
""".split('\n')
        adapter = ledger_adapter.LedgerAdapter()
        ledger = adapter.import_ledger('fake.ledger')
        transactions = ledger.transactions()

        assert len(transactions) == 1
        t = transactions.pop()

        assert t.date == '2022/01/02'
        assert t.description == 'Simple Transaction'

        transfers = t.transfers()
        assert len(transfers) == 2
        assert transfers[0].account = 'Asset:MyBank:Checking'
        assert transfers[0].ammount = '$123.45'
        assert transfers[1].account = 'Income:Nerds, Inc.'
        assert transfers[1].ammount = ''

if __name__ == '__main__':
    unittest.main()
