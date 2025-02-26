"""
Module containing the tests for the python_to_model module.
"""

import unittest

import src.converters.python_to_model as p2m

from src.models import Method, Variable, Visibility


class TestSplitClasses(unittest.TestCase):
    """
    Test cases for the split_classes function.
    """

    def test_01_single_class_no_additional_content(self):
        """
        Verify that split_classes returns a list containing a single element
            when the file contains a single class
        """
        # Arrange
        file_contents = ["class TestClass:", "    pass"]

        # Act
        result = p2m.split_classes(file_contents)

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], file_contents)

    def test_02_single_class_additional_content_before(self):
        """
        Verify that split_classes returns a list containing a single element
            when the file contains a single class with additional content before
        """
        # Arrange
        file_contents = ["import unittest", "", "class TestClass:", "    pass"]

        # Act
        result = p2m.split_classes(file_contents)

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], file_contents[2:])

    def test_03_single_class_additional_content_after(self):
        """
        Verify that split_classes returns a list containing a single element
            when the file contains a single class with additional content after
        """
        # Arrange
        file_contents = ["class TestClass:", "    pass", "", 'if __name__ == "__main__":', "    unittest.main()"]

        # Act
        result = p2m.split_classes(file_contents)

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], file_contents[:2])

    def test_04_single_class_additional_content_before_and_after(self):
        """
        Verify that split_classes returns a list containing a single element
            when the file contains a single class with additional content before and after
        """
        # Arrange
        file_contents = [
            "import unittest",
            "",
            "class TestClass:",
            "    pass",
            "",
            'if __name__ == "__main__":',
            "    unittest.main()",
        ]

        # Act
        result = p2m.split_classes(file_contents)

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], file_contents[2:4])

    def test_05_two_classes_no_additional_content(self):
        """
        Verify that split_classes returns a list containing two elements
            when the file contains two classes
        """
        # Arrange
        file_contents = ["class TestClass:", "    pass", "", "class TestClass2:", "    pass"]

        # Act
        result = p2m.split_classes(file_contents)

        # Assert
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], file_contents[:2])
        self.assertEqual(result[1], file_contents[3:])

    def test_06_two_classes_additional_content_middle(self):
        """
        Verify that split_classes returns a list containing two elements
            when the file contains two classes with additional content in the middle
        """
        # Arrange
        file_contents = ["class TestClass:", "    pass", "", "import unittest", "", "class TestClass2:", "    pass"]

        # Act
        result = p2m.split_classes(file_contents)

        # Assert
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], file_contents[:2])
        self.assertEqual(result[1], file_contents[5:])

    def test_07_no_classes(self):
        """
        Verify that split_classes returns an empty list when the file contains no classes
        """
        # Arrange
        file_contents = ["import unittest", "", "def test_01():", "    pass", "", "def test_02():", "    pass"]

        # Act
        result = p2m.split_classes(file_contents)

        # Assert
        self.assertEqual(len(result), 0)


class TestGetClassName(unittest.TestCase):
    """
    Test cases for the get_class_name function.
    """

    def test_01_has_class_name(self):
        """
        Verify that get_class_name returns the class name when the class name is in the first line
        """
        # Arrange
        class_content = "class TestClass:"

        # Act
        result = p2m.get_class_name(class_content)

        # Assert
        self.assertEqual(result, "TestClass")

    def test_02_has_class_name_with_inheritance(self):
        """
        Verify that get_class_name returns the class name when the class name is in the first line
            and the class inherits from another class
        """
        # Arrange
        class_content = "class TestClass(unittest.TestCase):"

        # Act
        result = p2m.get_class_name(class_content)

        # Assert
        self.assertEqual(result, "TestClass")

    def test_03_has_class_name_with_multiple_inheritance(self):
        """
        Verify that get_class_name returns the class name when the class name is in the first line
            and the class inherist from two classes
        """
        # Arrange
        class_content = "class TestClass(unittest.TestCase, ABC):"

        # Act
        result = p2m.get_class_name(class_content)

        # Assert
        self.assertEqual(result, "TestClass")

    def test_04_no_class_name(self):
        """
        Verify that get_class_name throws an exception where the input is invalid
        """
        # Arrange
        class_content = "Invalid class content"

        # Act & assert
        with self.assertRaises(ValueError):
            p2m.get_class_name(class_content)


