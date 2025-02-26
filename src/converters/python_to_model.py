"""
Module containing the converters which will be used to create the models from the Python code.
"""

import re

from enum import Enum
from re import Pattern

from src.models import ClassModel, ClassType, Method, Variable, Visibility

# Class-related patterns
class_pattern = re.compile(r"class (.*):")
class_name_pattern = re.compile(r"class ([a-zA-Z0-9]*).*:")
class_parents_pattern = re.compile(r"class .*\((.*)\)")

# Attribute-related patterns
attribute_pattern = re.compile(r"self\.(.*) =")
attribute_name_pattern = re.compile(r"self\.(_){0,2}(.*) =")
argument_type_pattern = re.compile(r"self\..* *: *(.*) =")

# Method-related patterns
method_pattern = re.compile(r"def .*\(self.*\).*:")
method_name_pattern = re.compile(r"def (.*)\(self.*")
method_return_type_pattern = re.compile(r"def .*\(.*\) *-> *([a-zA-Z0-9_-]*).*")

# Argument-related patterns
# TODO - Consider changing all other variable name captures to this group
argument_pattern = re.compile(r"([a-zA-Z0-9_-]).*")
argument_type_pattern = re.compile(r".*: *(.*).*")

STATIC_METHOD_NAME = "@staticmethod"
ABSTRACT_METHOD_NAME = "@abstractmethod"

# Other constants
PARENT_ABSTRACT_NAME = "ABC"
PARENT_ENUM_NAME = "Enum"
PARENT_EXCEPTION_NAME = "Exception"


class MethodType(Enum):
    """
    Enum class to represent the type of a method.
    """

    METHOD = 0
    STATIC = 1
    ABSTRACT = 2


def generate_models(file_contents: list[str]) -> list[ClassModel]:
    """
    Generate the models from the Python code.
    :param file_contents: The contents of the Python file.
    :return: The models.
    """

    classes_contents = split_classes(file_contents)

    return [generate_model(class_content) for class_content in classes_contents]


def generate_model(file_content: list[str]) -> ClassModel:
    """
    Generate a model from the Python code.
    :param file_content: The contents of the Python file.
    :return: The model.
    """

    class_name = get_class_name(file_content[0])
    class_attributes = get_class_attributes(file_content)
    methods = parsed_methods if (parsed_methods := get_methods(file_content)) else None
    class_type = get_class_type(file_content[0])

    static_methods = result if (result := get_static_methods(file_content)) else None
    abstract_methods = result if (result := get_abstract_methods(file_content)) else None

    return ClassModel(class_name, class_attributes, methods, class_type, static_methods, abstract_methods)


# Class-related functions
def split_classes(file_contents: list[str]) -> list[list[str]]:
    """
    Split the file contents into a list of classes.
    :param file_contents: The contents of the Python file.
    :return: The list of classes.
    """

    # Assume classes are defined at the top level
    indexes_to_split_at = [
        i for i, line in enumerate(file_contents) if not (line.startswith(" ") or line.startswith("\t"))
    ]

    if len(indexes_to_split_at) == 0:
        return []

    zero_indentated_content = [
        file_contents[indexes_to_split_at[i] : indexes_to_split_at[i + 1]] for i in range(len(indexes_to_split_at) - 1)
    ]
    zero_indentated_content += [file_contents[indexes_to_split_at[-1] :]]

    return [content for content in zero_indentated_content if class_pattern.match(content[0])]


def get_class_name(content: str) -> str:
    """
    Get the name of the class.
    :param content: The contents of the Python file.
    :return: The name of the class.
    """
    match class_name_pattern.match(content):
        case re.Match() as match_result:
            return match_result.group(1)
        case _:
            raise ValueError("No class name found")


def get_class_attributes(content: list[str]) -> list[Variable]:
    """
    Get the attributes of a class
    :param content: The contents of the Python file.
    :return: The attributes of the class.
    """

    raw_attributes = extract_item(content, attribute_pattern)

    return [parse_attribute(raw_attribute) for raw_attribute in raw_attributes]


def get_class_type(content: str) -> ClassType:
    """
    Get the type of the class.
    :param content: The contents of the Python file.
    :return: The type of the class.
    """
    content = content.strip()
    match class_parents_pattern.match(content):
        case re.Match() as match_result:
            class_type = match_result.group(1)
        case None:
            return ClassType.CLASS

    if PARENT_ABSTRACT_NAME in class_type:
        return ClassType.ABSTRACT
    if PARENT_ENUM_NAME in class_type:
        return ClassType.ENUM
    if PARENT_EXCEPTION_NAME in class_type:
        return ClassType.EXCEPTION

    return ClassType.CLASS


