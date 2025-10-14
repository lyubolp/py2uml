use crate::tree::{TreeNode, insert};
use crate::{graph::Graph, module::PythonModule};

pub fn generate_plantuml(graph: &Graph<PythonModule>) -> Vec<String> {
    let colors: Vec<&str> = vec![
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
        "#bcbd22", "#17becf",
    ];

    let mut result: Vec<String> = vec![];

    result.push(String::from("@startuml"));

    result.push(String::from(""));

    result.extend(declare_diagram_style());

    result.push(String::from(""));

    let tree_node = build_tree_from_dependency_graph(graph);
    let mut buffer: Vec<String> = vec![];

    declare_modules_into_packages(&tree_node, 0, &mut buffer);
    for item in buffer {
        result.push(item);
    }

    result.push(String::from(""));

    result.extend(declare_connections(graph, colors));

    result.push(String::from("@enduml"));
    result
}

fn declare_diagram_style() -> Vec<String> {
    let mut result = vec![];
    result.push(String::from("skinparam packageStyle rectangle"));
    result.push(String::from("skinparam linetype ortho"));
    result.push(String::from("skinparam class {"));
    result.push(String::from("    BackgroundColor White"));
    result.push(String::from("    BorderColor Black"));
    result.push(String::from("}"));
    result.push(String::from("left to right direction"));

    result
}

fn declare_connections(graph: &Graph<PythonModule>, colors: Vec<&str>) -> Vec<String> {
    let mut result: Vec<String> = vec![];
    for node in graph.get_nodes() {
        if let Ok(edges) = graph.get_edges(node) {
            for (i, edge) in edges.iter().enumerate() {
                let content = String::from(&format!(
                    "[\"{}\"] -[{}]-> [\"{}\"]",
                    node.get_name(),
                    colors[i % colors.len()],
                    edge.get_name()
                ));
                result.push(content);
            }
            result.push(String::from(""));
        }
    }
    result
}

fn build_tree_from_dependency_graph(graph: &Graph<PythonModule>) -> TreeNode {
    let mut root = TreeNode::new(String::from("pygrader"));

    for node in graph.get_nodes() {
        let mut packages: Vec<String> = node
            .get_packages()
            .iter()
            .filter(|item| *item != "")
            .map(|item| item.clone())
            .collect();
        packages.push(node.get_name().clone());

        insert(&mut root, packages);
    }

    root
}

fn declare_modules_into_packages(root: &TreeNode, level: usize, buffer: &mut Vec<String>) {
    if root.get_children().len() == 0 {
        buffer.push(String::from(format!(
            "{}[\"{}\"]",
            " ".repeat(level * 4),
            root.get_value()
        )));
        return;
    } else {
        buffer.push(String::from(format!(
            "{}package \"{}\" {{",
            " ".repeat(level * 4),
            root.get_value()
        )));
        for child in root.get_children().iter().rev() {
            declare_modules_into_packages(child, level + 1, buffer);
        }
        buffer.push(String::from(format!("{}{}", " ".repeat(level * 4), "}")));
    }
}
