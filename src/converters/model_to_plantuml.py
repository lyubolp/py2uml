"""
Module containing the converters which will be used to generate the UML diagrams.
"""
from typing import Optional

from src.models import ClassModel, LinkType, Method, Variable, Visibility

__all__ = ['generate_platuml_class_diagram']

ClassLink = tuple[LinkType, ClassModel]

link_type_to_plantuml = {
    LinkType.EXTENSION: '<|--',
    LinkType.COMPOSITION: '*--',
    LinkType.AGGREGATION: 'o--',
    LinkType.NORMAL: '--'
}

visibility_to_plantuml = {
    Visibility.PRIVATE: '-',
    Visibility.PROTECTED: '#',
    Visibility.PUBLIC: '+',
}


def generate_platuml_class_diagram(classes: list[ClassModel],
                                   links: Optional[dict[ClassModel,
                                                        list[ClassLink]]]) -> list[str]:
    """
    Generate the PlantUML code for a class diagram.
    :param classes: The classes of the diagram.
    :param links: The links between the classes.
    :return: The PlantUML code for the class diagram.
    """
    contents = []

    # TODO - Move the hardcoded string to a template file
    contents.append("@startuml")

    # TODO - Support for themes ?

    if links is not None:
        for class_model, class_links in links.items():
            contents += [generate_plantuml_link(class_model, link) for link in class_links]

    for class_model in classes:
        contents += generate_plantuml_class(class_model)

    contents.append("@enduml")
    return contents


def generate_plantuml_class(class_model: ClassModel) -> list[str]:
    """
    Generate the PlantUML code for a class.
    :param class_model: The class to generate the code for.
    :return: The PlantUML code for the class.
    """
    contents = []

    # TODO - Move the hardcoded string to a template file
    contents.append(f'class {class_model.name} ' + '{')

    if class_model.attributes is not None:
        contents += generate_plantuml_class_attributes(class_model)

    contents.append('}')
    return contents


def generate_plantuml_link(class_model: ClassModel, link: ClassLink) -> str:
    """
    Generate the plantuml link between two classes.
    :param class_model: The class model.
    :param link: The link between the two classes.
    :return: The PlantUML code for the link.
    """
    return f'{class_model.name} {link_type_to_plantuml[link[0]]} {link[1].name}'


def generate_plantuml_class_attributes(class_model: ClassModel) -> list[str]:
    """
    Generate the PlantUML code for the attributes of a class.
    :param class_model: The class model.
    :return: The PlantUML code for the attributes of the class.
    """
    if class_model.attributes is None:
        return []

    return [generate_plantuml_class_attribute(attribute) for attribute in class_model.attributes]


def generate_plantuml_class_attribute(attribute: Variable) -> str:
    """
    Generate the PlantUML code for a class attribute.
    :param attribute: The attribute to generate the code for.
    :return: The PlantUML code for the attribute.
    """
    attribute_visibility = visibility_to_plantuml[attribute.visibility]

    return f'\t{attribute_visibility}{attribute.variable_type} {attribute.name}'


def generate_plantuml_class_methods(class_model: ClassModel) -> list[str]:
    """
    Generate the PlantUML code for the methods of a class.
    :param class_model: The class model.
    :return: The PlantUML code for the methods of the class.
    """
    if class_model.methods is None:
        return []

    return [generate_plantuml_class_method(method) for method in class_model.methods]


def generate_plantuml_class_method(method: Method) -> str:
    """
    Generate the PlantUML code for a class method.
    :param method: The method to generate the code for.
    :return: The PlantUML code for the method.
    """
    method_visibility = visibility_to_plantuml[method.visibility]
    method_return_type = method.return_type if method.return_type is not None else ''

    method_arguments = ''

    if method.arguments is not None:
        method_arguments = ', '.join([f'{argument.variable_type} {argument.name}'
                                      for argument in method.arguments])

    return f'\t{method_visibility}{method.name}({method_arguments}): {method_return_type}'
