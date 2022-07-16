#!/usr/bin/env python3

from enum import Enum
from typing import Union


class Transaction:
    def __init__(self, date: str, description: str, transfers: list[str]):
        self.date = date
        self.description = description
        self.transfers = transfers

    def validate(self) -> bool:
        pass


class TransferStatus(Enum):
    DEFAULT = 1
    PENDING = 2
    CLEARED = 3


class Transfer:
    def __init__(self, account: str,
                 amount: Union[float, None] = None,
                 unit: Union[str, None] = None,
                 status: TransferStatus = TransferStatus.DEFAULT):
        self.account = account
        self.amount = amount
        self.unit = unit
        self.status = status


class LedgerListenerType(Enum):
    ADD_TRANSACTION = 1


class LedgerPluginManager:
    def __init__(self):
        self.add_transaction_listeners = []

    def register_listener(self, type: LedgerListenerType, f: callable):
        self.add_transaction_listeners.append(f)

    def trigger(self, type: LedgerListenerType, *args, **kwargs):
        if type == LedgerListenerType.ADD_TRANSACTION:
            for f in self.add_transaction_listeners:
                f(*args, **kwargs)


class Ledger:
    def __init__(self):
        self.transactions = []
        self.plugin_mgr = LedgerPluginManager()

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

        self.plugin_mgr.trigger(LedgerListenerType.ADD_TRANSACTION, transaction)

    def get_plugin_manager(self):
        return self.plugin_mgr
