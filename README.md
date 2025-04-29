# Py2UML

Python script that generates UML class diagrams from Python source code.

## Functionality

- Scan a directory and find all Python files
- Parse each Python file
- Extract all classes
- For each class, extract all attributes and methods
- Attributes have their names, types and visibility extracted
- Methods have their names, return types, parameters and visibility extracted
- Classes have their name, attributes, methods, class type, static methods and abstract methods extracted
- Generate a UML class diagram in PlantUML format

## TODOs

- For each class, extract all attributes and methods
- Attributes have their names, types and visibility extracted
- Methods have their names, return types, parameters and visibility extracted
- Classes have their name, attributes, methods, class type, static methods and abstract methods extracted
- Generate a UML class diagram in PlantUML format
- Add support for class inheritance
- Think about functions and their representation
- Consider replacing empty strings with None
- Unit tests
- Functional tests that verify the functionality
- Documentation
- CI/CD pipeline
- PyPI package

## Limitations

    - Does not support classes defined in other classes
    - Does not support multiline attribute definitions
    - Does not support links between classes
    - Missing class attributes
    - Does not support data classes
    - Does not support just functions
