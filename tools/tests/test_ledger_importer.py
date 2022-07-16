import sys
import unittest
from unittest import mock

sys.path.append('..')

from ledger import TransferStatus  # noqa
import ledger_importer  # noqa


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

    def test_scan_to_last_nonempty_line(self):
        text1 = ['a', 'b', 'c', ' ']
        self.assertEqual(ledger_importer._scan_to_last_nonempty_line(text1, 0), 2)
        self.assertEqual(ledger_importer._scan_to_last_nonempty_line(text1, 1), 2)
        self.assertEqual(ledger_importer._scan_to_last_nonempty_line(text1, 2), 2)
        self.assertEqual(ledger_importer._scan_to_last_nonempty_line(text1, 3), None)
        self.assertEqual(ledger_importer._scan_to_last_nonempty_line(text1, 4), None)
        self.assertEqual(ledger_importer._scan_to_last_nonempty_line(text1, -1), None)

        text2 = ['a', 'b', 'c', '']
        self.assertEqual(ledger_importer._scan_to_last_nonempty_line(text2, 0), 2)

        text3 = ['a', 'b', 'c', '\t']
        self.assertEqual(ledger_importer._scan_to_last_nonempty_line(text3, 0), 2)

        text4 = ['a', '']
        self.assertEqual(ledger_importer._scan_to_last_nonempty_line(text4, 0), 0)

        text5 = ['a', 'b', 'c']
        self.assertEqual(ledger_importer._scan_to_last_nonempty_line(text5, 0), 2)

        text6 = ['', ' ', '\t', 'a', 'b', 'c', '']
        self.assertEqual(ledger_importer._scan_to_last_nonempty_line(text6, 3), 5)
        self.assertEqual(ledger_importer._scan_to_last_nonempty_line(text6, 4), 5)
        self.assertEqual(ledger_importer._scan_to_last_nonempty_line(text6, 5), 5)

        text7 = []
        self.assertEqual(ledger_importer._scan_to_last_nonempty_line(text7, 0), None)

    def test_strip_line_comments(self):
        # Lines that only contain a comment
        # should be removed altogether
        lines = ['Some text',
                 '; Comment at beginning of line',
                 '  ; Indented comment',
                 'More text',
                 'Even more text',
                 ';; Comment with two semi-colons',
                 ';;; Comment with three semi-colons',
                 '',
                 'Yet another line with text',
                 '',
                 'Last line of text',
                 '',
                 ]

        expected_lines = ['Some text',
                          'More text',
                          'Even more text',
                          '',
                          'Yet another line with text',
                          '',
                          'Last line of text',
                          '',
                          ]
        self.assertEqual(ledger_importer._strip_comments(lines),
                         expected_lines)

    def test_strip_inline_comments(self):
        # Lines that only contain a comment
        # should be removed altogether
        lines = ['Some text',
                 'Some more text ; with comments',
                 '',
                 'Another line ;; with comments'
                 ]

        expected_lines = ['Some text',
                          'Some more text',
                          '',
                          'Another line'
                          ]
        self.assertEqual(ledger_importer._strip_comments(lines),
                         expected_lines)

    def test_parse_raw_amount(self):
        # negative cases
        cases = ['foo',
                 '-$4',
                 '5',
                 '5.32',
                 '2 dog dogs',
                 '$ 5',
                 '5 $5.00',
                 '$5.00 5',
                 '$3.00 dogs',
                 '$$2.00']
        for case in cases:
            with self.assertRaises(ledger_importer.MalformedTransfer):
                ledger_importer._parse_raw_amount(case)

        # dollars
        amt, unit = ledger_importer._parse_raw_amount('$123.45')
        self.assertEqual(amt, 123.45)
        self.assertEqual(unit, '$')

        amt, unit = ledger_importer._parse_raw_amount('$123')
        self.assertEqual(amt, 123.0)
        self.assertEqual(unit, '$')

        amt, unit = ledger_importer._parse_raw_amount('$-123.45')
        self.assertEqual(amt, -123.45)
        self.assertEqual(unit, '$')

        amt, unit = ledger_importer._parse_raw_amount('$-123')
        self.assertEqual(amt, -123.0)
        self.assertEqual(unit, '$')

        amt, unit = ledger_importer._parse_raw_amount('$.45')
        self.assertEqual(amt, 0.45)
        self.assertEqual(unit, '$')

        amt, unit = ledger_importer._parse_raw_amount('$0.45')
        self.assertEqual(amt, 0.45)
        self.assertEqual(unit, '$')

        amt, unit = ledger_importer._parse_raw_amount('$1,000.45')
        self.assertEqual(amt, 1000.45)
        self.assertEqual(unit, '$')

        amt, unit = ledger_importer._parse_raw_amount('$-1,000.45')
        self.assertEqual(amt, -1000.45)
        self.assertEqual(unit, '$')

        amt, unit = ledger_importer._parse_raw_amount('$1,000,000.45')
        self.assertEqual(amt, 1000000.45)
        self.assertEqual(unit, '$')

        amt, unit = ledger_importer._parse_raw_amount('$1000.45')
        self.assertEqual(amt, 1000.45)
        self.assertEqual(unit, '$')

        # euros
        amt, unit = ledger_importer._parse_raw_amount('€123.45')
        self.assertEqual(amt, 123.45)
        self.assertEqual(unit, '€')

        amt, unit = ledger_importer._parse_raw_amount('€123')
        self.assertEqual(amt, 123.0)
        self.assertEqual(unit, '€')

        amt, unit = ledger_importer._parse_raw_amount('€-123.45')
        self.assertEqual(amt, -123.45)
        self.assertEqual(unit, '€')

        amt, unit = ledger_importer._parse_raw_amount('€-123')
        self.assertEqual(amt, -123.0)
        self.assertEqual(unit, '€')

        # FOO stock
        amt, unit = ledger_importer._parse_raw_amount('123.45 FOO')
        self.assertEqual(amt, 123.45)
        self.assertEqual(unit, 'FOO')

        amt, unit = ledger_importer._parse_raw_amount('123 FOO')
        self.assertEqual(amt, 123.0)
        self.assertEqual(unit, 'FOO')

        amt, unit = ledger_importer._parse_raw_amount('-123.45 FOO')
        self.assertEqual(amt, -123.45)
        self.assertEqual(unit, 'FOO')

        amt, unit = ledger_importer._parse_raw_amount('-123 FOO')
        self.assertEqual(amt, -123.0)
        self.assertEqual(unit, 'FOO')

    def test_form_transaction_simple_case(self):
        lines = ['2022/07/14 Simple Transaction',
                 '    Asset:MyBank:Checking  $123.45',
                 '    Income:Nerds, Inc.']
        transaction = ledger_importer._form_transaction(lines)

        self.assertEqual(transaction.date, '2022/07/14')
        self.assertEqual(transaction.description, 'Simple Transaction')

        self.assertEqual(len(transaction.transfers), 2)
        transfer1, transfer2 = transaction.transfers
        self.assertEqual(transfer1.account, 'Asset:MyBank:Checking')
        self.assertEqual(transfer1.amount, 123.45)
        self.assertEqual(transfer1.unit, '$')
        self.assertEqual(transfer1.status, TransferStatus.DEFAULT)

        self.assertEqual(transfer2.account, 'Income:Nerds, Inc.')
        self.assertEqual(transfer2.amount, None)
        self.assertEqual(transfer2.unit, None)
        self.assertEqual(transfer2.status, TransferStatus.DEFAULT)

    def test_form_transaction_with_cleared_entry(self):
        lines = ['2022/07/14 Simple Transaction',
                 '    * Asset:MyBank:Checking  $123.45',
                 '    Income:Nerds, Inc.']
        transaction = ledger_importer._form_transaction(lines)

        self.assertEqual(transaction.date, '2022/07/14')
        self.assertEqual(transaction.description, 'Simple Transaction')

        self.assertEqual(len(transaction.transfers), 2)
        transfer1, transfer2 = transaction.transfers
        self.assertEqual(transfer1.account, 'Asset:MyBank:Checking')
        self.assertEqual(transfer1.amount, 123.45)
        self.assertEqual(transfer1.unit, '$')
        self.assertEqual(transfer1.status, TransferStatus.CLEARED)

        self.assertEqual(transfer2.account, 'Income:Nerds, Inc.')
        self.assertEqual(transfer2.amount, None)
        self.assertEqual(transfer2.unit, None)
        self.assertEqual(transfer2.status, TransferStatus.DEFAULT)

    def test_form_transaction_with_cleared_and_pending_entries(self):
        lines = ['2022/07/14 Simple Transaction',
                 '    ! Asset:MyBank:Checking  $123.45',
                 '    * Income:Nerds, Inc.']
        transaction = ledger_importer._form_transaction(lines)

        self.assertEqual(transaction.date, '2022/07/14')
        self.assertEqual(transaction.description, 'Simple Transaction')

        self.assertEqual(len(transaction.transfers), 2)
        transfer1, transfer2 = transaction.transfers
        self.assertEqual(transfer1.account, 'Asset:MyBank:Checking')
        self.assertEqual(transfer1.amount, 123.45)
        self.assertEqual(transfer1.unit, '$')
        self.assertEqual(transfer1.status, TransferStatus.PENDING)

        self.assertEqual(transfer2.account, 'Income:Nerds, Inc.')
        self.assertEqual(transfer2.amount, None)
        self.assertEqual(transfer2.unit, None)
        self.assertEqual(transfer2.status, TransferStatus.CLEARED)

    @mock.patch('ledger_importer.open')
    def test_parse_ledger_with_simple_transaction(self, mock_open):
        mock_open.return_value.__enter__.return_value.readlines.return_value = """
2022/01/02 Simple Transaction
    Asset:MyBank:Checking  $123.45
    Income:Nerds, Inc.
""".split('\n')
        transactions = ledger_importer.import_ledger('fake.ledger')

        self.assertEqual(len(transactions), 1)
        t = transactions[0]

        self.assertEqual(t.date, '2022/01/02')
        self.assertEqual(t.description, 'Simple Transaction')

        self.assertEqual(len(t.transfers), 2)
        transfer1, transfer2 = t.transfers
        self.assertEqual(transfer1.account, 'Asset:MyBank:Checking')
        self.assertEqual(transfer1.amount, 123.45)
        self.assertEqual(transfer1.unit, '$')
        self.assertEqual(transfer1.status, TransferStatus.DEFAULT)

        self.assertEqual(transfer2.account, 'Income:Nerds, Inc.')
        self.assertEqual(transfer2.amount, None)
        self.assertEqual(transfer2.unit, None)
        self.assertEqual(transfer2.status, TransferStatus.DEFAULT)

    @mock.patch('ledger_importer.open')
    def test_parse_ledger_with_multiple_simple_transactions(self, mock_open):
        mock_open.return_value.__enter__.return_value.readlines.return_value = """
2022/01/02 Consulting Income
    Asset:MyBank:Checking  $123.45
    Income:Nerds, Inc.

2022/01/03 20m CW HF Radio Kit
    Expenses:Hobby:Ham Radio  $75
    Asset:MyBank:Checking
""".split('\n')
        transactions = ledger_importer.import_ledger('fake.ledger')

        self.assertEqual(len(transactions), 2)
        t1 = transactions[0]

        self.assertEqual(t1.date, '2022/01/02')
        self.assertEqual(t1.description, 'Consulting Income')

        self.assertEqual(len(t1.transfers), 2)
        transfer1, transfer2 = t1.transfers
        self.assertEqual(transfer1.account, 'Asset:MyBank:Checking')
        self.assertEqual(transfer1.amount, 123.45)
        self.assertEqual(transfer1.unit, '$')
        self.assertEqual(transfer1.status, TransferStatus.DEFAULT)

        self.assertEqual(transfer2.account, 'Income:Nerds, Inc.')
        self.assertEqual(transfer2.amount, None)
        self.assertEqual(transfer2.unit, None)
        self.assertEqual(transfer2.status, TransferStatus.DEFAULT)

        t2 = transactions[1]
        self.assertEqual(t2.date, '2022/01/03')
        self.assertEqual(t2.description, '20m CW HF Radio Kit')

        self.assertEqual(len(t2.transfers), 2)
        transfer1, transfer2 = t2.transfers
        self.assertEqual(transfer1.account, 'Expenses:Hobby:Ham Radio')
        self.assertEqual(transfer1.amount, 75.0)
        self.assertEqual(transfer1.unit, '$')
        self.assertEqual(transfer1.status, TransferStatus.DEFAULT)

        self.assertEqual(transfer2.account, 'Asset:MyBank:Checking')
        self.assertEqual(transfer2.amount, None)
        self.assertEqual(transfer2.unit, None)
        self.assertEqual(transfer2.status, TransferStatus.DEFAULT)

    @mock.patch('ledger_importer.open')
    def test_parse_multiple_simple_transactions_with_comments(self, mock_open):
        mock_open.return_value.__enter__.return_value.readlines.return_value = """
; Pay day!
2022/01/02 Consulting Income
    Asset:MyBank:Checking  $123.45
    Income:Nerds, Inc.   ; ledger handles missing amounts for us

; These are some notes
; in between transactions

2022/01/03 20m CW HF Radio Kit
    ; Inline comment in the middle
    ; of a transaction
    Expenses:Hobby:Ham Radio  $75  ; add a comment here
    Asset:MyBank:Checking  ; .. and one here, too

;;;;;;;;;;;;;;;;;;;;;;;;
;; Big section header ;;
;;;;;;;;;;;;;;;;;;;;;;;;

; That's it!
""".split('\n')
        transactions = ledger_importer.import_ledger('fake.ledger')

        self.assertEqual(len(transactions), 2)
        t1 = transactions[0]

        self.assertEqual(t1.date, '2022/01/02')
        self.assertEqual(t1.description, 'Consulting Income')

        self.assertEqual(len(t1.transfers), 2)
        transfer1, transfer2 = t1.transfers
        self.assertEqual(transfer1.account, 'Asset:MyBank:Checking')
        self.assertEqual(transfer1.amount, 123.45)
        self.assertEqual(transfer1.unit, '$')
        self.assertEqual(transfer1.status, TransferStatus.DEFAULT)

        self.assertEqual(transfer2.account, 'Income:Nerds, Inc.')
        self.assertEqual(transfer2.amount, None)
        self.assertEqual(transfer2.unit, None)
        self.assertEqual(transfer2.status, TransferStatus.DEFAULT)

        t2 = transactions[1]
        self.assertEqual(t2.date, '2022/01/03')
        self.assertEqual(t2.description, '20m CW HF Radio Kit')

        self.assertEqual(len(t2.transfers), 2)
        transfer1, transfer2 = t2.transfers
        self.assertEqual(transfer1.account, 'Expenses:Hobby:Ham Radio')
        self.assertEqual(transfer1.amount, 75.0)
        self.assertEqual(transfer1.unit, '$')
        self.assertEqual(transfer1.status, TransferStatus.DEFAULT)

        self.assertEqual(transfer2.account, 'Asset:MyBank:Checking')
        self.assertEqual(transfer2.amount, None)
        self.assertEqual(transfer2.unit, None)
        self.assertEqual(transfer2.status, TransferStatus.DEFAULT)


if __name__ == '__main__':
    unittest.main()
