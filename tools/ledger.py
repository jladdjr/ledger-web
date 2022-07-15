#!/usr/bin/env python3

class Transaction:
    def __init__(self, date: str, description: str, transfers: list[str]):
        self.date = date
        self.description = description
        self.transfers = transfers

    def validate(self) -> bool:
        pass
