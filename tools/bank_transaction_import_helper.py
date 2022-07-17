#!/usr/bin/env python3

import csv
from typing import Union

import yaml

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

    bank_profiles = {}
    for bank in bank_configs['banks']:
        config = bank_configs['banks'][bank]['transaction_column_mapping']

        amount_col = config.get('amount', None)
        credit_amount_col = config.get('credit_amount', None)
        debit_amount_col = config.get('debit_amount', None)

        profile = BankTransactionProfile(bank, amount_col,
                                         credit_amount_col, debit_amount_col)
        bank_profiles[bank] = profile

    return bank_profiles


def import_bank_transactions(path: str, bank_profile: BankTransactionProfile):
    """Note: Function currently does not handle files with windows
    line endings (e.g. \r\n, unix systems show an extra ^M at the end of the line)"""
    amount_col = bank_profile.amount
    credit_amount_col = bank_profile.credit_amount
    debit_amount_col = bank_profile.debit_amount

    def get_amount(csv_row):
        if amount_col:
            return csv_row[amount_col]
        credit = csv_row[credit_amount_col]
        debit = csv_row[debit_amount_col]

        if len(credit) > 0:
            return float(credit)
        else:
            return -1.0 * float(debit)

    amount_to_full_transaction_tuples = []
    with open(path, 'r', newline='') as f:
        reader = csv.reader(f)

        first_row = True
        for row in reader:
            if first_row:
                first_row = False
                continue
            amount = get_amount(row)
            row_as_str = ', '.join(row)
            amount_to_full_transaction_tuples.append((amount, row_as_str))

    return amount_to_full_transaction_tuples

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
    # quick and dirty approach to have something useful rn
    ledger = import_ledger_file('/home/jim/ledger/ladds.ledger')

    profiles = import_bank_transaction_profile('/home/jim/.ledgerweb/bank_config.yml')
    profile = profiles['onpoint']

    # bank_transactions = import_bank_transactions('/home/jim/ledger/statements/chase/transactions.csv', profile)
    bank_transactions = import_bank_transactions('/home/jim/ledger/statements/onpoint/transactions.csv', profile)

    for tx in bank_transactions:
        found_match = False
        amount = abs(float(tx[0]))
        raw_line = tx[1]

        for ledger_tx in ledger.transactions:
            if found_match:
                break
            for transfer in ledger_tx.transfers:
                if found_match:
                    break
                ledger_tx_amount = transfer.amount
                if ledger_tx_amount == amount:
                    found_match = True

        if not found_match:
            print(f'MISSING: {amount} => {raw_line}')
