"""
Module containing the converters which will be used to generate the UML diagrams.
"""
from typing import Optional

from src.models import ClassModel, ClassType, LinkType, Method, Variable, Visibility

__all__ = ['generate_platuml_class_diagram']

ClassLink = tuple[LinkType, ClassModel]

LINK_TYPE_TO_PLANTUML = {
    LinkType.EXTENSION: '<|--',
    LinkType.COMPOSITION: '*--',
    LinkType.AGGREGATION: 'o--',
    LinkType.NORMAL: '--'
}

VISIBILITY_TO_PLANTUML = {
    Visibility.PRIVATE: '-',
    Visibility.PROTECTED: '#',
    Visibility.PUBLIC: '+',
}

CLASS_TYPE_TO_PLANTUML = {
    ClassType.ABSTRACT: 'abstract',
    ClassType.CLASS: 'class',
    ClassType.ENUM: 'enum',
    ClassType.EXCEPTION: 'exception'
}

STATIC_METHOD_TO_PLANTUML = '{static}'
ABSTRACT_METHOD_TO_PLANTUML = '{abstract}'


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

    contents.append(f'{CLASS_TYPE_TO_PLANTUML[class_model.class_type]} {class_model.name} ' + '{')

    # Handle attributes
    if class_model.attributes is not None:
        contents += generate_plantuml_class_attributes(class_model)

    # Handle methods
    if class_model.methods is not None:
        contents += generate_plantuml_class_methods(class_model)

    # Handle static methods
    if class_model.static_methods is not None:
        contents += generate_plantuml_static_methods(class_model)

    # Handle abstract methods
    if class_model.abstract_methods is not None:
        contents += generate_plantuml_abstract_methods(class_model)

    contents.append('}')
    return contents


def generate_plantuml_link(class_model: ClassModel, link: ClassLink) -> str:
    """
    Generate the plantuml link between two classes.
    :param class_model: The class model.
    :param link: The link between the two classes.
    :return: The PlantUML code for the link.
    """
    return f'{class_model.name} {LINK_TYPE_TO_PLANTUML[link[0]]} {link[1].name}'


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
    attribute_visibility = VISIBILITY_TO_PLANTUML[attribute.visibility]

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
    method_visibility = VISIBILITY_TO_PLANTUML[method.visibility]
    method_return_type = method.return_type if method.return_type is not None else ''

    method_arguments = ''

    if method.arguments is not None:
        method_arguments = ', '.join([f'{argument.variable_type} {argument.name}'
                                      for argument in method.arguments])

    items = [method_visibility, method.name, '(', method_arguments, ')']

    if method_return_type != '':
        items += [': ', method_return_type]

    return '\t' + ''.join(items)


def generate_plantuml_static_methods(class_model: ClassModel) -> list[str]:
    """
    Generate the PlantUML code for the static methods of a class.
    :param class_method: The class model.
    :return: The PlantUML code for the static methods of the class.
    """
    if class_model.static_methods is None:
        return []

    return [generate_plantuml_static_method(method) for method in class_model.static_methods]


def generate_plantuml_static_method(method: Method) -> str:
    """
    Generate the PlantUML code for a static method.
    :param method: The method to generate the code for.
    :return: The PlantUML code for the static method.
    """
    return STATIC_METHOD_TO_PLANTUML + ' ' + generate_plantuml_class_method(method)


def generate_plantuml_abstract_methods(class_model: ClassModel) -> list[str]:
    """
    Generate the PlantUML code for the abstract methods of a class.
    :param class_method: The class model.
    :return: The PlantUML code for the abstract methods of the class.
    """
    if class_model.abstract_methods is None:
        return []

    return [generate_plantuml_abstract_method(method) for method in class_model.abstract_methods]


def generate_plantuml_abstract_method(method: Method) -> str:
    """
    Generate the PlantUML code for a abstract method.
    :param method: The method to generate the code for.
    :return: The PlantUML code for the abstract method.
    """
    return ABSTRACT_METHOD_TO_PLANTUML + ' ' + generate_plantuml_class_method(method)
