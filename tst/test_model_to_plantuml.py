"""
Module containing the tests for the model_to_plantuml module.
"""
import unittest

import src.converters.model_to_plantuml as m2p

from src.models import ClassModel, ClassType, LinkType, Method, Variable, Visibility


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
        method = Method('test_method', Visibility.PUBLIC,
                        [Variable('test_variable', Visibility.PUBLIC, 'int')], None)
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


class TestGeneratePlantUMLClassMethods(unittest.TestCase):
    """
    Test cases for the generate_plantuml_class_methods function.

    Tests:
    - Available and missing methods
    - 0, 1 and 2 methods
    """

    def test_01_no_methods(self):
        """
        Verify that the PlantUML code for the methods is correctly generated.
        The class has no methods.
        """
        # Arrange
        class_model = ClassModel('test_class', None, None, None, None, None)
        expected = []

        # Act
        actual = m2p.generate_plantuml_class_methods(class_model)

        # Assert
        self.assertEqual(expected, actual)

    def test_02_one_method(self):
        """
        Verify that the PlantUML code for the methods is correctly generated.
        The class has one method.
        """
        # Arrange
        method = Method('test_method', Visibility.PUBLIC, None, None)
        class_model = ClassModel('test_class', None, [method], None, None, None)
        expected = ['\t+test_method()']

        # Act
        actual = m2p.generate_plantuml_class_methods(class_model)

        # Assert
        self.assertEqual(expected, actual)

    def test_03_two_methods(self):
        """
        Verify that the PlantUML code for the methods is correctly generated.
        The class has two methods.
        """
        # Arrange
        method_1 = Method('test_method_1', Visibility.PUBLIC, None, None)
        method_2 = Method('test_method_2', Visibility.PUBLIC, None, None)
        class_model = ClassModel('test_class', None, [method_1, method_2], None, None, None)
        expected = ['\t+test_method_1()', '\t+test_method_2()']

        # Act
        actual = m2p.generate_plantuml_class_methods(class_model)

        # Assert
        self.assertEqual(expected, actual)


class TestGeneratePlantUMLClassAttribute(unittest.TestCase):
    """
    Test cases for the generate_plantuml_class_attribute function.

    Tests:
    - Different attribute visibilities
    """
    def test_01_private_visibility(self):
        """
        Verify that the attribute visibility is correctly converted to PlantUML.
        The attribute has private visibility.
        """
        # Arrange
        attribute = Variable('test_attribute', Visibility.PRIVATE, 'int')
        expected = '\t-int test_attribute'

        # Act
        actual = m2p.generate_plantuml_class_attribute(attribute)

        # Assert
        self.assertEqual(expected, actual)

    def test_02_protected_visibility(self):
        """
        Verify that the attribute visibility is correctly converted to PlantUML.
        The attribute has protected visibility.
        """
        # Arrange
        attribute = Variable('test_attribute', Visibility.PROTECTED, 'int')
        expected = '\t#int test_attribute'

        # Act
        actual = m2p.generate_plantuml_class_attribute(attribute)

        # Assert
        self.assertEqual(expected, actual)

    def test_03_public_visibility(self):
        """
        Verify that the attribute visibility is correctly converted to PlantUML.
        The attribute has public visibility.
        """
        # Arrange
        attribute = Variable('test_attribute', Visibility.PUBLIC, 'int')
        expected = '\t+int test_attribute'

        # Act
        actual = m2p.generate_plantuml_class_attribute(attribute)

        # Assert
        self.assertEqual(expected, actual)