class TestGetClassAttributes(unittest.TestCase):
    """
    Test cases for the get_class_attributes function
    """

    def test_01_zero_class_attirbutes(self):
        """
        Verify that get_class_attributes returns an empty list when there are no attributes
        """
        # Arrange
        content = ["class TestClass():", "\tdef __init__(self):", '\t\tprint("Hello world")']

        # Act
        result = p2m.get_class_attributes(content)

        # Assert
        self.assertEqual(result, [])

    def test_02_one_class_attribute(self):
        """
        Verify that get_class_attributes returns an empty list when there is one attribute
        """
        # Arrange
        variable_name = "x"

        content = ["class TestClass():", "\tdef __init__(self):", f"\t\tself.{variable_name} = 5"]
        expected_variable = Variable(variable_name, Visibility.PUBLIC, "")

        # Act
        result = p2m.get_class_attributes(content)

        # Assert
        self.assertEqual(result, [expected_variable])


class TestGetClassType(unittest.TestCase):
    """
    Test cases for the get_class_type function
    """

    def test_01_no_parent_class(self):
        # Arrange
        content = "class Foo:"
        expected_class_type = p2m.ClassType.CLASS

        # Act
        actual_class_type = p2m.get_class_type(content)

        # Assert
        self.assertEqual(actual_class_type, expected_class_type)

    def test_02_parent_normal_class(self):
        # Arrange
        content = "class Foo(Bar):"
        expected_class_type = p2m.ClassType.CLASS

        # Act
        actual_class_type = p2m.get_class_type(content)

        # Assert
        self.assertEqual(actual_class_type, expected_class_type)

    def test_03_parent_abstract(self):
        # Arrange
        content = "class Foo(ABC):"
        expected_class_type = p2m.ClassType.ABSTRACT

        # Act
        actual_class_type = p2m.get_class_type(content)

        # Assert
        self.assertEqual(actual_class_type, expected_class_type)

    def test_04_parent_enum(self):
        # Arrange
        content = "class Foo(Enum):"
        expected_class_type = p2m.ClassType.ENUM

        # Act
        actual_class_type = p2m.get_class_type(content)

        # Assert
        self.assertEqual(actual_class_type, expected_class_type)

    def test_05_parent_exception(self):
        # Arrange
        content = "class Foo(Exception):"
        expected_class_type = p2m.ClassType.EXCEPTION

        # Act
        actual_class_type = p2m.get_class_type(content)

        # Assert
        self.assertEqual(actual_class_type, expected_class_type)

    def test_06_no_parent_but_with_parenthesis(self):
        # Arrange
        content = "class Foo():"
        expected_class_type = p2m.ClassType.CLASS

        # Act
        actual_class_type = p2m.get_class_type(content)

        # Assert
        self.assertEqual(actual_class_type, expected_class_type)

    def test_07_parent_abstract_full_import(self):
        # Arrange
        content = "class Foo(abc.ABC):"
        expected_class_type = p2m.ClassType.ABSTRACT

        # Act
        actual_class_type = p2m.get_class_type(content)

        # Assert
        self.assertEqual(actual_class_type, expected_class_type)

    def test_08_parent_enum_full_import(self):
        # Arrange
        content = "class Foo(enum.Enum):"
        expected_class_type = p2m.ClassType.ENUM

        # Act
        actual_class_type = p2m.get_class_type(content)

        # Assert
        self.assertEqual(actual_class_type, expected_class_type)


class TestGetMethods(unittest.TestCase):
    """
    Test cases for the get_methods function
    """

    def test_01_zero_methods(self):
        # Arrange
        content: list[str] = ["class Foo:", "\tpass"]
        expected_methods_amount = 0

        # Act
        actual_methods_amount = len(p2m.get_methods(content))

        # Assert
        self.assertEqual(actual_methods_amount, expected_methods_amount)

    def test_02_one_method(self):
        # Arrange
        content = ["class Foo:", "\tdef bar(self):", '\t\tprint("Hello world")']
        expected_methods_amount = 1

        # Act
        actual_methods_amount = len(p2m.get_methods(content))

        # Assert
        self.assertEqual(actual_methods_amount, expected_methods_amount)

    def test_03_two_methods(self):
        # Arrange
        content = [
            "class Foo:",
            "\tdef bar(self):",
            '\t\tprint("Hello world")',
            "\tdef baz(self, a: int) -> float:",
            "\t\treturn 3.14 * a",
        ]
        expected_methods_amount = 2

        # Act
        actual_methods_amount = len(p2m.get_methods(content))

        # Assert
        self.assertEqual(actual_methods_amount, expected_methods_amount)


