"""
Main program
"""

import argparse
import os

from src.app import generate_uml_class_diagram
from src.file_utils import expand_directory


def setup_cli():
    """
    Setup CLI
    """
    parser = argparse.ArgumentParser(description="Generate UML class diagram from source folder")

    parser.add_argument(
        "source", metavar="source", type=str, nargs="+", help="Files/directories to generate the diagram from"
    )
    parser.add_argument("output_dir", metavar="output_dir", type=str, help="Output directory")

    parser.add_argument("-p", "--plantuml", action="store_true", default=True, help="Store PlantUML file (default)")
    parser.add_argument("-i", "--image", action="store_true", default=True, help="Store image file (default)")
    parser.add_argument("--version", action="version", version="Py2UML 1.0")

    return parser.parse_args()


if __name__ == "__main__":
    args = setup_cli()

    input_files = []

    for source in args.source:
        if os.path.isdir(source):
            input_files += expand_directory(source)
        elif os.path.isfile(source):
            input_files.append(source)
        else:
            # TODO - Logging
            print(f"Cannot find file or directory: {source}")

    input_files = [path for path in input_files if "venv" not in path]  # TODO - There is a better way to do this
    output_dir = args.output_dir

    generate_uml_class_diagram(input_files, output_dir, args.plantuml, args.image)
