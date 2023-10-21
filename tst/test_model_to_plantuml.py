"""
Module containing the tests for the model_to_plantuml module.
"""
import unittest

import src.converters.model_to_plantuml as m2p

from src.models import ClassModel, LinkType, Method, Variable, Visibility


class TestGeneratePlantUMLClassMethod(unittest.TestCase):
    """
    Test cases for the generate_plantuml_class_method function.

    Tests:
    - Different method visibilities
    - Available and missing return type
    - 0, 1 and 2 arguments
    """

    def test_01_private_visibility(self):
        """
        Verify that the method visibility is correctly converted to PlantUML.
        The method has private visibility, no arguments and no return type.
        """
        # Arrange
        method = Method('test_method', Visibility.PRIVATE, None, None)
        expected = '\t-test_method()'

        # Act
        actual = m2p.generate_plantuml_class_method(method)

        # Assert
        self.assertEqual(expected, actual)

    def test_02_protected_visibility(self):
        """
        Verify that the method visibility is correctly converted to PlantUML.
        The method has protected visibility, no arguments and no return type.
        """
        # Arrange
        method = Method('test_method', Visibility.PROTECTED, None, None)
        expected = '\t#test_method()'

        # Act
        actual = m2p.generate_plantuml_class_method(method)

        # Assert
        self.assertEqual(expected, actual)

    def test_03_public_visibility(self):
        """
        Verify that the method visibility is correctly converted to PlantUML.
        The method has public visibility, no arguments and no return type.
        """
        # Arrange
        method = Method('test_method', Visibility.PUBLIC, None, None)
        expected = '\t+test_method()'

        # Act
        actual = m2p.generate_plantuml_class_method(method)

        # Assert
        self.assertEqual(expected, actual)

    def test_04_return_type(self):
        """
        Verify that the return type is correctly converted to PlantUML.
        The method has public visibility, no arguments and a return type.
        """
        # Arrange
        method = Method('test_method', Visibility.PUBLIC, None, 'int')
        expected = '\t+test_method(): int'

        # Act
        actual = m2p.generate_plantuml_class_method(method)

        # Assert
        self.assertEqual(expected, actual)

    def test_05_one_argument(self):
        """
        Verify that the arguments are correctly converted to PlantUML.
        The method has public visibility, one argument and no return type.
        """
        # Arrange
        method = Method('test_method', Visibility.PUBLIC, [Variable('test_variable', Visibility.PUBLIC, 'int')], None)
        expected = '\t+test_method(int test_variable)'

        # Act
        actual = m2p.generate_plantuml_class_method(method)

        # Assert
        self.assertEqual(expected, actual)

    def test_06_two_arguments(self):
        """
        Verify that the arguments are correctly converted to PlantUML.
        The method has public visibility, two arguments and no return type.
        """
        # Arrange
        method = Method('test_method', Visibility.PUBLIC,
                        [Variable('test_variable_1', Visibility.PUBLIC, 'int'),
                         Variable('test_variable_2', Visibility.PUBLIC, 'int')], None)
        expected = '\t+test_method(int test_variable_1, int test_variable_2)'

        # Act
        actual = m2p.generate_plantuml_class_method(method)

        # Assert
        self.assertEqual(expected, actual)