class TestParseMethod(unittest.TestCase):
    """
    Test cases for the parse_method function
    """

    def test_01_returns_a_method_object(self):
        # Arrange
        raw_method = "def foo(self)"

        # Act
        actual_method = p2m.parse_method(raw_method)

        # Assert
        self.assertTrue(isinstance(actual_method, Method))

    @unittest.skip("Is self an argument that should be handled ?")
    def test_02_method_without_argument(self):
        # Arrange
        raw_method = "def foo(self)"

        # Act
        actual_method = p2m.parse_method(raw_method)

        # Assert
        self.assertIsNone(actual_method.arguments)

    def test_03_method_with_argument(self):
        # Arrange
        raw_method = "def foo(self, a: int)"

        # Act
        actual_method = p2m.parse_method(raw_method)

        # Assert
        self.assertIsNotNone(actual_method.arguments)

    def test_04_method_without_return_type(self):
        # Arrange
        raw_method = "def foo(self)"

        # Act
        actual_method = p2m.parse_method(raw_method)

        # Assert
        self.assertIsNone(actual_method.return_type)

    def test_05_method_with_return_type(self):
        # Arrange
        raw_method = "def foo(self) -> int:"

        # Act
        actual_method = p2m.parse_method(raw_method)

        # Assert
        self.assertIsNotNone(actual_method.return_type)


class TestParseArguments(unittest.TestCase):
    """
    Test cases for the parse_arguments function
    4. Two arguments with type
    5. Two arguments without type
    6. One argument with return type
    7. One argument without return type
    """

    def test_01_parse_arguments_zero_arguments(self):
        # Arrange
        raw_method = "def foo()"

        # Act
        actual_arguments = p2m.parse_arguments(raw_method)

        # Assert
        self.assertEqual(actual_arguments, [])

    def test_02_parse_arguments_one_argument_with_type(self):
        # Arrange
        variable = Variable("a", Visibility.PUBLIC, "int")
        expected_arguments = [variable]
        raw_method = f"def foo({variable.name}: {variable.variable_type})"

        # Act
        actual_arguments = p2m.parse_arguments(raw_method)

        # Assert
        self.assertEqual(actual_arguments, expected_arguments)

    def test_03_parse_arguments_one_argument_without_type(self):
        # Arrange
        variable = Variable("a", Visibility.PUBLIC, "")
        expected_arguments = [variable]
        raw_method = f"def foo({variable.name})"

        # Act
        actual_arguments = p2m.parse_arguments(raw_method)

        # Assert
        self.assertEqual(actual_arguments, expected_arguments)

    def test_04_parse_arguments_two_arguments_with_type(self):
        # Arrange
        variable_a = Variable("a", Visibility.PUBLIC, "")
        variable_b = Variable("b", Visibility.PUBLIC, "int")
        expected_arguments = [variable_a, variable_b]
        raw_method = f"def foo({variable_a.name}, {variable_b.name}: {variable_b.variable_type})"

        # Act
        actual_arguments = p2m.parse_arguments(raw_method)

        # Assert
        self.assertEqual(actual_arguments, expected_arguments)


class TestParseReturnType(unittest.TestCase):
    """
    Test cases for the parse_return_type function
    """

    def test_01_return_type(self):
        # Arrange
        expected_return_type = "int"
        raw_method = f"def foo(self) -> {expected_return_type}:"

        # Act
        actual_return_type = p2m.parse_return_type(raw_method)

        # Assert
        self.assertEqual(actual_return_type, expected_return_type)

    def test_02_no_return_type(self):
        # Arrange
        raw_method = "def foo(self):"
        expected_return_type = ""

        # Act
        actual_return_type = p2m.parse_return_type(raw_method)

        # Assert
        self.assertEqual(actual_return_type, expected_return_type)


