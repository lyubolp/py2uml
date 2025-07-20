"""
Module containing the tests for the python_to_model module.
"""

import re
import unittest
import unittest.mock
from unittest.mock import MagicMock, patch, call

import src.converters.python_to_model as p2m

from src.models import Method, Variable, Visibility, ClassType


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

    def test_08_class_with_content(self):
        """
        Verify that split_classes returns a list containing a single element
            when the file contains a class with content
        """
        # Arrange
        file_contents = [
            "class TestClass:",
            "    def __init__(self):",
            "        self.attribute = 5",
            "",
            "    def method(self):",
            "        return self.attribute",
        ]
        expected_file_contents = [
            "class TestClass:",
            "    def __init__(self):",
            "        self.attribute = 5",
            "    def method(self):",
            "        return self.attribute",
        ]

        # Act
        result = p2m.split_classes(file_contents)

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], expected_file_contents)


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

    @patch("src.converters.python_to_model.extract_item_from_multiple_lines")
    def test_01_extract_item_called(self, mocked_extract_item: MagicMock):
        """
        Verify that the extract_item function is called
        """
        # Arrange
        content = ["class Foo:", "\tdef bar(self):", "\t\tpass"]

        # Act
        p2m.get_class_attributes(content)

        # Assert
        mocked_extract_item.assert_called_once_with(content, p2m.attribute_pattern)

    @patch("src.converters.python_to_model.parse_attribute")
    @patch("src.converters.python_to_model.extract_item_from_multiple_lines")
    def test_02_parse_attribute_called_once_when_one_attribute_is_found(
        self, mocked_extract_item: MagicMock, mocked_parse_attribute: MagicMock
    ):
        """
        Verify that the parse_attribute() is called once when only one item is returned by extract_item()
        """
        # Arrange
        sample_attribute = "self.x = 5"
        content = ["class Foo:", f"\t{sample_attribute}", "\t\tpass"]
        mocked_extract_item.return_value = [sample_attribute]

        # Act
        p2m.get_class_attributes(content)

        # Assert
        mocked_parse_attribute.assert_called_once_with(sample_attribute)

    @patch("src.converters.python_to_model.parse_attribute")
    @patch("src.converters.python_to_model.extract_item_from_multiple_lines")
    def test_03_parse_attribute_called_multiple_times_when_multiple_attributes_found(
        self, mocked_extract_item: MagicMock, mocked_parse_attribute: MagicMock
    ):
        """
        Verify that the parse_attribute() is called multiple times when multiple items are returned by extract_item()
        """
        # Arrange
        sample_attributes = ["self.x = 5", "self.y = 10"]
        content = ["class Foo:", f"\t{sample_attributes[0]}", "\t\tpass", f"\t{sample_attributes[1]}", "\t\tpass"]
        mocked_extract_item.return_value = sample_attributes

        expected_calls = [call(sample_attribute) for sample_attribute in sample_attributes]
        # Act
        p2m.get_class_attributes(content)

        # Assert
        self.assertEqual(mocked_parse_attribute.call_count, len(sample_attributes))
        self.assertEqual(mocked_parse_attribute.call_args_list, expected_calls)

    @patch("src.converters.python_to_model.parse_attribute")
    @patch("src.converters.python_to_model.extract_item_from_multiple_lines")
    def test_04_parse_attribute_called_once_when_no_attributes_found(
        self, mocked_extract_item: MagicMock, mocked_parse_attribute: MagicMock
    ):
        """
        Verify that the parse_attribute() is called once when no items are returned by extract_item()
        """
        # Arrange
        content = ["class Foo:", "\tpass"]
        mocked_extract_item.return_value = []

        # Act
        p2m.get_class_attributes(content)

        # Assert
        mocked_parse_attribute.assert_not_called()


class TestGetClassType(unittest.TestCase):
    """
    Test cases for the get_class_type function
    """

    def test_01_no_parent_class(self):
        """
        Verify that get_class_type returns CLASS when there is no parent class
        """
        # Arrange
        content = "class Foo:"
        expected_class_type = p2m.ClassType.CLASS
        # Act
        actual_class_type = p2m.get_class_type(content)
        # Assert
        self.assertEqual(actual_class_type, expected_class_type)

    def test_02_parent_normal_class(self):
        """
        Verify that get_class_type returns CLASS when the parent class is a normal class
        """
        # Arrange
        content = "class Foo(Bar):"
        expected_class_type = p2m.ClassType.CLASS
        # Act
        actual_class_type = p2m.get_class_type(content)
        # Assert
        self.assertEqual(actual_class_type, expected_class_type)

    def test_03_parent_abstract(self):
        """
        Verify that get_class_type returns ABSTRACT when the parent class is ABC
        """
        # Arrange
        content = "class Foo(ABC):"
        expected_class_type = p2m.ClassType.ABSTRACT
        # Act
        actual_class_type = p2m.get_class_type(content)
        # Assert
        self.assertEqual(actual_class_type, expected_class_type)

    def test_04_parent_enum(self):
        """
        Verify that get_class_type returns ENUM when the parent class is Enum
        """
        # Arrange
        content = "class Foo(Enum):"
        expected_class_type = p2m.ClassType.ENUM
        # Act
        actual_class_type = p2m.get_class_type(content)
        # Assert
        self.assertEqual(actual_class_type, expected_class_type)

    def test_05_parent_exception(self):
        """
        Verify that get_class_type returns EXCEPTION when the parent class is Exception
        """
        # Arrange
        content = "class Foo(Exception):"
        expected_class_type = p2m.ClassType.EXCEPTION
        # Act
        actual_class_type = p2m.get_class_type(content)
        # Assert
        self.assertEqual(actual_class_type, expected_class_type)

    def test_06_no_parent_but_with_parenthesis(self):
        """
        Verify that get_class_type returns CLASS when there is no parent class but with parenthesis
        """
        # Arrange
        content = "class Foo():"
        expected_class_type = p2m.ClassType.CLASS
        # Act
        actual_class_type = p2m.get_class_type(content)
        # Assert
        self.assertEqual(actual_class_type, expected_class_type)

    def test_07_parent_abstract_full_import(self):
        """
        Verify that get_class_type returns ABSTRACT when the parent class is abc.ABC
        """
        # Arrange
        content = "class Foo(abc.ABC):"
        expected_class_type = p2m.ClassType.ABSTRACT
        # Act
        actual_class_type = p2m.get_class_type(content)
        # Assert
        self.assertEqual(actual_class_type, expected_class_type)

    def test_08_parent_enum_full_import(self):
        """
        Verify that get_class_type returns ENUM when the parent class is enum.Enum
        """
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

    @patch("src.converters.python_to_model.extract_item_from_multiple_lines")
    def test_01_extract_item_called(self, mocked_extract_item: MagicMock):
        """
        Verify that the extract_item function is called
        """
        # Arrange
        content = ["class Foo:", "\tdef bar(self):", "\t\tpass"]

        # Act
        p2m.get_methods(content)

        # Assert
        mocked_extract_item.assert_called_once_with(content, p2m.method_pattern)

    @patch("src.converters.python_to_model.parse_method")
    @patch("src.converters.python_to_model.extract_item_from_multiple_lines")
    def test_02_parse_method_called_once_when_one_method_is_found(
        self, mocked_extract_item: MagicMock, mocked_parse_method: MagicMock
    ):
        """
        Verify that the parse_method() is called once when only one item is returned by extract_item()
        """
        # Arrange
        sample_method = "def bar(self):"
        content = ["class Foo:", f"\t{sample_method}", "\t\tpass"]
        mocked_extract_item.return_value = [sample_method]

        # Act
        p2m.get_methods(content)

        # Assert
        mocked_parse_method.assert_called_once_with(sample_method)

    @patch("src.converters.python_to_model.parse_method")
    @patch("src.converters.python_to_model.extract_item_from_multiple_lines")
    def test_03_parse_method_called_multiple_times_when_multiple_methods_found(
        self, mocked_extract_item: MagicMock, mocked_parse_method: MagicMock
    ):
        """
        Verify that the parse_method() is called multiple times when multiple items are returned by extract_item()
        """
        # Arrange
        sample_methods = ["def bar(self):", "def baz(self):"]
        content = ["class Foo:", f"\t{sample_methods[0]}", "\t\tpass", f"\t{sample_methods[1]}", "\t\tpass"]
        mocked_extract_item.return_value = sample_methods

        expected_calls = [call(sample_method) for sample_method in sample_methods]
        # Act
        p2m.get_methods(content)

        # Assert
        self.assertEqual(mocked_parse_method.call_count, len(sample_methods))
        self.assertEqual(mocked_parse_method.call_args_list, expected_calls)

    @patch("src.converters.python_to_model.parse_method")
    @patch("src.converters.python_to_model.extract_item_from_multiple_lines")
    def test_04_parse_method_called_once_when_no_methods_found(
        self, mocked_extract_item: MagicMock, mocked_parse_method: MagicMock
    ):
        """
        Verify that the parse_method() is called once when no items are returned by extract_item()
        """
        # Arrange
        content = ["class Foo:", "\tpass"]
        mocked_extract_item.return_value = []

        # Act
        p2m.get_methods(content)

        # Assert
        mocked_parse_method.assert_not_called()


