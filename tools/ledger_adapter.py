class LedgerAdapter:
    def import_ledger(self, path):
        with open(path) as ledger_file:
            lines = ledger_file.readlines()
            return lines

if __name__ == '__main__':
    unittest.main()
