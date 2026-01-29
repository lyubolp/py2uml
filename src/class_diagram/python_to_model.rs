use ruff_python_ast::{Expr, Parameter, Stmt, StmtClassDef, StmtFunctionDef};
use ruff_python_parser;
use std::fs::read;

use super::models;

pub fn generate_models(filepaths: &Vec<String>) -> Vec<models::ClassModel> {
    filepaths
        .iter()
        .flat_map(extract_classes)
        .flatten()
        .map(|class| generate_model(&class))
        .collect()
}

fn generate_model(class: &StmtClassDef) -> models::ClassModel {
    let class_type = if let Some(parents) = &extract_parent_classes(class) {
        determine_class_type_from_parents(parents)
    } else {
        models::ClassType::CLASS
    };

    models::ClassModel::new(
        &extract_name(class),
        extract_attributes(class),
        extract_methods(class),
        extract_properties(class),
        class_type,
        extract_static_methods(class),
        extract_abstract_methods(class),
    )
}

fn extract_classes(filepath: &String) -> Result<Vec<StmtClassDef>, String> {
    let content = String::from_utf8(read(filepath).unwrap()).unwrap();

    match ruff_python_parser::parse_module(&content) {
        Ok(items) => Ok(items
            .syntax()
            .body
            .clone()
            .into_iter()
            .filter_map(|stmt| stmt.class_def_stmt())
            .collect::<Vec<StmtClassDef>>()),
        Err(e) => Err(format!("Failed to parse Python file: {}", e)),
    }
}

fn extract_name(model: &StmtClassDef) -> String {
    model.name.id.clone()
}

fn extract_attributes(parser_model: &StmtClassDef) -> Option<Vec<models::Variable>> {
    let Some(init_function) = parser_model
        .body
        .iter()
        .filter_map(|item| item.clone().function_def_stmt())
        .find(|function| function.name.eq("__init__"))
    else {
        return None;
    };

    let raw_attributes = extract_raw_attributes(&init_function);

    if !raw_attributes.is_empty() {
        Some(
            raw_attributes
                .iter()
                .map(|name| {
                    models::Variable::new(name, extract_visibility(name), &String::from(""))
                })
                .collect(),
        )
    } else {
        None
    }
}

fn extract_raw_attributes(init_function: &StmtFunctionDef) -> Vec<String> {
    // TODO - Add type information
    let mut stack: Vec<Stmt> = vec![];
    let mut result: Vec<String> = vec![];

    for statement in init_function.body.clone() {
        stack.push(statement);
    }

    while let Some(current) = stack.pop() {
        match current {
            Stmt::AugAssign(ruff_python_ast::StmtAugAssign { target, .. })
            | Stmt::AnnAssign(ruff_python_ast::StmtAnnAssign { target, .. }) => {
                if target.is_attribute_expr() {
                    result.push(target.attribute_expr().unwrap().attr.id)
                }
            }
            Stmt::Match(ruff_python_ast::StmtMatch { cases, .. }) => {
                for case in cases {
                    stack.extend(case.body);
                }
            }
            Stmt::ClassDef(ruff_python_ast::StmtClassDef { body, .. })
            | Stmt::FunctionDef(ruff_python_ast::StmtFunctionDef { body, .. })
            | Stmt::Try(ruff_python_ast::StmtTry { body, .. })
            | Stmt::If(ruff_python_ast::StmtIf { body, .. })
            | Stmt::With(ruff_python_ast::StmtWith { body, .. }) => {
                stack.extend(body);
            }
            Stmt::Assign(ruff_python_ast::StmtAssign { targets, .. }, ..) => {
                result.push(targets[0].clone().attribute_expr().unwrap().attr.id)
            }
            _ => {}
        }
    }
    result
}

fn extract_visibility(name: &String) -> models::Visibility {
    // Extract visibility based on naming conventions from a string name
    if name.starts_with("__") && !name.ends_with("__") {
        models::Visibility::PRIVATE
    } else if name.starts_with("_") {
        models::Visibility::PROTECTED
    } else {
        models::Visibility::PUBLIC
    }
}

fn extract_methods(parser_model: &StmtClassDef) -> Option<Vec<models::Function>> {
    let raw_methods = parser_model
        .body
        .iter()
        .filter_map(|item| item.clone().function_def_stmt())
        .filter(|function| !function.name.eq("__init__"))
        .filter(|function| !does_function_have_decorator(function, &String::from("property")))
        .filter(|function| !does_function_have_decorator(function, &String::from("abstractmethod")))
        .filter(|function| !does_function_have_decorator(function, &String::from("staticmethod")))
        .collect::<Vec<StmtFunctionDef>>();

    if !raw_methods.is_empty() {
        Some(raw_methods.iter().map(extract_method).collect())
    } else {
        None
    }
}

fn extract_method(method: &StmtFunctionDef) -> models::Function {
    models::Function::new(
        &method.name.id,
        extract_visibility(&method.name.id),
        extract_method_arguments(method),
        extract_method_return_type(method),
    )
}