class TestParseMethod(unittest.TestCase):
    """
    Test cases for the parse_method function
    """

    # def __init__(self):
    #     super().__init__()

    #     self.__sample_method_name = "foo"
    #     self.__sample_method_arguments = "self, a: int"
    #     self.__sample_method_return_type = "int"
    #     self.__sample_method = (
    #         f"def {self.__sample_method_name}({self.__sample_method_arguments}) -> {self.__sample_method_return_type}:"
    #     )

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        self.__sample_method_name = "foo"
        self.__sample_method_arguments = "self, a: int"
        self.__sample_method_return_type = "int"
        self.__sample_method = (
            f"def {self.__sample_method_name}({self.__sample_method_arguments}) -> {self.__sample_method_return_type}:"
        )

    def test_01_returns_a_method_object(self):
        # Act
        actual_method = p2m.parse_method(self.__sample_method)

        # Assert
        self.assertTrue(isinstance(actual_method, Method))

    @patch("src.converters.python_to_model.extract_item_from_single_line")
    def test_02_extract_item_called(self, mocked_extract_item: MagicMock):
        """
        Verify that the extract_item_from_single_line function is called
        """
        # Arrange
        expected_call = call(self.__sample_method, p2m.method_name_pattern, target_capture_group=1)
        mocked_extract_item.return_value = self.__sample_method_name

        # Act
        model = p2m.parse_method(self.__sample_method)

        # Assert
        self.assertEqual(mocked_extract_item.call_args_list[0], expected_call)
        self.assertEqual(model.name, self.__sample_method_name)

    @patch("src.converters.python_to_model.extract_item_from_single_line")
    def test_03_extract_item_raises_exception(self, mocked_extract_item: MagicMock):
        """
        Verify that the parse_method function returns an empty string as a method name
        when the extract_item_from_single_line function raises an exception
        """
        # Arrange
        mocked_extract_item.side_effect = ValueError("Method name not found")

        # Act
        model = p2m.parse_method(self.__sample_method)

        # Assert
        self.assertEqual(model.name, "")

    @patch("src.converters.python_to_model.parse_visibility")
    def test_04_parse_visibility_called(self, mocked_parse_visibility: MagicMock):
        """
        Verify that the parse_visibility function is called
        """
        # Arrange
        expected_call = call(self.__sample_method)
        mocked_parse_visibility.return_value = Visibility.PUBLIC

        # Act
        model = p2m.parse_method(self.__sample_method)

        # Assert
        self.assertEqual(mocked_parse_visibility.call_args_list[0], expected_call)
        self.assertEqual(model.visibility, Visibility.PUBLIC)

    @patch("src.converters.python_to_model.parse_arguments")
    def test_05_parse_arguments_called(self, mocked_parse_arguments: MagicMock):
        """
        Verify that the parse_arguments function is called
        """
        # Arrange
        expected_call = call(self.__sample_method)
        mocked_parse_arguments.return_value = [Variable("a", Visibility.PUBLIC, "int")]

        # Act
        model = p2m.parse_method(self.__sample_method)

        # Assert
        self.assertEqual(mocked_parse_arguments.call_args_list[0], expected_call)
        self.assertIsNotNone(model.arguments)
        self.assertEqual(len(model.arguments), 1)
        self.assertEqual(model.arguments[0].name, "a")
        self.assertEqual(model.arguments[0].variable_type, "int")

    @patch("src.converters.python_to_model.parse_arguments")
    def test_06_parse_arguments_returns_none(self, mocked_parse_arguments: MagicMock):
        """
        Verify that the arguments are None when the parse_arguments returns a [].
        """
        # Arrange
        mocked_parse_arguments.return_value = []

        # Act
        model = p2m.parse_method(self.__sample_method)

        # Assert
        self.assertIsNone(model.arguments)

    @patch("src.converters.python_to_model.parse_return_type")
    def test_07_parse_return_type_called(self, mocked_parse_return_type: MagicMock):
        """
        Verify that the parse_return_type function is called
        """
        # Arrange
        expected_call = call(self.__sample_method)
        mocked_parse_return_type.return_value = "int"

        # Act
        model = p2m.parse_method(self.__sample_method)

        # Assert
        self.assertEqual(mocked_parse_return_type.call_args_list[0], expected_call)
        self.assertEqual(model.return_type, "int")

    @patch("src.converters.python_to_model.parse_return_type")
    def test_08_parse_return_type_returns_none(self, mocked_parse_return_type: MagicMock):
        """
        Verify that the return_type is None when the parse_return_type returns an empty string.
        """
        # Arrange
        mocked_parse_return_type.return_value = ""

        # Act
        model = p2m.parse_method(self.__sample_method)

        # Assert
        self.assertIsNone(model.return_type)


class TestParseArguments(unittest.TestCase):
    """
    Test cases for the parse_arguments function

    """

    @patch("src.converters.python_to_model.extract_item_from_single_line")
    def test_01_extract_item_called(self, mocked_extract_item: MagicMock):
        """
        Verify that the extract_item_from_single_line function is called
        """
        # Arrange
        raw_method = "def foo(self, a: int, b: str)"
        expected_call = call(raw_method, p2m.arguments_pattern, target_capture_group=1)
        mocked_extract_item.return_value = "a: int, b: str"

        # Act
        p2m.parse_arguments(raw_method)

        # Assert
        self.assertEqual(mocked_extract_item.call_args_list[0], expected_call)

    @patch("src.converters.python_to_model.extract_item_from_single_line")
    def test_02_arguments_are_empty_when_extract_item_raises_exception(self, mocked_extract_item: MagicMock):
        """
        Verify that when extract_item_from_single_line raises an exception,
        the parse_arguments function returns an empty list.
        """
        # Arrange
        raw_method = "def foo(self, a: int, b: str)"
        mocked_extract_item.side_effect = ValueError("No arguments found")

        # Act
        model = p2m.parse_arguments(raw_method)

        # Assert
        self.assertEqual(model, [])

    @patch("src.converters.python_to_model.extract_item_from_single_line")
    def test_03_arguments_are_empty_when_extract_item_returns_empty(self, mocked_extract_item: MagicMock):
        """
        Verify that when no arguments are found, the parse_arguments function returns an empty list.
        """
        # Arrange
        raw_method = "def foo(self)"
        mocked_extract_item.return_value = ""

        # Act
        model = p2m.parse_arguments(raw_method)

        # Assert
        self.assertEqual(model, [])

    @patch("src.converters.python_to_model.extract_item_from_single_line")
    @patch("src.converters.python_to_model.parse_argument")
    def test_04_results_from_extract_are_split_and_parse_argument_called(
        self, mocked_parse_argument: MagicMock, mocked_extract_item: MagicMock
    ):
        """
        Verify that parse_arguments returns an empty list when there are no arguments
        """
        # Arrange
        raw_arguments = "a: int, b: str"
        expected_calls = [call("a: int"), call("b: str")]
        raw_method = f"def foo({raw_arguments})"

        mocked_extract_item.return_value = raw_arguments

        # Act
        p2m.parse_arguments(raw_method)

        # Assert
        self.assertEqual(mocked_parse_argument.call_args_list, expected_calls)


