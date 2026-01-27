"""
Module containing the converters which will be used to create the models from the Python code.
"""

import re

from enum import Enum
from re import Pattern

from src.models import ClassModel, ClassType, Method, Variable, Visibility
from src.string_utils import get_indentation_level

IDENTIFIER_PATTERN = r"[^\d\W]\w*"
TYPE_PATTERN = r"[^\d\W][\w\[\], ]*"

# Class-related patterns
class_type_pattern = re.compile(r"class (.*):")
class_name_pattern = re.compile(r"class *([a-zA-Z0-9_]*).*:")
class_parents_pattern = re.compile(r"class .*\((.*)\)")  # Looks unused

# Attribute-related patterns
attribute_pattern = re.compile(r"self\.(.*) *=.*")
attribute_name_pattern = re.compile(r"self\.(_){0,2}(.*) =")
attribute_type_pattern = re.compile(r"self\..* *: *(.*) =")

# Method-related patterns
method_pattern = re.compile(r"def .*\(self.*\).*:")
method_name_pattern = re.compile(rf"def +({IDENTIFIER_PATTERN}) *\(.*")
method_return_type_pattern = re.compile(rf"""def .*\(.*\) *-> *({TYPE_PATTERN}).*""")

# Argument-related patterns
arguments_pattern = re.compile(r".*\((.*)\).*")
argument_name_pattern = re.compile(rf"({IDENTIFIER_PATTERN}).*")
argument_type_pattern = re.compile(rf".*: *({TYPE_PATTERN})")

STATIC_METHOD_NAME = "@staticmethod"
ABSTRACT_METHOD_NAME = "@abstractmethod"

# TODO - What about classmethods ?


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
    The function expects only one class in the file content.
    :param file_content: The contents of the Python file.
    :return: The model.
    """

    class_name = get_class_name(file_content[0])
    class_attributes = get_class_attributes(file_content)
    methods = parsed_methods if (parsed_methods := get_methods(file_content)) else None
    class_type = get_class_type(file_content[0])

    static_methods = result if (result := get_static_methods(file_content)) else None
    abstract_methods = result if (result := get_abstract_methods(file_content)) else None

    # TODO - Abstract methods are present in both `methods` and `abstract_methods`

    return ClassModel(class_name, class_attributes, methods, class_type, static_methods, abstract_methods)


# Class-related functions
def split_classes(file_contents: list[str]) -> list[list[str]]:
    """
    Split the file contents into a list of classes.
    :param file_contents: The contents of the Python file.
    :return: The list of classes.
    """
    # TODO - Ugly code, maybe fix it at some point
    # TODO - Nested classes will break this
    result: list[list[str]] = []
    current_class: list[str] = []
    current_indent_level = 0
    is_class_active = False

    for line in file_contents:
        indent_level = get_indentation_level(line)
        match class_name_pattern.match(line):
            case re.Match():
                if len(current_class) != 0:
                    result.append(current_class)
                current_class = [line]
                current_indent_level = indent_level
                is_class_active = True
            case None:
                if indent_level > current_indent_level and is_class_active:
                    current_class.append(line)
                else:
                    if line.strip() == "":
                        continue
                    if len(current_class) != 0:
                        result.append(current_class)
                    current_class = []
                    current_indent_level = 0
                    is_class_active = False

    if len(current_class) != 0 and is_class_active:
        result.append(current_class)

    return result


def get_class_name(content: str) -> str:
    """
    Get the name of the class.

    `class TestClass:` -> `TestClass`
    :param content: Line from the python code containing the class definition.
    :return: The name of the class.
    """
    content = content.strip()
    return extract_item_from_single_line(content, class_name_pattern, target_capture_group=1)


def get_class_attributes(content: list[str]) -> list[Variable]:
    """
    Get the attributes of a class.
    The function expects only one class in the file content.
    :param content: Lines containing a Python class
    :return: The attributes of the class.
    """

    raw_attributes = extract_item_from_multiple_lines(content, attribute_pattern)

    return [parse_attribute(raw_attribute) for raw_attribute in raw_attributes]


def get_class_type(content: str) -> ClassType:
    """
    Get the type of the class.
    The function expects only the class definition line.
    :param content: The contents of the Python file.
    :return: The type of the class.
    """
    content = content.strip()

    try:
        class_type: str = extract_item_from_single_line(content, class_type_pattern, target_capture_group=1)
    except ValueError:
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
    The function expects only one class in the file content.
    :param content: A whole class.
    :return: The methods of the class.
    """

    raw_methods = extract_item_from_multiple_lines(content, method_pattern)

    return [parse_method(raw_method) for raw_method in raw_methods]


