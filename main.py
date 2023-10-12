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
    parser.add_argument('output_file', metavar='output_file', type=str, help='Output file')

    parser.add_argument('-u', '--uml', action='store_true', help='Generate the PlantUML file')
    parser.add_argument('-p', '--png', action='store_true', default=True,
                        help='Generate the PNG file (default)')

    return parser.parse_args()


if __name__ == "__main__":
    args = setup_cli()
    input_files = args.source_files
    output_file = args.output_file

    is_generate_uml = args.uml
    is_generate_png = args.png

    generate_uml_class_diagram(input_files, output_file)
