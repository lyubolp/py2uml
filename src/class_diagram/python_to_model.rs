use ruff_python_ast::{Parameter, Stmt, StmtClassDef, StmtFunctionDef};
use ruff_python_parser;
use std::{fs::read, result};

use super::models;

pub fn generate_models(filepaths: &Vec<String>) -> Vec<models::ClassModel> {
    let classes = extract_classes(&filepaths[0]).unwrap();

    vec![generate_model(&classes[0])]
}

fn generate_model(class: &StmtClassDef) -> models::ClassModel {
    models::ClassModel::new(
        &extract_name(class),
        extract_attributes(class),
        extract_methods(class),
        None,
        models::ClassType::CLASS,
        None,
        None,
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
            .collect::<Vec<StmtClassDef>>()
            .into()),
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
        .filter(|function| function.name.eq("__init__"))
        .next()
    else {
        return None;
    };

    let raw_attributes = extract_raw_attributes(&init_function);

    if raw_attributes.len() > 0 {
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

    while !stack.is_empty() {
        let current = stack.pop().unwrap();

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
        .collect::<Vec<StmtFunctionDef>>();

    if raw_methods.len() > 0 {
        Some(
            raw_methods
                .iter()
                .map(|method| extract_method(method))
                .collect(),
        )
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
        result.push(extract_method_argument(&argument));
    }

    if result.len() > 0 { Some(result) } else { None }
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
        Some(annotation) => match annotation.as_name_expr() {
            Some(name_expr) => Some(name_expr.id.clone()),
            None => None,
        },
        None => None,
    }
}
