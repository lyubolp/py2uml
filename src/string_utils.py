def get_indentation_level(line: str) -> int:
    """
    Get the indentation level of a line of code.

    :param line: The line of code to check.
    :return: The number of leading spaces in the line.
    """
    return len(line) - len(line.lstrip())