class TestGeneratePlantUMLClassAttributes(unittest.TestCase):
    """
    Test cases for the generate_plantuml_class_attributes function.

    Tests:
    - Available and missing attributes
    - 0, 1 and 2 attributes
    """

    def test_01_no_attributes(self):
        """
        Verify that the PlantUML code for the attributes is correctly generated.
        The class has no attributes.
        """
        # Arrange
        class_model = ClassModel('test_class', None, None, None, None, None)
        expected = []

        # Act
        actual = m2p.generate_plantuml_class_attributes(class_model)

        # Assert
        self.assertEqual(expected, actual)

    def test_02_one_attribute(self):
        """
        Verify that the PlantUML code for the attributes is correctly generated.
        The class has one attribute.
        """
        # Arrange
        attribute = Variable('test_attribute', Visibility.PUBLIC, 'int')
        class_model = ClassModel('test_class', [attribute], None, None, None, None)
        expected = ['\t+int test_attribute']

        # Act
        actual = m2p.generate_plantuml_class_attributes(class_model)

        # Assert
        self.assertEqual(expected, actual)

    def test_03_two_attributes(self):
        """
        Verify that the PlantUML code for the attributes is correctly generated.
        The class has two attributes.
        """
        # Arrange
        attribute_1 = Variable('test_attribute_1', Visibility.PUBLIC, 'int')
        attribute_2 = Variable('test_attribute_2', Visibility.PUBLIC, 'int')
        class_model = ClassModel('test_class', [attribute_1, attribute_2], None, None, None, None)
        expected = ['\t+int test_attribute_1', '\t+int test_attribute_2']

        # Act
        actual = m2p.generate_plantuml_class_attributes(class_model)

        # Assert
        self.assertEqual(expected, actual)


class TestGeneratePlantUMLLink(unittest.TestCase):
    """
    Test case for the generate_plantuml_link function.

    Tests:
    - Different link types
    """
    def test_001_extension(self):
        """
        Verify that the PlantUML code for the link is correctly generated.
        The link is an extension.
        """
        # Arrange
        class_model_1 = ClassModel('test_class_1', None, None, None, None, None)
        class_model_2 = ClassModel('test_class_2', None, None, None, None, None)
        link = (LinkType.EXTENSION, class_model_2)
        expected = 'test_class_1 <|-- test_class_2'

        # Act
        actual = m2p.generate_plantuml_link(class_model_1, link)

        # Assert
        self.assertEqual(expected, actual)

    def test_002_composition(self):
        """
        Verify that the PlantUML code for the link is correctly generated.
        The link is a composition.
        """
        # Arrange
        class_model_1 = ClassModel('test_class_1', None, None, None, None, None)
        class_model_2 = ClassModel('test_class_2', None, None, None, None, None)
        link = (LinkType.COMPOSITION, class_model_2)
        expected = 'test_class_1 *-- test_class_2'

        # Act
        actual = m2p.generate_plantuml_link(class_model_1, link)

        # Assert
        self.assertEqual(expected, actual)

    def test_003_aggregation(self):
        """
        Verify that the PlantUML code for the link is correctly generated.
        The link is a composition.
        """
        # Arrange
        class_model_1 = ClassModel('test_class_1', None, None, None, None, None)
        class_model_2 = ClassModel('test_class_2', None, None, None, None, None)
        link = (LinkType.AGGREGATION, class_model_2)
        expected = 'test_class_1 o-- test_class_2'

        # Act
        actual = m2p.generate_plantuml_link(class_model_1, link)

        # Assert
        self.assertEqual(expected, actual)

    def test_004_normal(self):
        """
        Verify that the PlantUML code for the link is correctly generated.
        The link is a composition.
        """
        # Arrange
        class_model_1 = ClassModel('test_class_1', None, None, None, None, None)
        class_model_2 = ClassModel('test_class_2', None, None, None, None, None)
        link = (LinkType.NORMAL, class_model_2)
        expected = 'test_class_1 -- test_class_2'

        # Act
        actual = m2p.generate_plantuml_link(class_model_1, link)

        # Assert
        self.assertEqual(expected, actual)


