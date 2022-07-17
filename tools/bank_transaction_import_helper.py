#!/usr/bin/env python3

from typing import Union

import yaml

from ledger import Ledger
from ledger_importer import import_ledger_file


class BankTransactionProfile:
    def __init__(self, bank_alias: str,
                 amount: Union[int, None] = None,
                 credit_amount: Union[int, None] = None,
                 debit_amount: Union[int, None] = None):
        self.bank_alias = bank_alias
        self.amount = amount
        self.credit_amount = credit_amount
        self.debit_amount = debit_amount


def import_bank_transaction_profile(path: str):
    with open(path, 'r') as f:
        raw_config = f.read()
        bank_configs = yaml.safe_load(raw_config)

    bank_profiles = []
    for bank in bank_configs['banks']:
        config = bank_configs['banks'][bank]['transaction_column_mapping']

        amount_col = config.get('amount', None)
        credit_amount_col = config.get('credit_amount', None)
        debit_amount_col = config.get('debit_amount', None)

        profile = BankTransactionProfile(bank, amount_col,
                                         credit_amount_col, debit_amount_col)
        bank_profiles.append(profile)

    return bank_profiles

# import bank csv file
# interactively ask what each column represents
# offer to save the colummn mapping as a bank csv profile

# create empty ledger object
# load a listener that creates an index of transactions by amount and date

# for each item in the bank list (optionally starting from a given start date)
# check to see if amount is listed (and if so, ensure transaction's date is
# relatively close to the one given)

# list all transactions that are clearly not listed
# list all transactions that seem suspect because date is pretty far off
# list all transactions that have an amount and date that is close to
#   those listed in transactions that haven't been accounted foreign
# and, in the future, could maybe get fancy and try to determine
# if a transaction is actually split into several transactions in
# the ledger file


if __name__ == '__main__':
    pass