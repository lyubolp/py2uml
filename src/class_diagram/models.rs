#[derive(Debug)]
pub enum ClassType {
    CLASS,
    ABSTRACT,
    ENUM,
    EXCEPTION,
}

#[derive(Debug)]
pub enum Visibility {
    PUBLIC,
    PRIVATE,
    PROTECTED,
}

#[derive(Debug)]
pub enum LinkType {
    EXTENSION,
    COMPOSITION,
    AGGREGATION,
    NORMAL,
}

#[derive(Debug)]
pub struct Variable {
    name: String,
    visibility: Visibility,
    variable_type: String,
}

impl Variable {
    pub fn new(name: &String, visiblity: Visibility, variable_type: &String) -> Self {
        Variable {
            name: name.clone(),
            visibility: visiblity,
            variable_type: variable_type.clone(),
        }
    }
}

#[derive(Debug)]
pub struct Function {
    name: String,
    visibility: Visibility,
    arguments: Option<Vec<Variable>>,
    return_type: Option<String>,
}

impl Function {
    pub fn new(
        name: &String,
        visibility: Visibility,
        arguments: Option<Vec<Variable>>,
        return_type: Option<String>,
    ) -> Self {
        Function {
            name: name.clone(),
            visibility,
            arguments,
            return_type,
        }
    }
}

#[derive(Debug)]
pub struct ClassModel {
    name: String,
    attributes: Option<Vec<Variable>>,
    methods: Option<Vec<Function>>,
    properties: Option<Vec<Variable>>,
    class_type: ClassType,
    static_methods: Option<Vec<Function>>,
    abstract_methods: Option<Vec<Function>>,
}

impl ClassModel {
    pub fn new(
        name: &String,
        attributes: Option<Vec<Variable>>,
        methods: Option<Vec<Function>>,
        properties: Option<Vec<Variable>>,
        class_type: ClassType,
        static_methods: Option<Vec<Function>>,
        abstract_methods: Option<Vec<Function>>,
    ) -> Self {
        ClassModel {
            name: name.clone(),
            attributes,
            methods,
            properties,
            class_type,
            static_methods,
            abstract_methods,
        }
    }
}