fn extract_method_arguments(method: &StmtFunctionDef) -> Option<Vec<models::Variable>> {
    let mut result: Vec<models::Variable> = vec![];

    for argument in &method.parameters.args {
        result.push(extract_method_argument(&argument.parameter));
    }

    if let Some(argument) = &method.parameters.kwarg {
        result.push(extract_method_argument(argument));
    }

    for argument in &method.parameters.kwonlyargs {
        result.push(extract_method_argument(&argument.parameter));
    }

    for argument in &method.parameters.posonlyargs {
        result.push(extract_method_argument(&argument.parameter));
    }

    if let Some(argument) = &method.parameters.vararg {
        result.push(extract_method_argument(argument));
    }

    if !result.is_empty() {
        Some(result)
    } else {
        None
    }
}

fn extract_method_argument(argument: &Parameter) -> models::Variable {
    let variable_type = match &argument.annotation {
        Some(annotation) => match annotation.as_name_expr() {
            Some(name_expr) => name_expr.id.clone(),
            None => String::from(""),
        },
        None => String::from(""),
    };

    models::Variable::new(
        &argument.name.id,
        extract_visibility(&argument.name.id),
        &variable_type,
    )
}

fn extract_method_return_type(method: &StmtFunctionDef) -> Option<String> {
    match &method.returns {
        Some(annotation) => annotation
            .as_name_expr()
            .map(|name_expr| name_expr.id.clone()),
        None => None,
    }
}

fn extract_properties(parser_model: &StmtClassDef) -> Option<Vec<models::Variable>> {
    let raw_properties = parser_model
        .body
        .iter()
        .filter_map(|item| item.clone().function_def_stmt())
        .filter(|function| does_function_have_decorator(function, &String::from("property")))
        .collect::<Vec<StmtFunctionDef>>();

    if !raw_properties.is_empty() {
        Some(
            raw_properties
                .iter()
                .map(|property| {
                    models::Variable::new(
                        &property.name.id,
                        extract_visibility(&property.name.id),
                        &extract_method_return_type(property).unwrap_or(String::from("")), // TODO - Extract type from return annotation
                    )
                })
                .collect(),
        )
    } else {
        None
    }
}

fn does_function_have_decorator(function: &StmtFunctionDef, decorator_name: &String) -> bool {
    function.decorator_list.iter().any(|decorator| {
        decorator
            .expression
            .as_name_expr()
            .is_some_and(|name| name.id == *decorator_name)
    })
}

fn extract_abstract_methods(parser_model: &StmtClassDef) -> Option<Vec<models::Function>> {
    let raw_methods = parser_model
        .body
        .iter()
        .filter_map(|item| item.clone().function_def_stmt())
        .filter(|function| does_function_have_decorator(function, &String::from("abstractmethod")))
        .collect::<Vec<StmtFunctionDef>>();

    if !raw_methods.is_empty() {
        Some(raw_methods.iter().map(extract_method).collect())
    } else {
        None
    }
}

fn extract_static_methods(parser_model: &StmtClassDef) -> Option<Vec<models::Function>> {
    let raw_methods = parser_model
        .body
        .iter()
        .filter_map(|item| item.clone().function_def_stmt())
        .filter(|function| does_function_have_decorator(function, &String::from("staticmethod")))
        .collect::<Vec<StmtFunctionDef>>();

    if !raw_methods.is_empty() {
        Some(raw_methods.iter().map(extract_method).collect())
    } else {
        None
    }
}

fn extract_parent_classes(class: &StmtClassDef) -> Option<Vec<String>> {
    if let Some(args) = class.arguments.clone() {
        Some(
            args.args
                .iter()
                .filter_map(|base| extract_parent_class(base))
                .collect(),
        )
    } else {
        None
    }
}

fn extract_parent_class(argument: &Expr) -> Option<String> {
    if argument.is_name_expr() {
        Some(argument.as_name_expr().unwrap().id.clone())
    } else if argument.is_subscript_expr() {
        Some(
            argument
                .as_subscript_expr()
                .unwrap()
                .value
                .as_name_expr()
                .unwrap()
                .id
                .clone(),
        )
    } else {
        println!("Unknown parent class expression: {:?}", argument);
        None
    }
}

fn determine_class_type_from_parents(parents: &Vec<String>) -> models::ClassType {
    if parents
        .iter()
        .any(|parent| parent.eq("ABC") || parent.eq("ABCMeta"))
    {
        models::ClassType::ABSTRACT
    } else if parents
        .iter()
        .any(|parent| parent.eq("Enum") || parent.eq("enum.Enum"))
    {
        models::ClassType::ENUM
    } else if parents.iter().any(|parent| parent.eq("Exception")) {
        models::ClassType::EXCEPTION
    } else {
        models::ClassType::CLASS
    }
}
