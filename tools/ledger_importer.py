import logging
import re

from ledger import Transaction, Transfer, TransferStatus


logger = logging.getLogger(__name__)


class MalformedTransaction(Exception):
    pass


class MalformedTransfer(Exception):
    pass

def _has_text(s: str) -> bool:
    return len(s.strip()) != 0


def _scan_to_nonempty_line(text: list[str], start_line: int) -> int:
    """Return index of first non-empty line"""
    if len(text) == 0:
        return None
    if start_line < 0:
        return None

    curr_line = start_line
    while True:
        if curr_line >= len(text):
            # never found non-emtpy line
            return None
        if not _has_text(text[curr_line]):
            curr_line += 1
        else:
            return curr_line


def _scan_to_last_nonempty_line(text: list[str], start_line: int) -> int:
    """Return index of last non-empty line"""
    if len(text) == 0:
        return None
    if start_line < 0 or start_line >= len(text):
        return None

    # first line must have text
    if not _has_text(text[start_line]):
        return None

    # skip first line since we just confirmed
    # it has text
    curr_line = start_line + 1
    while True:
        if curr_line >= len(text):
            # in this case, the end of the text is
            # the boundary that determines the last
            # nonempty line
            return curr_line - 1
        if _has_text(text[curr_line]):
            curr_line += 1
        else:
            return curr_line - 1

def _strip_comments(lines: list[str]) -> list[str]:
    def has_content(line):
        """determine if line contains more than
        just a comment"""
        return not re.match(r'^\s*;.*$', line)
    lines_with_content = list(filter(has_content, lines))

    def strip_inline_comments(line):
        res = re.match(r'^([^;]*);.*$', line)

        if not res:
            # no comments found, return line as is
            return line
        # found a comment, return all content
        # preceeding the comment, except for any whitespace
        # found just before the comment
        return res.group(1).rstrip()

    lines_without_inline_comments = map(strip_inline_comments, lines_with_content)

    return list(lines_without_inline_comments)


def _parse_raw_amount(raw_amount: str) -> tuple[float, str]:
    """Returns amount and unit as tuple.

    Supports dollars, euros, and custom units.

    For example:
    - $500.00
    - €300.00
    - 2 FOO

    Note that negative sign must always come immediately
    before the amount in the original string.

    For example:
    - Valid: $-42.00
    - Not Valid: -$42.00

    Raises MalformedTransfer if it is unable to parse `raw_amount`
    into a unit and decimal amount.
    """
    try:
        # does this use dollars or euros?
        res = re.match(r'^([$€])(-?[0-9,.]*)$', raw_amount)
        if res is not None:
            unit = res.group(1)
            amount = float(res.group(2).replace(',', ''))
            return amount, unit

        # does this use a custom unit?
        res = re.match(r'^(-?[0-9,.]*) (\s+)$', raw_amount)
        if res is not None:
            unit = res.group(2)
            amount = float(res.group(1).replace(',', ''))  # might throw an exception
            return amount, unit
    except ValueError:
        raise MalformedTransfer(f'Unable to parse decimal amount given in {raw_amount}')

    raise MalformedTransfer(f'Unable to parse amount string: {raw_amount}')


def _parse_status_symbol(status_text):
    status_text = status_text.strip()
    if status_text == '':
        return TransferStatus.DEFAULT
    elif status_text == '!':
        return TransferStatus.PENDING
    elif status_text == '*':
        return TransferStatus.CLEARED
    else:
        raise MalformedTransfer(f'Unable to parse status from: {status_text}')


def _form_transaction(text: list[str]):
    # parse date
    date_text = text[0].split()[0]
    res = re.match(r'^\d{4}/\d{2}/\d{2}', date_text)
    if not res:
        raise MalformedTransaction(f'Expected date, found {text[0]}')
    date = res.group(0)

    # parse description
    res = re.match(r'^\d{4}/\d{2}/\d{2}\s+(.*)\s*$', text[0])
    if not res:
        raise MalformedTransaction(f'Could not find description, found: {text[0]}')
    description = res.group(1)

    # parse transfers
    if len(text) < 2:
        raise MalformedTransaction(f'Failed to find any transfers for {text[0]}')

    transfers = []
    found_empty_amount = False  # at most one transfer line can have an unspecified amount
    for line in text[1:]:
        # for cash transfers (currently only supports dollars, euros)
        # - must start with four (or more spaces)
        # - account can be a string without spaces
        #   or can have single spaces spread through name
        # - after account name must be two (or more) spaces
        # - amount must start with dollar or euro symbol
        # - and then have some amount
        res = re.match(r'^\s{4}\s*(([*!] )?)((\S+ )*\S+)\s{2}\s*([$€]\S+)$', line)
        if res:
            status = _parse_status_symbol(res.group(1))
            account = res.group(3)
            amount, unit = _parse_raw_amount(res.group(5))
            transfer = Transfer(account=account,
                                amount=amount,
                                unit=unit,
                                status=status)
            transfers.append(transfer)
            continue
        else:
            # for custom units (e.g. 5 apples)
            # - must start with four (or more spaces)
            # - account can be a string without spaces
            #   or can have single spaces spread through name
            # - after account name must be two (or more) spaces
            # - amount must have one or more non-space characters
            # - and unit must have one or more non-space characters
            res = re.match(r'^\s{4}\s*(([*!] )?)((\S+ )*\S+)\s{2}\s*(\S+ \S+)$', line)
            if res is not None:
                status = _parse_status_symbol(res.group(1))
                account = res.group(3)
                amount, unit = _parse_raw_amount(res.group(5))
                transfer = Transfer(account=account,
                                    amount=amount,
                                    unit=unit,
                                    status=status)
                transfers.append(transfer)
                continue

        # last possibility is that this is a transfer where the amount was left blank
        # - must start with four (or more spaces)
        # - account can be a string without spaces
        #   or can have single spaces spread through name
        # - after account, string can end, or there could be trailing spaces
        res = re.match(r'^\s{4}\s*((\S+ )*\S+)\s*$', line)
        if res is None:
            # we were just unable to parse this line
            raise MalformedTransaction(f'Unable to parse transfer: {line}')

        if found_empty_amount:
            raise MalformedTransaction(f'Found multiple transfers with no amount specified for {text[0]}')

        found_empty_amount = True
        transfer = Transfer(account=res.group(1),
                            amount=None,
                            unit=None)
        transfers.append(transfer)

    return Transaction(date=date, description=description, transfers=transfers)


def import_ledger(path: str) -> None:
    try:
        with open(path, 'r') as ledger_file:
            lines = ledger_file.readlines()
    except FileNotFoundError:
        logger.exception(f'Unable to open {path}')

    if len(lines) == 0:
        return []

    transactions = []

    last_end = -1  # inclusive
    while last_end < len(lines):
        start = _scan_to_nonempty_line(lines, last_end + 1)
        if start is None:
            break

        end = _scan_to_last_nonempty_line(lines, start)

        lines_without_comments = _strip_comments(lines[start:end + 1])

        # skip block if lines only contain comments
        if len(lines_without_comments) > 0:
            transaction = _form_transaction(lines_without_comments)
            transactions.append(transaction)

        last_end = end

    return transactions


if __name__ == '__main__':
    pass
