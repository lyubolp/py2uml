use super::models;

pub fn generate_plantuml(models: &Vec<models::ClassModel>) -> Vec<String> {
    let mut result: Vec<String> = vec![];

    result.push(String::from("@startuml"));

    result.push(String::from(""));

    for model in models {
        let uml_lines = model_to_uml(model);
        for line in uml_lines {
            result.push(line);
        }
        result.push(String::from(""));
    }

    result.push(String::from("@enduml"));
    result
}

fn model_to_uml(model: &models::ClassModel) -> Vec<String> {
    let mut result: Vec<String> = vec![];

    result.push(format!("class {} {{", model.name()));

    if let Some(attributes) = model.attributes() {
        for attribute in attributes {
            result.push(attribute_to_uml(attribute));
        }
    }

    if let Some(methods) = model.methods() {
        for method in methods {
            result.push(method_to_uml(method));
        }
    }

    result.push(String::from("}"));

    result.push(String::from(""));

    result
}

fn attribute_to_uml(attribute: &models::Variable) -> String {
    if attribute.variable_type().is_empty() {
        format!(
            "    {} {}",
            visibility_to_uml(attribute.visibility()),
            attribute.name()
        )
    } else {
        format!(
            "    {} {} : {}",
            visibility_to_uml(attribute.visibility()),
            attribute.name(),
            attribute.variable_type()
        )
    }
}

fn method_to_uml(method: &models::Function) -> String {
    let args = arguments_to_uml(method.arguments().as_ref());
    let return_type = return_type_to_uml(method.return_type().as_ref());

    if return_type.is_empty() {
        format!(
            "    {} {}({})",
            visibility_to_uml(method.visibility()),
            method.name(),
            args
        )
    } else {
        format!(
            "    {} {}({}) : {}",
            visibility_to_uml(method.visibility()),
            method.name(),
            args,
            return_type
        )
    }
}

fn arguments_to_uml(arguments: Option<&Vec<models::Variable>>) -> String {
    match arguments {
        Some(args) => args
            .iter()
            .map(argument_to_uml)
            .collect::<Vec<String>>()
            .join(", "),
        None => String::from(""),
    }
}

fn argument_to_uml(argument: &models::Variable) -> String {
    if argument.variable_type().is_empty() {
        argument.name().to_string()
    } else {
        format!("{}: {}", argument.name(), argument.variable_type())
    }
}

fn return_type_to_uml(return_type: Option<&String>) -> String {
    match return_type {
        Some(ret_type) => ret_type.clone(),
        None => String::from("void"),
    }
}

fn visibility_to_uml(visibility: &models::Visibility) -> &str {
    match visibility {
        models::Visibility::PUBLIC => "+",
        models::Visibility::PRIVATE => "-",
        models::Visibility::PROTECTED => "#",
    }
}