class TestGetStaticMethods(unittest.TestCase):
    """
    Test cases for the get_static_methods function
    """

    def test_01_zero_static_methods_zero_other_methods(self):
        # Arrange
        content = ["class Foo:", "\tpass"]
        expected_methods_count = 0

        # Act
        actual_methods = p2m.get_static_methods(content)

        # Assert
        self.assertEqual(len(actual_methods), expected_methods_count)

    def test_02_zero_static_methods_one_other_methods(self):
        # Arrange
        content = ["class Foo:", "\tdef foo(self):", "\t\tpass"]
        expected_methods_count = 0

        # Act
        actual_methods = p2m.get_static_methods(content)

        # Assert
        self.assertEqual(len(actual_methods), expected_methods_count)

    def test_03_zero_static_methods_two_other_methods(self):
        # Arrange
        content = ["class Foo:", "\tdef foo(self):", "\t\tpass", "\tdef bar(self):", "\t\tpass"]
        expected_methods_count = 0

        # Act
        actual_methods = p2m.get_static_methods(content)

        # Assert
        self.assertEqual(len(actual_methods), expected_methods_count)

    def test_04_one_static_method_zero_other_methods(self):
        # Arrange
        content = ["class Foo:", "\t@staticmethod", "\tdef foo():", "\t\tpass"]
        expected_methods_count = 1

        # Act
        actual_methods = p2m.get_static_methods(content)

        # Assert
        self.assertEqual(len(actual_methods), expected_methods_count)

    def test_05_one_static_method_one_other_method(self):
        # Arrange
        content = ["class Foo:", "\t@staticmethod", "\tdef foo():", "\t\tpass", "\tdef bar(self):", "\t\tpass"]
        expected_methods_count = 1

        # Act
        actual_methods = p2m.get_static_methods(content)

        # Assert
        self.assertEqual(len(actual_methods), expected_methods_count)

    def test_06_one_static_method_two_other_methods(self):
        # Arrange
        content = [
            "class Foo:",
            "\t@staticmethod",
            "\tdef foo():",
            "\t\tpass",
            "\tdef bar(self):",
            "\t\tpass",
            "\tdef baz(self):",
            "\t\tpass",
        ]
        expected_methods_count = 1

        # Act
        actual_methods = p2m.get_static_methods(content)

        # Assert
        self.assertEqual(len(actual_methods), expected_methods_count)

    def test_07_two_static_methods_zero_other_methods(self):
        # Arrange
        content = [
            "class Foo:",
            "\t@staticmethod",
            "\tdef foo():",
            "\t\tpass",
            "\t@staticmethod",
            "\tdef bar():",
            "\t\tpass",
        ]
        expected_methods_count = 2

        # Act
        actual_methods = p2m.get_static_methods(content)

        # Assert
        self.assertEqual(len(actual_methods), expected_methods_count)

    def test_08_two_static_methods_one_other_method(self):
        # Arrange
        content = [
            "class Foo:",
            "\t@staticmethod",
            "\tdef foo():",
            "\t\tpass",
            "\t@staticmethod",
            "\tdef bar():",
            "\t\tpass",
            "\tdef baz(self):",
            "\t\tpass",
        ]
        expected_methods_count = 2

        # Act
        actual_methods = p2m.get_static_methods(content)

        # Assert
        self.assertEqual(len(actual_methods), expected_methods_count)

    def test_09_two_static_methods_two_other_methods(self):
        # Arrange
        content = [
            "class Foo:",
            "\t@staticmethod",
            "\tdef foo():",
            "\t\tpass",
            "\t@staticmethod",
            "\tdef bar():",
            "\t\tpass",
            "\tdef baz(self):",
            "\t\tpass",
            "\tdef qux(self):",
            "\t\tpass",
        ]
        expected_methods_count = 2

        # Act
        actual_methods = p2m.get_static_methods(content)

        # Assert
        self.assertEqual(len(actual_methods), expected_methods_count)


class TestGetAbstractMethods(unittest.TestCase):
    """
    Test cases for the get_abstract_methods function
    """

    pass


class TestParseVisibilityMethods(unittest.TestCase):
    """
    Test cases for the parse_visibility function
    """

    pass


class TestExtractItemMethods(unittest.TestCase):
    """
    Test cases for the extract_item function
    """

    pass


class TestParseAttributeMethods(unittest.TestCase):
    """
    Test cases for the parse_attribute function
    """

    pass


class TestGenerateModelsMethods(unittest.TestCase):
    """
    Test cases for the generate_models function
    """

    pass


class TestGenerateModelMethods(unittest.TestCase):
    """
    Test cases for the generate_model function
    """

    pass
