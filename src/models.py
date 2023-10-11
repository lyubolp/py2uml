"""
Module containing the models which will be used as a middle layer between the
    Python code and the UML diagrams.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ClassType(Enum):
    """
    Enum class to represent the type of a class.
    """
    CLASS = 0,
    ABSTRACT = 1,
    ENUM = 2,
    EXCEPTION = 3,


class Visibility(Enum):
    """
    Enum class to represent the visibility of a class.
    """
    PUBLIC = 0,
    PRIVATE = 1,
    PROTECTED = 2,


@dataclass
class Variable:
    """
    Data class to represent a variable
    """
    name: str
    visibility: Visibility
    variable_type: str


@dataclass
class Method:
    """
    Data class to represent a method of a class.
    """
    name: str
    visibility: Visibility
    arguments: Optional[list[Variable]]
    return_type: Optional[str]


class ClassModel:
    """
    Class to represent a class.
    """
    def __init__(self, name: str, attributes: Optional[list[Variable]],
                 methods: Optional[list[Method]], class_type: ClassType,
                 class_methods: Optional[list[Method]], static_methods: Optional[list[Method]],
                 class_variables: Optional[list[Variable]]):
        self.__name = name
        self.__attributes = attributes
        self.__methods = methods
        self.__class_type = class_type
        self.__class_methods = class_methods
        self.__static_methods = static_methods
        self.__class_variables = class_variables

    @property
    def name(self) -> str:
        """
        Getter for the name of the class.
        :return: The name of the class.
        """
        return self.__name

    @property
    def attributes(self) -> Optional[list[Variable]]:
        """
        Getter for the attributes of the class.
        :return: The attributes of the class.
        """
        return self.__attributes

    @property
    def methods(self) -> Optional[list[Method]]:
        """
        Getter for the methods of the class.
        :return: The methods of the class.
        """
        return self.__methods

    @property
    def class_type(self) -> ClassType:
        """
        Getter for the type of the class.
        :return: The type of the class.
        """
        return self.__class_type

    @property
    def class_methods(self) -> Optional[list[Method]]:
        """
        Getter for the class methods of the class.
        :return: The class methods of the class.
        """
        return self.__class_methods

    @property
    def static_methods(self) -> Optional[list[Method]]:
        """
        Getter for the static methods of the class.
        :return: The static methods of the class.
        """
        return self.__static_methods

    @property
    def class_variables(self) -> Optional[list[Variable]]:
        """
        Getter for the class variables of the class.
        :return: The class variables of the class.
        """
        return self.__class_variables
