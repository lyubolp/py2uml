"""
Module containing functions for file handling.
"""
import os


def expand_directory(directory_path: str) -> list[str]:
    """
    Functions that returns a list of all python files in a directory
    :param directory_path: Path to directory
    :return: List of all python files in directory
    """

    files = []

    for dirpath, _, filenames in os.walk(directory_path):
        for filename in filenames:
            if filename.endswith('.py') and not filename.startswith('__'):
                files.append(os.path.join(dirpath, filename))

    return files
