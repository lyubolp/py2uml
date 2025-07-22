"""
Main application logic
"""

import os

import src.converters.python_to_model as p2m
import src.converters.model_to_plantuml as m2p


def generate_uml_class_diagram(
    source_files: list[str], output_dir: str, is_saving_plantuml: bool = True, is_saving_image: bool = True
):
    """
    Generate UML class diagram from source folder
    """

    models = []
    for source_file in source_files:
        print(f"Generating model from {source_file}")
        with open(source_file, "r", encoding="utf-8") as file:
            file_contents = file.readlines()
            models.append(p2m.generate_models(file_contents))

    if is_saving_plantuml:
        output_path = os.path.join(output_dir, "diagram.puml")
    else:
        # TODO - Think about temporary files
        output_path = os.path.join(output_dir, "diagram.puml")

    print(models)
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w+", encoding="utf-8") as file:
        # TODO - Links
        content = m2p.generate_platuml_class_diagram(sum(models, []), None)
        content = [line + "\n" for line in content]
        file.writelines(content)