class TestGeneratePlantUMLClass(unittest.TestCase):
    """
    Test cases for the generate_plantuml_class function.

    Tests:
    - Available and missing attributes
    - Available and missing methods
    - Available and missing static methods
    - Available and missing abstract methods
    - Abstract class
    - Normal class
    - Enum
    - Exception
    """
    def test_01_no_attributes_no_methods_no_static_methods_no_abstract_methods(self):
        """
        Verify that the PlantUML code for the class is correctly generated.
        The class has no attributes.
        """
        # Arrange
        class_model = ClassModel('test_class', attributes=None, methods=None,
                                 class_type=ClassType.CLASS, static_methods=None,
                                 abstract_methods=None)
        expected = ['class test_class {', '}']

        # Act
        actual = m2p.generate_plantuml_class(class_model)

        # Assert
        self.assertEqual(expected, actual)

    def test_02_attributes(self):
        """
        Verify that the PlantUML code for the class is correctly generated.
        The class has attributes.
        """
        # Arrange
        attribute_1 = Variable('test_attribute_1', Visibility.PUBLIC, 'int')
        attribute_2 = Variable('test_attribute_2', Visibility.PUBLIC, 'str')

        class_model = ClassModel('test_class', attributes=[attribute_1, attribute_2], methods=None,
                                 class_type=ClassType.CLASS, static_methods=None,
                                 abstract_methods=None)
        expected = ['class test_class {',
                    '\t+int test_attribute_1',
                    '\t+str test_attribute_2',
                    '}']

        # Act
        actual = m2p.generate_plantuml_class(class_model)

        # Assert
        self.assertEqual(expected, actual)

    def test_03_methods(self):
        """
        Verify that the PlantUML code for the class is correctly generated.
        The class has methods.
        """
        # Arrange
        method_1 = Method('test_method_1', Visibility.PUBLIC, None, None)
        method_2 = Method('test_method_2', Visibility.PUBLIC, None, None)

        class_model = ClassModel('test_class', attributes=None, methods=[method_1, method_2],
                                 class_type=ClassType.CLASS, static_methods=None,
                                 abstract_methods=None)
        expected = ['class test_class {',
                    '\t+test_method_1()',
                    '\t+test_method_2()',
                    '}']

        # Act
        actual = m2p.generate_plantuml_class(class_model)

        # Assert
        self.assertEqual(expected, actual)

    def test_04_static_methods(self):
        """
        Verify that the PlantUML code for the class is correctly generated.
        The class has static methods.
        """
        # Arrange
        method_1 = Method('test_method_1', Visibility.PUBLIC, None, None)
        method_2 = Method('test_method_2', Visibility.PUBLIC, None, None)

        class_model = ClassModel('test_class', attributes=None, methods=None,
                                 class_type=ClassType.CLASS, static_methods=[method_1, method_2],
                                 abstract_methods=None)
        expected = ['class test_class {',
                    '\t{static} +test_method_1()',
                    '\t{static} +test_method_2()',
                    '}']

        # Act
        actual = m2p.generate_plantuml_class(class_model)

        # Assert
        self.assertEqual(expected, actual)

    def test_05_abstract_methods(self):
        """
        Verify that the PlantUML code for the class is correctly generated.
        The class has abstract methods.
        """
        # Arrange
        method_1 = Method('test_method_1', Visibility.PUBLIC, None, None)
        method_2 = Method('test_method_2', Visibility.PUBLIC, None, None)

        class_model = ClassModel('test_class', attributes=None, methods=None,
                                 class_type=ClassType.CLASS, static_methods=None,
                                 abstract_methods=[method_1, method_2])
        expected = ['abstract class test_class {',
                    '\t{abstract} +test_method_1()',
                    '\t{abstract} +test_method_2()',
                    '}']

        # Act
        actual = m2p.generate_plantuml_class(class_model)

        # Assert
        self.assertEqual(expected, actual)

    def test_06_abstract_class(self):
        """
        Verify that the PlantUML code for the class is correctly generated.
        The class is an abstract class.
        """
        # Arrange
        class_model = ClassModel('test_class', attributes=None, methods=None,
                                 class_type=ClassType.ABSTRACT, static_methods=None,
                                 abstract_methods=None)
        expected = ['abstract test_class {', '}']

        # Act
        actual = m2p.generate_plantuml_class(class_model)

        # Assert
        self.assertEqual(expected, actual)

    def test_07_enum(self):
        """
        Verify that the PlantUML code for the class is correctly generated.
        The class is an enum.
        """
        # Arrange
        class_model = ClassModel('test_class', attributes=None, methods=None,
                                 class_type=ClassType.ENUM, static_methods=None,
                                 abstract_methods=None)
        expected = ['enum test_class {', '}']

        # Act
        actual = m2p.generate_plantuml_class(class_model)

        # Assert
        self.assertEqual(expected, actual)

    def test_08_exception(self):
        """
        Verify that the PlantUML code for the class is correctly generated.
        The class is an exception.
        """
        # Arrange
        class_model = ClassModel('test_class', attributes=None, methods=None,
                                 class_type=ClassType.EXCEPTION, static_methods=None,
                                 abstract_methods=None)
        expected = ['exception test_class {', '}']

        # Act
        actual = m2p.generate_plantuml_class(class_model)

        # Assert
        self.assertEqual(expected, actual)


class TestGeneratePlantUMLStaticMethod(unittest.TestCase):
    pass