class TestParseReturnType(unittest.TestCase):
    """
    Test cases for the parse_return_type function
    """

    @patch("src.converters.python_to_model.extract_item_from_single_line")
    def test_01_extract_item_called(self, mocked_extract_item: MagicMock):
        """
        Verify that the extract_item_from_single_line function is called
        """
        # Arrange
        expected_return_type = "int"
        raw_method = f"def foo(self) -> {expected_return_type}:"
        expected_call = call(raw_method, p2m.method_return_type_pattern, target_capture_group=1)
        mocked_extract_item.return_value = expected_return_type

        # Act
        model = p2m.parse_return_type(raw_method)

        # Assert
        self.assertEqual(mocked_extract_item.call_args_list[0], expected_call)
        self.assertEqual(model, expected_return_type)

    @patch("src.converters.python_to_model.extract_item_from_single_line")
    def test_02_return_type_empty_when_extract_item_raises_exception(self, mocked_extract_item: MagicMock):
        """
        Verify that when extract_item_from_single_line raises an exception,
        the parse_return_type function returns an empty string.
        """
        # Arrange
        raw_method = "def foo(self) -> int:"
        mocked_extract_item.side_effect = ValueError("Return type not found")

        # Act
        model = p2m.parse_return_type(raw_method)

        # Assert
        self.assertEqual(model, "")