# Method-related functions
def get_methods(content: list[str]) -> list[Method]:
    """
    Get the methods of a class.
    :param content: The contents of the Python file.
    :return: The methods of the class.
    """

    raw_methods = extract_item(content, method_pattern)

    return [parse_method(raw_method) for raw_method in raw_methods]


def parse_method(raw_method: str) -> Method:
    """
    Parse a method from the raw string.
    :param raw_method: The raw string.
    :return: The method.
    """
    raw_method = raw_method.strip()
    match method_name_pattern.match(raw_method):
        case re.Match() as match_result:
            method_name = match_result.group(1)
        case None:
            method_name = ""

    method_visibility = parse_visibility(raw_method)

    method_arguments = arguments if (arguments := parse_arguments(raw_method)) else None
    method_return_type = return_type if (return_type := parse_return_type(raw_method)) else None

    return Method(method_name, method_visibility, method_arguments, method_return_type)


def parse_arguments(raw_method: str) -> list[Variable]:
    """
    Parse the arguments of a method from the raw string.
    :param raw_arguments: The raw string.
    :return: The arguments.
    """
    raw_method = raw_method.strip()
    arguments_pattern = re.compile(r".*\((.*)\).*")

    match arguments_pattern.match(raw_method):
        case re.Match() as match_result:
            raw_arguments: str = match_result.group(1)
        case None:
            return []

    if raw_arguments == "":
        return []

    arguments = raw_arguments.split(",")
    arguments = [argument.strip() for argument in arguments]

    parsed_arguments = [parse_argument(argument) for argument in arguments]

    return parsed_arguments


def parse_return_type(raw_method: str) -> str:
    """
    Parse the return type of a method from the raw string.
    :param raw_method: The raw string.
    :return: The return type.
    """
    raw_method = raw_method.strip()
    match method_return_type_pattern.match(raw_method):
        case re.Match() as match_result:
            return_type = match_result.group(1).strip()
        case None:
            return_type = ""

    return return_type


def get_static_methods(content: list[str]) -> list[Method]:
    """
    Get the static methods of a class.
    :param content: The contents of the Python file.
    :return: The static methods of the class.
    """
    raw_methods = [content[i + 1] for i, line in enumerate(content) if STATIC_METHOD_NAME in line]

    return [parse_method(raw_method) for raw_method in raw_methods]


def get_abstract_methods(content: list[str]) -> list[Method]:
    """
    Get the abstract methods of a class.
    :param content: The contents of the Python file.
    :return: The abstract methods of the class.
    """
    raw_methods = [content[i + 1] for i, line in enumerate(content) if ABSTRACT_METHOD_NAME in line]

    return [parse_method(raw_method) for raw_method in raw_methods]


# Utils
def parse_visibility(raw_attribute) -> Visibility:
    """
    Parse the visibility of an attribute.
    :param raw_attribute: The raw string.
    :return: The visibility of the attribute.
    """
    underscore_count = raw_attribute.count("_")

    if underscore_count == 0:
        visibility = Visibility.PUBLIC
    elif underscore_count == 1:
        visibility = Visibility.PROTECTED
    else:
        # Having multiple underscores is valid in python - assume private
        visibility = Visibility.PRIVATE
    return visibility


def extract_item(content: list[str], item_pattern: Pattern) -> list[str]:
    """
    Extract an item from the raw string.
    :param raw_item: The raw string.
    :return: The extracted item.
    """
    result = [
        match_result.group(0) for line in content if (match_result := item_pattern.match(line.strip())) is not None
    ]

    return result


def parse_attribute(raw_attribute: str) -> Variable:
    """
    Parse an attribute from the raw string.
    :param raw_attribute: The raw string.
    :return: The attribute.
    """

    raw_attribute = raw_attribute.strip()
    match attribute_name_pattern.match(raw_attribute):
        case re.Match() as match_result:
            attribute_name = match_result.group(2)
        case None:
            raise ValueError("No attribute name found")

    attribute_visibility = parse_visibility(raw_attribute)

    match argument_type_pattern.match(raw_attribute):
        case re.Match() as match_result:
            attribute_type = match_result.group(1)
        case None:
            attribute_type = ""

    return Variable(attribute_name, attribute_visibility, attribute_type)


def parse_argument(raw_argument: str) -> Variable:
    """
    Parse an argument fro the raw string
    :param raw_argument: The raw string.
    :return: The argument
    """
    match argument_pattern.match(raw_argument):
        case re.Match() as match_result:
            argument_name = match_result.group(1)
        case None:
            raise ValueError("No argument found")

    argument_visibility = parse_visibility(raw_argument)

    match argument_type_pattern.match(raw_argument):
        case re.Match() as match_result:
            attribute_type = match_result.group(1)
        case None:
            attribute_type = ""

    return Variable(argument_name, argument_visibility, attribute_type)
