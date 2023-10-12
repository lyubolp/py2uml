"""
Main program
"""
import argparse
from src.app import generate_uml_class_diagram


def setup_cli():
    """
    Setup CLI
    """
    parser = argparse.ArgumentParser(description='Generate UML class diagram from source folder')
    parser.add_argument('source_files', metavar='source_files', type=str, nargs='+',
                        help='Files to generate the diagram from')
    parser.add_argument('output_dir', metavar='output_dir', type=str, help='Output directory')


    return parser.parse_args()


if __name__ == "__main__":
    args = setup_cli()
    input_files = args.source_files
    output_file = args.output_dir

    uml = generate_uml_class_diagram(input_files, output_file)