def parse_method(raw_method: str) -> Method:
    """
    Parse a method from the raw string.
    :param raw_method: The raw string.
    :return: The method.
    """
    raw_method = raw_method.strip()

    try:
        method_name = extract_item_from_single_line(raw_method, method_name_pattern, target_capture_group=1).strip()
    except ValueError:
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

    try:
        raw_arguments = extract_item_from_single_line(raw_method, arguments_pattern, target_capture_group=1)
    except ValueError:
        return []

    if raw_arguments == "":
        return []

    # TODO - This will cause bugs - what if the type hint has a ,
    arguments = [argument.strip() for argument in raw_arguments.split(",")]

    parsed_arguments = [parse_argument(argument) for argument in arguments]

    return parsed_arguments


def parse_return_type(raw_method: str) -> str:
    """
    Parse the return type of a method from the raw string.
    :param raw_method: The raw string.
    :return: The return type.
    """
    raw_method = raw_method.strip()
    try:
        return_type = extract_item_from_single_line(raw_method, method_return_type_pattern, target_capture_group=1)
    except ValueError:
        return_type = ""

    return return_type


def get_static_methods(content: list[str]) -> list[Method]:
    """
    Get the static methods of a class.
    The function expects only one class in the file content.
    :param content: The contents of the Python file.
    :return: The static methods of the class.
    """
    raw_methods = [content[i + 1] for i, line in enumerate(content) if STATIC_METHOD_NAME in line]

    return [parse_method(raw_method) for raw_method in raw_methods]


def get_abstract_methods(content: list[str]) -> list[Method]:
    """
    Get the abstract methods of a class.
    The function expects only one class in the file content.
    :param content: The contents of the Python file.
    :return: The abstract methods of the class.
    """
    raw_methods = [content[i + 1] for i, line in enumerate(content) if ABSTRACT_METHOD_NAME in line]

    return [parse_method(raw_method) for raw_method in raw_methods]


# Utils
def parse_visibility(raw_attribute: str) -> Visibility:
    """
    Parse the visibility of an attribute.

    `self.__foo = 1` -> `Visibility.PRIVATE`
    `self._foo = 1` -> `Visibility.PROTECTED`
    `self.foo = 1` -> `Visibility.PUBLIC`
    `a = "asd"` -> `Visibility.PUBLIC`

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


def extract_item_from_multiple_lines(content: list[str], item_pattern: Pattern) -> list[str]:
    """
    Extract an item from the raw string.
    :param raw_item: The raw string.
    :return: The extracted item.
    """
    result = [
        match_result.group(0) for line in content if (match_result := item_pattern.match(line.strip())) is not None
    ]

    return result


def extract_item_from_single_line(content: str, item_pattern: Pattern, target_capture_group: int = 0) -> str:
    """
    Extract an item from a single line.
    :param content: The raw string.
    :param item_pattern: The pattern to match the item.
    :param target_capture_group: The capture group to return (default is 0, which returns the whole match).
    :return: The extracted item.
    """
    match item_pattern.match(content):
        case re.Match() as match_result:
            return match_result.group(target_capture_group).strip()
        case None:
            raise ValueError("No item found")
        case _:
            raise SyntaxError("Unexpected return type from regex match")


def parse_attribute(line: str) -> Variable:
    """
    Parse an attribute from the raw string.

    `self._attribute_name = 1` -> `Variable("attribute_name", Visibility.PROTECTED, "int")`

    :param line: Line containing an attribute.
    :return: The attribute.
    """

    line = line.strip()
    try:
        attribute_name = extract_item_from_single_line(line, attribute_name_pattern, target_capture_group=2)
    except ValueError as exc:
        raise ValueError("No attribute name found") from exc

    attribute_visibility = parse_visibility(line)

    try:
        attribute_type = extract_item_from_single_line(line, attribute_type_pattern, target_capture_group=1)
    except ValueError:
        attribute_type = ""

    return Variable(attribute_name, attribute_visibility, attribute_type)


def parse_argument(raw_argument: str) -> Variable:
    """
    Parse an argument fro the raw string:

    a: int -> Variable("a", Visibility.PUBLIC, "int")
    :param raw_argument: The raw string.
    :return: The argument
    """

    try:
        argument_name = extract_item_from_single_line(raw_argument, argument_name_pattern, target_capture_group=1)
    except ValueError as error:
        raise ValueError("No argument name found") from error

    argument_visibility = parse_visibility(raw_argument)

    try:
        attribute_type = extract_item_from_single_line(raw_argument, argument_type_pattern, target_capture_group=1)
    except ValueError:
        attribute_type = ""

    return Variable(argument_name, argument_visibility, attribute_type)
