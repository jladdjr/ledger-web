import sys
import unittest
from unittest import mock

sys.path.append('..')

import ledger_importer


class TestLedgerImporter(unittest.TestCase):

    def test_has_text(self):
        self.assertEqual(ledger_importer._has_text(''), False)
        self.assertEqual(ledger_importer._has_text(' '), False)
        self.assertEqual(ledger_importer._has_text('   '), False)
        self.assertEqual(ledger_importer._has_text('\t'), False)
        self.assertEqual(ledger_importer._has_text('a'), True)
        self.assertEqual(ledger_importer._has_text('2022/07/14 Some Trannsaction'), True)
        self.assertEqual(ledger_importer._has_text('    Foo:Bar:Baz  $192.50'), True)
        self.assertEqual(ledger_importer._has_text('    Biz:Baz'), True)

    def test_scan_to_nonempty_line(self):
        text1 = ['a', 'b', 'c']
        self.assertEqual(ledger_importer._scan_to_nonempty_line(text1, 0), 0)
        self.assertEqual(ledger_importer._scan_to_nonempty_line(text1, 1), 1)
        self.assertEqual(ledger_importer._scan_to_nonempty_line(text1, 2), 2)
        self.assertEqual(ledger_importer._scan_to_nonempty_line(text1, 3), None)
        self.assertEqual(ledger_importer._scan_to_nonempty_line(text1, -1), None)

        text2 = ['', ' ', '\t', 'test']
        self.assertEqual(ledger_importer._scan_to_nonempty_line(text2, 0), 3)

        text3 = ['', ' ', '\t', 'test', ' ', ' ', '   ', 'foo', ' ', ' ']
        self.assertEqual(ledger_importer._scan_to_nonempty_line(text3, 0), 3)
        self.assertEqual(ledger_importer._scan_to_nonempty_line(text3, 3), 3)
        self.assertEqual(ledger_importer._scan_to_nonempty_line(text3, 4), 7)
        self.assertEqual(ledger_importer._scan_to_nonempty_line(text3, 5), 7)
        self.assertEqual(ledger_importer._scan_to_nonempty_line(text3, 6), 7)
        self.assertEqual(ledger_importer._scan_to_nonempty_line(text3, 7), 7)
        self.assertEqual(ledger_importer._scan_to_nonempty_line(text3, 8), None)
        self.assertEqual(ledger_importer._scan_to_nonempty_line(text3, 9), None)
        self.assertEqual(ledger_importer._scan_to_nonempty_line(text3, len(text3)), None)

    def test_form_transaction_simple_case(self):
        lines = ['2022/07/14 Simple Transaction',
                 '    Asset:MyBank:Checking  $123.45',
                 '    Income:Nerds, Inc.']
        transaction = ledger_importer._form_transaction(lines)

        self.assertEqual(transaction.date, '2022/07/14')
        self.assertEqual(transaction.description, 'Simple Transaction')
        transfers = transaction.transfers
        self.assertEqual(len(transfers), 2)
        self.assertEqual(transfers[0], ('Asset:MyBank:Checking', '$123.45'))
        self.assertEqual(transfers[1], ('Income:Nerds, Inc.', None))


#     @mock.patch('ledger_importer.open')
#     def test_parse_simple_transaction(self, mock_open):
#         mock_open.return_value.__enter__.return_value.readlines.return_value = """
# 2022/01/02 Simple Transaction
#     Asset:MyBank:Checking  $123.45
#     Income:Nerds, Inc.
# """.split('\n')
#         ledger = ledger_importer.import_ledger('fake.ledger')
#         transactions = ledger.transactions()

#         assert len(transactions) == 1
#         t = transactions.pop()

#         assert t.date == '2022/01/02'
#         assert t.description == 'Simple Transaction'

#         transfers = t.transfers()
#         assert len(transfers) == 2
#         assert transfers[0].account = 'Asset:MyBank:Checking'
#         assert transfers[0].ammount = '$123.45'
#         assert transfers[1].account = 'Income:Nerds, Inc.'
#         assert transfers[1].ammount = ''

if __name__ == '__main__':
    unittest.main()
