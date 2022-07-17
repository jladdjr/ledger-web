#!/usr/bin/env python3

from ledger import Ledger
from ledger_importer import import_ledger_file


def import_bank_transaction_profile():
    pass

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
