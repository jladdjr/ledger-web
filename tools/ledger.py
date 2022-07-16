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
