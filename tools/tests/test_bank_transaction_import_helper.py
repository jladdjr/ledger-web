import unittest
from unittest import mock

import bank_transaction_import_helper as bank_tx_helper


class TestBankTransactionImportHelper(unittest.TestCase):

    @mock.patch('bank_transaction_import_helper.open')
    def test_import_bank_transaction_profile(self, mock_open):
        open_ctx_mgr = mock_open.return_value.__enter__.return_value
        open_ctx_mgr.read.return_value = """
banks:
  mybank:
    transaction_column_mapping:
      amount: 5
  my_credit_card:
    transaction_column_mapping:
      credit_amount: 2
      debit_amount: 3
"""

        bank_profiles = bank_tx_helper.import_bank_transaction_profile('fake_bank_import_config.yml')

        self.assertEqual(len(bank_profiles), 2)

        bank_profile1 = bank_profiles[0]
        self.assertEqual(bank_profile1.bank_alias, 'mybank')
        self.assertEqual(bank_profile1.amount, 5)
        self.assertEqual(bank_profile1.credit_amount, None)
        self.assertEqual(bank_profile1.debit_amount, None)

        bank_profile2 = bank_profiles[1]
        self.assertEqual(bank_profile2.bank_alias, 'my_credit_card')
        self.assertEqual(bank_profile2.amount, None)
        self.assertEqual(bank_profile2.credit_amount, 2)
        self.assertEqual(bank_profile2.debit_amount, 3)

#     @mock.patch('bank_transaction_import_helper.open')
#     def test_import_bank_transactions(self, mock_open):
#         mock_open.return_value.__enter__.return_value = iter("""\
# header_1, header_2, header_3
# a, b, c
# 1, 2, 3""".split('\n'))
#         bank_tx_helper.import_bank_transactions('fake_transactions.csv', )
