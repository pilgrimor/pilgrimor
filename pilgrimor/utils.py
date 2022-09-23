from itertools import cycle
from shutil import get_terminal_size
from threading import Thread
from time import sleep


class BColors:
    """Colors for print function."""

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def error_text(text: str) -> str:
    """
    Returns text in red.

    :param text: text to make red.
    """
    return BColors.FAIL + text + BColors.ENDC


def attention_text(text: str) -> str:
    """
    Returns text in attention color.

    :param text: text to make blue.
    """
    return BColors.OKCYAN + text + BColors.ENDC


def warning_text(text: str) -> str:
    """
    Returns text in attention color.

    :param text: text to make blue.
    """
    return BColors.WARNING + text + BColors.ENDC


def success_text(text: str) -> str:
    """
    Print success text.

    :param text: text to print.
    """
    return BColors.OKGREEN + text + BColors.ENDC


def eprint(text: str) -> None:
    """
    Print error text.

    :param text: text to print.
    """
    print(BColors.FAIL + text + BColors.ENDC)


def aprint(text: str) -> None:
    """
    Print attention text.

    :param text: text to print.
    """
    print(BColors.OKCYAN + text + BColors.ENDC)


def wprint(text: str) -> None:
    """
    Print warning text.

    :param text: text to print.
    """
    print(BColors.WARNING + text + BColors.ENDC)


def sprint(text: str) -> None:
    """
    Print success text.

    :param text: text to print.
    """
    print(BColors.OKGREEN + text + BColors.ENDC)