class TestGetStaticMethods(unittest.TestCase):
    """
    Test cases for the get_static_methods function
    """

    @patch("src.converters.python_to_model.parse_method")
    def test_01_zero_static_methods_zero_other_methods(self, mocked_parse_method: MagicMock):
        # Arrange
        content = ["class Foo:", "\tpass"]
        expected_methods_count = 0

        # Act
        actual_methods = p2m.get_static_methods(content)

        # Assert
        mocked_parse_method.assert_not_called()
        self.assertEqual(len(actual_methods), expected_methods_count)

    @patch("src.converters.python_to_model.parse_method")
    def test_02_zero_static_methods_one_other_methods(self, mocked_parse_method: MagicMock):
        # Arrange
        content = ["class Foo:", "\tdef foo(self):", "\t\tpass"]
        expected_methods_count = 0

        # Act
        actual_methods = p2m.get_static_methods(content)

        # Assert
        self.assertEqual(len(actual_methods), expected_methods_count)
        mocked_parse_method.assert_not_called()

    @patch("src.converters.python_to_model.parse_method")
    def test_03_zero_static_methods_two_other_methods(self, mocked_parse_method: MagicMock):
        # Arrange
        content = ["class Foo:", "\tdef foo(self):", "\t\tpass", "\tdef bar(self):", "\t\tpass"]
        expected_methods_count = 0

        # Act
        actual_methods = p2m.get_static_methods(content)

        # Assert
        mocked_parse_method.assert_not_called()
        self.assertEqual(len(actual_methods), expected_methods_count)

    @patch("src.converters.python_to_model.parse_method")
    def test_04_one_static_method_zero_other_methods(self, mocked_parse_method: MagicMock):
        # Arrange
        static_method = "\tdef foo():"
        content = ["class Foo:", "\t@staticmethod", static_method, "\t\tpass"]
        expected_methods_count = 1

        # Act
        actual_methods = p2m.get_static_methods(content)

        # Assert
        mocked_parse_method.assert_called_once_with(static_method)
        self.assertEqual(len(actual_methods), expected_methods_count)

    @patch("src.converters.python_to_model.parse_method")
    def test_05_one_static_method_one_other_method(self, mocked_parse_method: MagicMock):
        # Arrange
        static_method = "\tdef foo():"
        content = ["class Foo:", "\t@staticmethod", static_method, "\t\tpass", "\tdef bar(self):", "\t\tpass"]
        expected_methods_count = 1

        # Act
        actual_methods = p2m.get_static_methods(content)

        # Assert
        mocked_parse_method.assert_called_once_with(static_method)
        self.assertEqual(len(actual_methods), expected_methods_count)

    @patch("src.converters.python_to_model.parse_method")
    def test_06_one_static_method_two_other_methods(self, mocked_parse_method: MagicMock):
        # Arrange
        static_method = "\tdef foo():"
        content = [
            "class Foo:",
            "\t@staticmethod",
            static_method,
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
        mocked_parse_method.assert_called_once_with(static_method)
        self.assertEqual(len(actual_methods), expected_methods_count)

    @patch("src.converters.python_to_model.parse_method")
    def test_07_two_static_methods_zero_other_methods(self, mocked_parse_method: MagicMock):
        # Arrange
        static_method_1 = "\tdef foo():"
        static_method_2 = "\tdef bar():"
        content = [
            "class Foo:",
            "\t@staticmethod",
            static_method_1,
            "\t\tpass",
            "\t@staticmethod",
            static_method_2,
            "\t\tpass",
        ]
        expected_methods_count = 2

        # Act
        actual_methods = p2m.get_static_methods(content)

        # Assert
        mocked_parse_method.assert_has_calls([call(static_method_1), call(static_method_2)])
        self.assertEqual(len(actual_methods), expected_methods_count)

    @patch("src.converters.python_to_model.parse_method")
    def test_08_two_static_methods_one_other_method(self, mocked_parse_method: MagicMock):
        # Arrange
        static_method_1 = "\tdef foo():"
        static_method_2 = "\tdef bar():"
        content = [
            "class Foo:",
            "\t@staticmethod",
            static_method_1,
            "\t\tpass",
            "\t@staticmethod",
            static_method_2,
            "\t\tpass",
            "\tdef baz(self):",
            "\t\tpass",
        ]
        expected_methods_count = 2

        # Act
        actual_methods = p2m.get_static_methods(content)

        # Assert
        mocked_parse_method.assert_has_calls([call(static_method_1), call(static_method_2)])
        self.assertEqual(len(actual_methods), expected_methods_count)

    @patch("src.converters.python_to_model.parse_method")
    def test_09_two_static_methods_two_other_methods(self, mocked_parse_method: MagicMock):
        # Arrange
        static_method_1 = "\tdef foo():"
        static_method_2 = "\tdef bar():"
        content = [
            "class Foo:",
            "\t@staticmethod",
            static_method_1,
            "\t\tpass",
            "\t@staticmethod",
            static_method_2,
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
        mocked_parse_method.assert_has_calls([call(static_method_1), call(static_method_2)])
        self.assertEqual(len(actual_methods), expected_methods_count)


class TestGetAbstractMethods(unittest.TestCase):
    """
    Test cases for the get_abstract_methods function
    """

    @patch("src.converters.python_to_model.parse_method")
    def test_01_zero_abstract_methods_zero_other_methods(self, mocked_parse_method: MagicMock):
        # Arrange
        content = ["class Foo:", "\tpass"]
        expected_methods_count = 0

        # Act
        actual_methods = p2m.get_abstract_methods(content)

        # Assert
        mocked_parse_method.assert_not_called()
        self.assertEqual(len(actual_methods), expected_methods_count)

    @patch("src.converters.python_to_model.parse_method")
    def test_02_zero_abstract_methods_one_other_methods(self, mocked_parse_method: MagicMock):
        # Arrange
        content = ["class Foo:", "\tdef foo(self):", "\t\tpass"]
        expected_methods_count = 0

        # Act
        actual_methods = p2m.get_abstract_methods(content)

        # Assert
        mocked_parse_method.assert_not_called()
        self.assertEqual(len(actual_methods), expected_methods_count)

    @patch("src.converters.python_to_model.parse_method")
    def test_03_zero_abstract_methods_two_other_methods(self, mocked_parse_method: MagicMock):
        # Arrange
        content = ["class Foo:", "\tdef foo(self):", "\t\tpass", "\tdef bar(self):", "\t\tpass"]
        expected_methods_count = 0

        # Act
        actual_methods = p2m.get_abstract_methods(content)

        # Assert
        mocked_parse_method.assert_not_called()
        self.assertEqual(len(actual_methods), expected_methods_count)

    @patch("src.converters.python_to_model.parse_method")
    def test_04_one_abstract_method_zero_other_methods(self, mocked_parse_method: MagicMock):
        # Arrange
        static_method = "\tdef foo():"
        content = ["class Foo:", "\t@abstractmethod", static_method, "\t\tpass"]
        expected_methods_count = 1

        # Act
        actual_methods = p2m.get_abstract_methods(content)

        # Assert
        mocked_parse_method.assert_called_once_with(static_method)
        self.assertEqual(len(actual_methods), expected_methods_count)

    @patch("src.converters.python_to_model.parse_method")
    def test_05_one_abstract_method_one_other_method(self, mocked_parse_method: MagicMock):
        # Arrange
        static_method = "\tdef foo():"
        content = ["class Foo:", "\t@abstractmethod", static_method, "\t\tpass", "\tdef bar(self):", "\t\tpass"]
        expected_methods_count = 1

        # Act
        actual_methods = p2m.get_abstract_methods(content)

        # Assert
        mocked_parse_method.assert_called_once_with(static_method)
        self.assertEqual(len(actual_methods), expected_methods_count)

    @patch("src.converters.python_to_model.parse_method")
    def test_06_one_abstract_method_two_other_methods(self, mocked_parse_method: MagicMock):
        # Arrange
        static_method = "\tdef foo():"
        content = [
            "class Foo:",
            "\t@abstractmethod",
            static_method,
            "\t\tpass",
            "\tdef bar(self):",
            "\t\tpass",
            "\tdef baz(self):",
            "\t\tpass",
        ]
        expected_methods_count = 1

        # Act
        actual_methods = p2m.get_abstract_methods(content)

        # Assert
        mocked_parse_method.assert_called_once_with(static_method)
        self.assertEqual(len(actual_methods), expected_methods_count)

    @patch("src.converters.python_to_model.parse_method")
    def test_07_two_abstract_methods_zero_other_methods(self, mocked_parse_method: MagicMock):
        # Arrange
        static_method_1 = "\tdef foo():"
        static_method_2 = "\tdef bar():"
        content = [
            "class Foo:",
            "\t@abstractmethod",
            static_method_1,
            "\t\tpass",
            "\t@abstractmethod",
            static_method_2,
            "\t\tpass",
        ]
        expected_methods_count = 2

        # Act
        actual_methods = p2m.get_abstract_methods(content)

        # Assert
        mocked_parse_method.assert_has_calls([call(static_method_1), call(static_method_2)])
        self.assertEqual(len(actual_methods), expected_methods_count)

    @patch("src.converters.python_to_model.parse_method")
    def test_08_two_abstract_methods_one_other_method(self, mocked_parse_method: MagicMock):
        # Arrange
        static_method_1 = "\tdef foo():"
        static_method_2 = "\tdef bar():"
        content = [
            "class Foo:",
            "\t@abstractmethod",
            static_method_1,
            "\t\tpass",
            "\t@abstractmethod",
            static_method_2,
            "\t\tpass",
            "\tdef baz(self):",
            "\t\tpass",
        ]
        expected_methods_count = 2

        # Act
        actual_methods = p2m.get_abstract_methods(content)

        # Assert
        mocked_parse_method.assert_has_calls([call(static_method_1), call(static_method_2)])
        self.assertEqual(len(actual_methods), expected_methods_count)

    @patch("src.converters.python_to_model.parse_method")
    def test_09_two_abstract_methods_two_other_methods(self, mocked_parse_method: MagicMock):
        # Arrange
        static_method_1 = "\tdef foo():"
        static_method_2 = "\tdef bar():"
        content = [
            "class Foo:",
            "\t@abstractmethod",
            static_method_1,
            "\t\tpass",
            "\t@abstractmethod",
            static_method_2,
            "\t\tpass",
            "\tdef baz(self):",
            "\t\tpass",
            "\tdef qux(self):",
            "\t\tpass",
        ]
        expected_methods_count = 2

        # Act
        actual_methods = p2m.get_abstract_methods(content)

        # Assert
        mocked_parse_method.assert_has_calls([call(static_method_1), call(static_method_2)])
        self.assertEqual(len(actual_methods), expected_methods_count)


class TestParseVisibility(unittest.TestCase):
    """
    Test cases for the parse_visibility function
    """

    def test_01_public_visibility(self):
        """
        Verify that parse_visibility returns PUBLIC when the visibility is public
        """
        # Arrange
        content = "self.attribute = value"

        # Act
        result = p2m.parse_visibility(content)

        # Assert
        self.assertEqual(result, Visibility.PUBLIC)

    def test_02_protected_visibility(self):
        """
        Verify that parse_visibility returns PROTECTED when the visibility is protected
        """
        # Arrange
        content = "self._attribute = value"

        # Act
        result = p2m.parse_visibility(content)

        # Assert
        self.assertEqual(result, Visibility.PROTECTED)

    def test_03_private_visibility(self):
        """
        Verify that parse_visibility returns PRIVATE when the visibility is private
        """
        # Arrange
        content = "self.__attribute = value"

        # Act
        result = p2m.parse_visibility(content)

        # Assert
        self.assertEqual(result, Visibility.PRIVATE)

    def test_04_normal_variable(self):
        """
        Verify that parse_visibility returns PUBLIC when the variable is a normal variable
        """
        # Arrange
        content = "attribute = value"

        # Act
        result = p2m.parse_visibility(content)

        # Assert
        self.assertEqual(result, Visibility.PUBLIC)


class TestExtractItemFromMultipleLines(unittest.TestCase):
    """
    Test cases for the extract_item function
    """

    pass


class TestExtractItemFromMultipleLinesMethodPattern(unittest.TestCase):
    def test_01_one_method(self):
        # Arrange
        expected_methods = ["def foo(self):"]
        raw_content = ["class Foo:", f"\t{expected_methods[0]}", "\t\tpass"]

        # Act
        actual_methods = p2m.extract_item_from_multiple_lines(raw_content, p2m.method_pattern)

        # Assert
        self.assertEqual(actual_methods, expected_methods)

    def test_02_static_methods_ignored(self):
        # Arrange
        expected_methods = ["def foo(self):"]
        raw_content = [
            "class Foo:",
            f"\t{expected_methods[0]}",
            "\t\tpass",
            "\t@staticmethod",
            "\tdef bar(foo):",
            "\t\tpass",
        ]

        # Act
        actual_methods = p2m.extract_item_from_multiple_lines(raw_content, p2m.method_pattern)

        # Assert
        self.assertEqual(actual_methods, expected_methods)

    def test_03_abstract_methods_ignored(self):
        # Arrange
        expected_methods = ["def foo(self):"]
        raw_content = [
            "class Foo:",
            f"\t{expected_methods[0]}",
            "\t\tpass",
            "\t@abstractmethod",
            "\tdef bar(foo):",
            "\t\tpass",
        ]

        # Act
        actual_methods = p2m.extract_item_from_multiple_lines(raw_content, p2m.method_pattern)

        # Assert
        self.assertEqual(actual_methods, expected_methods)

    def test_04_init_method(self):
        # Arrange
        expected_methods = ["def __init__(self):"]
        raw_content = ["class Foo:", f"\t{expected_methods[0]}", "\t\tprint('Hello')", "\t\tprint('World')"]

        # Act
        actual_methods = p2m.extract_item_from_multiple_lines(raw_content, p2m.method_pattern)

        # Assert
        self.assertEqual(actual_methods, expected_methods)

    def test_05_dunder_method(self):
        # Arrange
        expected_methods = ["def __str__(self):"]
        raw_content = ["class Foo:", f"\t{expected_methods[0]}", "\t\tprint('Hello')", "\t\tprint('World')"]

        # Act
        actual_methods = p2m.extract_item_from_multiple_lines(raw_content, p2m.method_pattern)

        # Assert
        self.assertEqual(actual_methods, expected_methods)

    def test_06_class_method(self):
        # Arrange
        expected_methods = []
        raw_content = [
            "class Foo:",
            "\t@classmethod",
            "\tdef foo(cls):",
            "\t\tprint('Hello')",
            "\t\tprint('World')",
        ]

        # Act
        actual_methods = p2m.extract_item_from_multiple_lines(raw_content, p2m.method_pattern)

        # Assert
        self.assertEqual(actual_methods, expected_methods)

    def test_07_two_methods(self):
        # Arrange
        expected_methods = ["def foo(self):", "def bar(self):"]
        raw_content = [
            "class Foo:",
            f"\t{expected_methods[0]}",
            "\t\tprint('Hello')",
            "\t\tprint('World')",
            "\n",
            "\n",
            f"\t{expected_methods[1]}",
            "\t\tprint('Hello')",
            "\t\tprint('World')",
        ]

        # Act
        actual_methods = p2m.extract_item_from_multiple_lines(raw_content, p2m.method_pattern)

        # Assert
        self.assertEqual(actual_methods, expected_methods)

    def test_08_three_methods(self):
        # Arrange
        expected_methods = ["def foo(self):", "def bar(self):", "def baz(self):"]
        raw_content = [
            "class Foo:",
            f"\t{expected_methods[0]}",
            "\t\tprint('Hello')",
            "\t\tprint('World')",
            "\n",
            "\n",
            f"\t{expected_methods[1]}",
            "\t\tprint('Hello')",
            "\t\tprint('World')",
            "\n",
            f"\t{expected_methods[2]}",
            "\t\tprint('Hello')",
            "\t\tprint('World')",
        ]

        # Act
        actual_methods = p2m.extract_item_from_multiple_lines(raw_content, p2m.method_pattern)

        # Assert
        self.assertEqual(actual_methods, expected_methods)

    def test_09_two_methods_static_in_between(self):
        # Arrange
        expected_methods = ["def foo(self):", "def baz(self):"]
        raw_content = [
            "class Foo:",
            f"\t{expected_methods[0]}",
            "\t\tprint('Hello')",
            "\t\tprint('World')",
            "\n",
            "\n",
            "\t@staticmethod" "\tdef bar():",
            "\t\tprint('Hello')",
            "\t\tprint('World')",
            "\n",
            f"\t{expected_methods[1]}",
            "\t\tprint('Hello')",
            "\t\tprint('World')",
        ]

        # Act
        actual_methods = p2m.extract_item_from_multiple_lines(raw_content, p2m.method_pattern)

        # Assert
        self.assertEqual(actual_methods, expected_methods)

    def test_10_method_with_arguments_and_type_hint(self):
        # Arrange
        expected_methods = ["def foo(self, first: int) -> dict[str, int]:"]
        raw_content = ["class Foo:", f"\t{expected_methods[0]}", "\t\tpass"]

        # Act
        actual_methods = p2m.extract_item_from_multiple_lines(raw_content, p2m.method_pattern)

        # Assert
        self.assertEqual(actual_methods, expected_methods)


class TestExtractItemFromMultipleLinesAttributePattern(unittest.TestCase):
    def test_01_zero_class_attributes(self):
        """
        Verify that get_class_attributes returns an empty list when there are no attributes
        """
        # Arrange
        content = ["class TestClass():", "\tdef __init__(self):", '\t\tprint("Hello world")']

        # Act
        result = p2m.extract_item_from_multiple_lines(content, p2m.attribute_pattern)

        # Assert
        self.assertEqual(result, [])

    def test_02_one_class_attribute(self):
        """
        Verify that get_class_attributes returns an empty list when there is one attribute
        """
        # Arrange
        expected_attributes = ["self.first = 5"]

        content = ["class TestClass():", "\tdef __init__(self):", f"\t\t{expected_attributes[0]}"]

        # Act
        actual_attributes = p2m.extract_item_from_multiple_lines(content, p2m.attribute_pattern)

        # Assert
        self.assertEqual(actual_attributes, expected_attributes)

    def test_03_two_class_attributes(self):
        """
        Verify that get_class_attributes returns a list with two attributes when there are two attributes
        """
        # Arrange
        expected_attributes = ["self.first = 5", "self.second_attribute = 10"]

        content = [
            "class TestClass():",
            "\tdef __init__(self):",
            f"\t\t{expected_attributes[0]}",
            f"\t\t{expected_attributes[1]}",
        ]
        # Act
        actual_attributes = p2m.extract_item_from_multiple_lines(content, p2m.attribute_pattern)

        # Assert
        self.assertEqual(actual_attributes, expected_attributes)

    def test_04_one_private_class_attribute(self):
        """
        Verify that get_class_attributes returns an empty list when there is one attribute
        """
        # Arrange
        expected_attributes = ["self.__first = 5"]

        content = ["class TestClass():", "\tdef __init__(self):", f"\t\t{expected_attributes[0]}"]

        # Act
        actual_attributes = p2m.extract_item_from_multiple_lines(content, p2m.attribute_pattern)

        # Assert
        self.assertEqual(actual_attributes, expected_attributes)

    def test_05_one_class_attribute_with_type_hint(self):
        """
        Verify that get_class_attributes returns an empty list when there is one attribute
        """
        # Arrange
        expected_attributes = ["self.first: int = 5"]

        content = ["class TestClass():", "\tdef __init__(self):", f"\t\t{expected_attributes[0]}"]

        # Act
        actual_attributes = p2m.extract_item_from_multiple_lines(content, p2m.attribute_pattern)

        # Assert
        self.assertEqual(actual_attributes, expected_attributes)

    def test_06_two_class_attributes_with_complex_type_hint(self):
        # Arrange
        expected_attributes = ["self.first = 5", "self.second_attribute: tuple[int, str] = (10, 'hello')"]

        content = [
            "class TestClass():",
            "\tdef __init__(self):",
            f"\t\t{expected_attributes[0]}",
            f"\t\t{expected_attributes[1]}",
        ]
        # Act
        actual_attributes = p2m.extract_item_from_multiple_lines(content, p2m.attribute_pattern)

        # Assert
        self.assertEqual(actual_attributes, expected_attributes)

    def test_07_two_class_attributes_with_code_between(self):
        # Arrange
        expected_attributes = ["self.first = 5", "self.second_attribute: tuple[int, str] = (10, 'hello')"]

        content = [
            "class TestClass():",
            "\tdef __init__(self):",
            f"\t\t{expected_attributes[0]}",
            "\t\tprint('Hello world')",
            f"\t\t{expected_attributes[1]}",
        ]
        # Act
        actual_attributes = p2m.extract_item_from_multiple_lines(content, p2m.attribute_pattern)

        # Assert
        self.assertEqual(actual_attributes, expected_attributes)


class TestExtractItemFromSingleLineGeneralFunctionality(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.__sample_words = ["hello", "world"]
        self.__sample_content = " ".join(self.__sample_words)
        self.__sample_regex = re.compile(r"([a-z]*) ([a-z]*)")

    def test_01_match_present(self):
        # Arrange
        expected_item = self.__sample_content

        # Act
        actual_item = p2m.extract_item_from_single_line(self.__sample_content, self.__sample_regex)

        # Assert
        self.assertEqual(actual_item, expected_item)

    def test_02_target_group_returned(self):
        # Arrange
        target_group = 1
        expected_item = self.__sample_words[target_group - 1]

        # Act
        actual_item = p2m.extract_item_from_single_line(self.__sample_content, self.__sample_regex, target_group)

        # Assert
        self.assertEqual(actual_item, expected_item)

    def test_03_match_returns_none(self):
        # Arrange
        regex = re.compile("qwerty")

        # Act & Assert
        with self.assertRaises(ValueError):
            p2m.extract_item_from_single_line(self.__sample_content, regex)


class TestExtractItemFromSingleLineClassName(unittest.TestCase):
    def test_01_no_inheritance(self):
        # Arrange
        expected_class_name = "Foo"
        content = f"class {expected_class_name}:"

        # Act
        actual_class_name = p2m.extract_item_from_single_line(content, p2m.class_name_pattern, 1)

        # Assert
        self.assertEqual(actual_class_name, expected_class_name)

    def test_02_single_inheritance(self):
        # Arrange
        expected_class_name = "Foo"
        content = f"class {expected_class_name}(Base):"

        # Act
        actual_class_name = p2m.extract_item_from_single_line(content, p2m.class_name_pattern, 1)

        # Assert
        self.assertEqual(actual_class_name, expected_class_name)

    def test_03_multiple_inheritance(self):
        # Arrange
        expected_class_name = "Foo"
        content = f"class {expected_class_name}(Base1, Base2):"

        # Act
        actual_class_name = p2m.extract_item_from_single_line(content, p2m.class_name_pattern, 1)

        # Assert
        self.assertEqual(actual_class_name, expected_class_name)

    def test_04_white_space(self):
        # Arrange
        expected_class_name = "Foo"
        content = f"class   {expected_class_name}  (Base)   :       "

        # Act
        actual_class_name = p2m.extract_item_from_single_line(content, p2m.class_name_pattern, 1)

        # Assert
        self.assertEqual(actual_class_name, expected_class_name)

    def test_05_complex_name(self):
        # Arrange
        expected_class_name = "FooBarBaz123_qwerty"
        content = f"class {expected_class_name}(Base):"

        # Act
        actual_class_name = p2m.extract_item_from_single_line(content, p2m.class_name_pattern, 1)

        # Assert
        self.assertEqual(actual_class_name, expected_class_name)


class TestExtractItemFromSingleLineClassTypePattern(unittest.TestCase):
    def test_01_no_inheritance(self):
        # Arrange
        expected_class_content = "Foo"
        content = f"class {expected_class_content}:"

        # Act
        actual_class_content = p2m.extract_item_from_single_line(
            content, p2m.class_type_pattern, target_capture_group=1
        )

        # Assert
        self.assertEqual(actual_class_content, expected_class_content)

    def test_02_single_inheritance(self):
        # Arrange
        expected_class_content = "Foo(Bar)"
        content = f"class {expected_class_content}:"

        # Act
        actual_class_content = p2m.extract_item_from_single_line(
            content, p2m.class_type_pattern, target_capture_group=1
        )

        # Assert
        self.assertEqual(actual_class_content, expected_class_content)

    def test_03_multiple_inheritance(self):
        # Arrange
        expected_class_content = "Foo(Bar, Enum)"
        content = f"class {expected_class_content}:"

        # Act
        actual_class_content = p2m.extract_item_from_single_line(
            content, p2m.class_type_pattern, target_capture_group=1
        )

        # Assert
        self.assertEqual(actual_class_content, expected_class_content)


class TestExtractItemFromSingleLineMethodNamePattern(unittest.TestCase):
    def test_01_simple_name(self):
        # Arrange
        expected_method_name = "foo"
        content = f"def {expected_method_name}(self):"

        # Act
        actual_method_name = p2m.extract_item_from_single_line(
            content, p2m.method_name_pattern, target_capture_group=1
        )

        # Assert
        self.assertEqual(actual_method_name, expected_method_name)

    def test_02_complex_name(self):
        # Arrange
        expected_method_name = "foo_bar_baz_123A"
        content = f"def {expected_method_name}(self):"

        # Act
        actual_method_name = p2m.extract_item_from_single_line(
            content, p2m.method_name_pattern, target_capture_group=1
        )

        # Assert
        self.assertEqual(actual_method_name, expected_method_name)

    def test_03_multiple_arguments_and_return_type(self):
        # Arrange
        expected_method_name = "foo_bar_baz"
        content = f"def {expected_method_name}(self, a: int, b) -> str:"

        # Act
        actual_method_name = p2m.extract_item_from_single_line(
            content, p2m.method_name_pattern, target_capture_group=1
        )

        # Assert
        self.assertEqual(actual_method_name, expected_method_name)

    def test_04_white_space(self):
        # Arrange
        expected_method_name = "foo_bar_baz"
        content = f"def     {expected_method_name}  (self, a: int, b) -> str:"

        # Act
        actual_method_name = p2m.extract_item_from_single_line(
            content, p2m.method_name_pattern, target_capture_group=1
        )

        # Assert
        self.assertEqual(actual_method_name, expected_method_name)


class TestExtractItemFromSingleLineMethodReturnTypePattern(unittest.TestCase):
    def test_01_return_type(self):
        # Arrange
        expected_return_type = "int"
        raw_method = f"def foo(self) -> {expected_return_type}:"

        # Act
        actual_return_type = p2m.extract_item_from_single_line(
            raw_method, p2m.method_return_type_pattern, target_capture_group=1
        )

        # Assert
        self.assertEqual(actual_return_type, expected_return_type)

    def test_02_no_return_type(self):
        # Arrange
        raw_method = "def foo(self):"

        # Act & Assert
        with self.assertRaises(ValueError):
            p2m.extract_item_from_single_line(raw_method, p2m.method_return_type_pattern, target_capture_group=1)

    def test_03_complex_type_old_syntax(self):
        # Arrange
        expected_return_type = "List[int]"
        raw_method = f"def foo(self) -> {expected_return_type}:"

        # Act
        actual_return_type = p2m.extract_item_from_single_line(
            raw_method, p2m.method_return_type_pattern, target_capture_group=1
        )

        # Assert
        self.assertEqual(actual_return_type, expected_return_type)

    def test_04_complex_type_new_syntax(self):
        # Arrange
        expected_return_type = "list[int]"
        raw_method = f"def foo(self) -> {expected_return_type}:"

        # Act
        actual_return_type = p2m.extract_item_from_single_line(
            raw_method, p2m.method_return_type_pattern, target_capture_group=1
        )

        # Assert
        self.assertEqual(actual_return_type, expected_return_type)

    def test_05_no_whitespace(self):
        # Arrange
        expected_return_type = "int"
        raw_method = f"def foo(self)->{expected_return_type}:"

        # Act
        actual_return_type = p2m.extract_item_from_single_line(
            raw_method, p2m.method_return_type_pattern, target_capture_group=1
        )

        # Assert
        self.assertEqual(actual_return_type, expected_return_type)

    def test_06_whitespace(self):
        # Arrange
        expected_return_type = "int"
        raw_method = f"def foo(self) ->  {expected_return_type} :"

        # Act
        actual_return_type = p2m.extract_item_from_single_line(
            raw_method, p2m.method_return_type_pattern, target_capture_group=1
        )

        # Assert
        self.assertEqual(actual_return_type, expected_return_type)

    def test_07_nested_complex_syntax(self):
        # Arrange
        expected_return_type = "dict[str, list[int]]"
        raw_method = f"def foo(self) -> {expected_return_type}:"

        # Act
        actual_return_type = p2m.extract_item_from_single_line(
            raw_method, p2m.method_return_type_pattern, target_capture_group=1
        )

        # Assert
        self.assertEqual(actual_return_type, expected_return_type)


class TestExtractItemFromSingleLineArgumentsPattern(unittest.TestCase):
    def test_01_zero_arguments(self):
        # Arrange
        expected_arguments = ""
        raw_method = f"def foo({expected_arguments})"

        # Act
        actual_arguments = p2m.extract_item_from_single_line(raw_method, p2m.arguments_pattern, target_capture_group=1)

        # Assert
        self.assertEqual(actual_arguments, expected_arguments)

    def test_02_one_argument_with_type(self):
        # Arrange
        expected_arguments = "first: int"
        raw_method = f"def foo({expected_arguments})"

        # Act
        actual_arguments = p2m.extract_item_from_single_line(raw_method, p2m.arguments_pattern, target_capture_group=1)

        # Assert
        self.assertEqual(actual_arguments, expected_arguments)

    def test_03_one_argument_without_type(self):
        # Arrange
        expected_arguments = "first"
        raw_method = f"def foo({expected_arguments})"

        # Act
        actual_arguments = p2m.extract_item_from_single_line(raw_method, p2m.arguments_pattern, target_capture_group=1)

        # Assert
        self.assertEqual(actual_arguments, expected_arguments)

    def test_04_two_arguments_with_type(self):
        # Arrange
        expected_arguments = "first: int, second: str"
        raw_method = f"def foo({expected_arguments})"

        # Act
        actual_arguments = p2m.extract_item_from_single_line(raw_method, p2m.arguments_pattern, target_capture_group=1)

        # Assert
        self.assertEqual(actual_arguments, expected_arguments)

    def test_05_two_arguments_without_type(self):
        # Arrange
        expected_arguments = "first, second"
        raw_method = f"def foo({expected_arguments})"

        # Act
        actual_arguments = p2m.extract_item_from_single_line(raw_method, p2m.arguments_pattern, target_capture_group=1)

        # Assert
        self.assertEqual(actual_arguments, expected_arguments)

    def test_06_two_arguments_one_with_type_one_without(self):
        # Arrange
        expected_arguments = "first, second: int"
        raw_method = f"def foo({expected_arguments})"

        # Act
        actual_arguments = p2m.extract_item_from_single_line(raw_method, p2m.arguments_pattern, target_capture_group=1)

        # Assert
        self.assertEqual(actual_arguments, expected_arguments)

    def test_07_complex_names(self):
        # Arrange
        expected_arguments = "first_argument: int, secondArgument"
        raw_method = f"def foo({expected_arguments})"

        # Act
        actual_arguments = p2m.extract_item_from_single_line(raw_method, p2m.arguments_pattern, target_capture_group=1)

        # Assert
        self.assertEqual(actual_arguments, expected_arguments)

    def test_08_return_type_and_default_value(self):
        # Arrange
        expected_arguments = "first: list[list[int]], second: list[str] = [], third: int = 42"
        raw_method = f"def foo({expected_arguments})"

        # Act
        actual_arguments = p2m.extract_item_from_single_line(raw_method, p2m.arguments_pattern, target_capture_group=1)

        # Assert
        self.assertEqual(actual_arguments, expected_arguments)


class TestExtractItemFromSingleLineArgumentNamePattern(unittest.TestCase):
    def test_01_one_argument_with_type(self):
        # Arrange
        expected_argument_name = "first"
        raw_argument = f"{expected_argument_name}: int"

        # Act
        actual_arguments = p2m.extract_item_from_single_line(
            raw_argument, p2m.argument_name_pattern, target_capture_group=1
        )

        # Assert
        self.assertEqual(actual_arguments, expected_argument_name)

    def test_02_one_argument_without_type(self):
        # Arrange
        expected_argument_name = "first"
        raw_argument = f"{expected_argument_name}"

        # Act
        actual_arguments = p2m.extract_item_from_single_line(
            raw_argument, p2m.argument_name_pattern, target_capture_group=1
        )

        # Assert
        self.assertEqual(actual_arguments, expected_argument_name)

    def test_03_complex_names(self):
        # Arrange
        expected_argument_name = "first_argument"
        raw_argument = f"{expected_argument_name}: int"

        # Act
        actual_arguments = p2m.extract_item_from_single_line(
            raw_argument, p2m.argument_name_pattern, target_capture_group=1
        )

        # Assert
        self.assertEqual(actual_arguments, expected_argument_name)

    def test_04_complex_type(self):
        # Arrange
        expected_argument_name = "first"
        raw_argument = f"{expected_argument_name}: list[list[int]]"

        # Act
        actual_arguments = p2m.extract_item_from_single_line(
            raw_argument, p2m.argument_name_pattern, target_capture_group=1
        )

        # Assert
        self.assertEqual(actual_arguments, expected_argument_name)

    def test_05_default_value_no_type_hint(self):
        # Arrange
        expected_argument_name = "first"
        raw_argument = f"{expected_argument_name} = 5"

        # Act
        actual_arguments = p2m.extract_item_from_single_line(
            raw_argument, p2m.argument_name_pattern, target_capture_group=1
        )

        # Assert
        self.assertEqual(actual_arguments, expected_argument_name)

    def test_06_default_value_with_type_hint(self):
        # Arrange
        expected_argument_name = "first"
        raw_argument = f"{expected_argument_name}: tuple[str, int] = ('', 2)"

        # Act
        actual_arguments = p2m.extract_item_from_single_line(
            raw_argument, p2m.argument_name_pattern, target_capture_group=1
        )

        # Assert
        self.assertEqual(actual_arguments, expected_argument_name)


class TestExtractItemFromSingleLineArgumentTypePattern(unittest.TestCase):
    def test_01_no_argument_type(self):
        # Arrange
        raw_argument = "first"

        # Act & Assert
        with self.assertRaises(ValueError):
            p2m.extract_item_from_single_line(raw_argument, p2m.argument_type_pattern, target_capture_group=1)

    def test_02_simple_argument_type(self):
        # Arrange
        expected_argument_type = "int"
        raw_argument = f"first: {expected_argument_type}"

        # Act
        actual_argument_type = p2m.extract_item_from_single_line(
            raw_argument, p2m.argument_type_pattern, target_capture_group=1
        )

        # Assert
        self.assertEqual(actual_argument_type, expected_argument_type)

    def test_03_complex_argument_type(self):
        # Arrange
        expected_argument_type = "list[int]"
        raw_argument = f"first: {expected_argument_type}"

        # Act
        actual_argument_type = p2m.extract_item_from_single_line(
            raw_argument, p2m.argument_type_pattern, target_capture_group=1
        )

        # Assert
        self.assertEqual(actual_argument_type, expected_argument_type)

    def test_04_argument_type_with_comma(self):
        # Arrange
        expected_argument_type = "dict[str, int]"
        raw_argument = f"first: {expected_argument_type}"

        # Act
        actual_argument_type = p2m.extract_item_from_single_line(
            raw_argument, p2m.argument_type_pattern, target_capture_group=1
        )

        # Assert
        self.assertEqual(actual_argument_type, expected_argument_type)

    def test_05_complex_argument_type_and_default_value(self):
        # Arrange
        expected_argument_type = "tuple[int, str]"
        raw_argument = f"first: {expected_argument_type} = (2, 'asd')"

        # Act
        actual_argument_type = p2m.extract_item_from_single_line(
            raw_argument, p2m.argument_type_pattern, target_capture_group=1
        )

        # Assert
        self.assertEqual(actual_argument_type, expected_argument_type)

    def test_06_no_whitespace(self):
        # Arrange
        expected_argument_type = "int"
        raw_argument = f"first:{expected_argument_type}"

        # Act
        actual_argument_type = p2m.extract_item_from_single_line(
            raw_argument, p2m.argument_type_pattern, target_capture_group=1
        )

        # Assert
        self.assertEqual(actual_argument_type, expected_argument_type)


class TestParseAttribute(unittest.TestCase):
    """
    Test cases for the parse_attribute function.
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up the test class
        """
        cls.__attribute_name = "attribute_name"
        cls.__attribute_value = 5
        cls.__attribute_type = "int"

    def test_01_attribute_name_extracted(self):
        """
        Verify that the attribute name is extracted correctly
        """
        # Arrange
        content = f"self.{self.__attribute_name} = {self.__attribute_value}"

        # Act
        result = p2m.parse_attribute(content)

        # Assert
        self.assertEqual(result.name, self.__attribute_name)

    def test_02_value_error_raised_when_name_is_not_matched(self):
        """
        Verify that a ValueError is raised when the attribute name is not matched
        """
        # Arrange
        content = "Invalid content"

        # Act & Assert
        with self.assertRaises(ValueError):
            p2m.parse_attribute(content)

    def test_03_not_an_attribute(self):
        """
        Verify that the function raises ValueError when the content is not an attribute
        """
        # Arrange
        content = f"{self.__attribute_name} = {self.__attribute_value}"

        # Act & Assert
        with self.assertRaises(ValueError):
            p2m.parse_attribute(content)

    @patch("src.converters.python_to_model.parse_visibility")
    def test_04_parse_visibility_called(self, mocked_parse_visibility):
        """
        Verify that the parse_visibility function is called
        """
        # Arrange
        content = f"self.{self.__attribute_name} = {self.__attribute_value}"

        # Act
        p2m.parse_attribute(content)

        # Assert
        mocked_parse_visibility.assert_called_once_with(content)

    def test_05_attribute_type_present_and_extracted(self):
        """
        Verify that the attribute type is present and extracted correctly
        """
        # Arrange
        content = f"self.{self.__attribute_name}: {self.__attribute_type} = {self.__attribute_value}"

        # Act
        result = p2m.parse_attribute(content)

        # Assert
        self.assertEqual(result.variable_type, self.__attribute_type)

    def test_06_attribute_type_not_present(self):
        """
        Verify that the attribute type is not present
        """
        # Arrange
        content = f"self.{self.__attribute_name} = {self.__attribute_value}"

        # Act
        result = p2m.parse_attribute(content)

        # Assert
        self.assertEqual(result.variable_type, "")


class TestGenerateModels(unittest.TestCase):
    """
    Test cases for the generate_models function
    """

    @patch("src.converters.python_to_model.generate_model")
    @patch("src.converters.python_to_model.split_classes")
    def test_01_split_classes_called(self, mocked_split_classes, _):
        """
        Verify that the split_classes function is called
        """
        # Arrange
        file_contents = ["class TestClass:", "    pass"]

        # Act
        p2m.generate_models(file_contents)

        # Assert
        mocked_split_classes.assert_called_once_with(file_contents)

    @patch("src.converters.python_to_model.generate_model")
    @patch("src.converters.python_to_model.split_classes")
    def test_02_generate_model_called(self, mocked_split_classes, mocked_generate_model: MagicMock):
        """
        Verify that the generate_model function is called
        """
        # Arrange
        file_contents = ["class TestClass:", "    pass"]
        sample_classes = ["first", "second", "third"]
        mocked_split_classes.return_value = sample_classes
        expected_args_list = [unittest.mock.call(item) for item in sample_classes]
        # Act
        p2m.generate_models(file_contents)

        # Assert
        self.assertEqual(mocked_generate_model.call_count, 3)
        self.assertEqual(mocked_generate_model.call_args_list, expected_args_list)


class TestGenerateModel(unittest.TestCase):
    """
    Test cases for the generate_model function
    """

    __class_content: list[str] = []
    __class_name = "TestClass"

    @classmethod
    def setUpClass(cls):
        """
        Set up the test class
        """
        cls.__class_content = [f"class {cls.__class_name}:", "    def foo(self):", "        print('Hi')"]

    @patch("src.converters.python_to_model.get_class_name")
    def test_01_get_class_name_called(self, mocked_get_class_name: MagicMock):
        """
        Verify that the get_class_name function is called
        """
        # Arrange
        mocked_get_class_name.return_value = self.__class_name

        # Act
        model = p2m.generate_model(self.__class_content)

        # Assert
        mocked_get_class_name.assert_called_once_with(self.__class_content[0])
        self.assertEqual(model.name, self.__class_name)

    @patch("src.converters.python_to_model.get_class_attributes")
    def test_02_get_class_attributes_called(self, mocked_get_class_attributes: MagicMock):
        """
        Verify that the get_class_attributes function is called
        """
        # Arrange
        mocked_get_class_attributes.return_value = []

        # Act
        p2m.generate_model(self.__class_content)

        # Assert
        mocked_get_class_attributes.assert_called_once_with(self.__class_content)

    @patch("src.converters.python_to_model.get_class_type")
    def test_03_get_class_type_called(self, mocked_get_class_type: MagicMock):
        """
        Verify that the get_class_type function is called
        """
        # Arrange
        expected_class_type = ClassType.CLASS
        mocked_get_class_type.return_value = expected_class_type

        # Act
        model = p2m.generate_model(self.__class_content)

        # Assert
        mocked_get_class_type.assert_called_once_with(self.__class_content[0])
        self.assertEqual(model.class_type, expected_class_type)

    @patch("src.converters.python_to_model.get_methods")
    def test_04_get_methods_called_no_methods(self, mocked_get_methods: MagicMock):
        """
        Verify that the get_methods function is called
        """
        # Arrange
        mocked_get_methods.return_value = []

        # Act
        model = p2m.generate_model(self.__class_content)

        # Assert
        mocked_get_methods.assert_called_once_with(self.__class_content)
        self.assertEqual(model.methods, None)

    @patch("src.converters.python_to_model.get_methods")
    def test_05_get_methods_called_with_methods(self, mocked_get_methods: MagicMock):
        """
        Verify that the get_methods function is called
        """
        # Arrange
        expected_methods = [Method("foo", Visibility.PROTECTED, None, "str")]
        mocked_get_methods.return_value = expected_methods

        # Act
        model = p2m.generate_model(self.__class_content)

        # Assert
        mocked_get_methods.assert_called_once_with(self.__class_content)
        self.assertEqual(model.methods, expected_methods)

    @patch("src.converters.python_to_model.get_static_methods")
    def test_06_get_static_methods_called_no_static_methods(self, mocked_get_static_methods: MagicMock):
        """
        Verify that the get_static_methods function is called
        """
        # Arrange
        mocked_get_static_methods.return_value = []

        # Act
        model = p2m.generate_model(self.__class_content)

        # Assert
        mocked_get_static_methods.assert_called_once_with(self.__class_content)
        self.assertEqual(model.static_methods, None)

    @patch("src.converters.python_to_model.get_static_methods")
    def test_07_get_static_methods_called_with_static_methods(self, mocked_get_static_methods: MagicMock):
        """
        Verify that the get_static_methods function is called
        """
        # Arrange
        expected_static_methods = [Method("foo", Visibility.PUBLIC, None, "str")]
        mocked_get_static_methods.return_value = expected_static_methods

        # Act
        model = p2m.generate_model(self.__class_content)

        # Assert
        mocked_get_static_methods.assert_called_once_with(self.__class_content)
        self.assertEqual(model.static_methods, expected_static_methods)

    @patch("src.converters.python_to_model.get_abstract_methods")
    def test_08_get_abstract_methods_called_no_abstract_methods(self, mocked_get_abstract_methods: MagicMock):
        """
        Verify that the get_abstract_methods function is called
        """
        # Arrange
        mocked_get_abstract_methods.return_value = []

        # Act
        model = p2m.generate_model(self.__class_content)

        # Assert
        mocked_get_abstract_methods.assert_called_once_with(self.__class_content)
        self.assertEqual(model.abstract_methods, None)

    @patch("src.converters.python_to_model.get_abstract_methods")
    def test_09_get_abstract_methods_called_with_abstract_methods(self, mocked_get_abstract_methods: MagicMock):
        """
        Verify that the get_abstract_methods function is called
        """
        # Arrange
        expected_abstract_methods = [Method("foo", Visibility.PUBLIC, None, "str")]
        mocked_get_abstract_methods.return_value = expected_abstract_methods

        # Act
        model = p2m.generate_model(self.__class_content)

        # Assert
        mocked_get_abstract_methods.assert_called_once_with(self.__class_content)
        self.assertEqual(model.abstract_methods, expected_abstract_methods)


class TestParseArgument(unittest.TestCase):
    @patch("src.converters.python_to_model.extract_item_from_single_line")
    def test_01_extract_item_called_for_argument(self, mocked_extract_item: MagicMock):
        """
        Verify that the extract_item_from_single_line function is called
        """
        # Arrange
        raw_argument = "a: int"
        expected_call = call(raw_argument, p2m.argument_name_pattern, target_capture_group=1)
        mocked_extract_item.return_value = "a: int"

        # Act
        p2m.parse_argument(raw_argument)

        # Assert
        self.assertEqual(mocked_extract_item.call_args_list[0], expected_call)

    @patch("src.converters.python_to_model.extract_item_from_single_line")
    def test_02_extract_item_raises_exception(self, mocked_extract_item: MagicMock):
        """
        Verify that the parse_argument function returns None when extract_item_from_single_line raises an exception
        """
        # Arrange
        raw_argument = "a: int"
        mocked_extract_item.side_effect = ValueError("No argument found")

        # Act & Assert
        with self.assertRaises(ValueError):
            p2m.parse_argument(raw_argument)

    @patch("src.converters.python_to_model.parse_visibility")
    def test_03_parse_visibility_called(self, mocked_parse_visibility: MagicMock):
        """
        Verify that the parse_visibility function is called
        """
        # Arrange
        raw_argument = "a: int"
        expected_call = call(raw_argument)
        expected_visibility = Visibility.PUBLIC
        mocked_parse_visibility.return_value = expected_visibility

        # Act
        model = p2m.parse_argument(raw_argument)

        # Assert
        self.assertEqual(mocked_parse_visibility.call_args_list[0], expected_call)
        self.assertEqual(model.visibility, expected_visibility)

    @patch("src.converters.python_to_model.extract_item_from_single_line")
    def test_04_extract_item_called_for_return_type(self, mocked_extract_item: MagicMock):
        """
        Verify that the extract_item_from_single_line function is called for the return type
        """
        # Arrange
        raw_argument = "a: int"
        expected_call = call(raw_argument, p2m.argument_type_pattern, target_capture_group=1)
        mocked_extract_item.return_value = "int"

        # Act
        p2m.parse_argument(raw_argument)

        # Assert
        self.assertEqual(mocked_extract_item.call_args_list[1], expected_call)

    @patch("src.converters.python_to_model.extract_item_from_single_line")
    def test_05_extract_item_raises_exception_for_return_type(self, mocked_extract_item: MagicMock):
        """
        Verify that the parse_argument function returns None when extract_item_from_single_line raises an exception
        """
        # Arrange
        raw_argument = "a: int"

        mocked_extract_item.side_effect = ["a: int", ValueError("No return type found")]

        # Act
        model = p2m.parse_argument(raw_argument)

        # Assert
        self.assertEqual(model.variable_type, "")
