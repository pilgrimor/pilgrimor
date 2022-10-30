class BColors:
    """Colors for print function."""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def error_text(text: str) -> str:
    """
    Returns text in red.

    :param text: text to make red.

    :return: text in red.
    """
    return BColors.FAIL + text + BColors.ENDC


def attention_text(text: str) -> str:
    """
    Returns text in attention color.

    :param text: text to make blue.

    :return: text in blue.
    """
    return BColors.OKCYAN + text + BColors.ENDC


def warning_text(text: str) -> str:
    """
    Returns text in attention color.

    :param text: text to make orange.

    :return: text in orange.
    """
    return BColors.WARNING + text + BColors.ENDC


def success_text(text: str) -> str:
    """
    Print success text.

    :param text: text to print in green.

    :return: text in green.
    """
    return BColors.OKGREEN + text + BColors.ENDC
