use std::{collections::HashSet, fs::read, path::Path};

use ruff_python_ast::Stmt;
use ruff_python_parser;

use crate::graph::Graph;
use crate::module::PythonModule;
use crate::python_utils::{extract_module_name_from_import, is_import_internal, split_import};

pub fn build_dependency_graph(files: Vec<String>, root_dir: &str) -> Graph<PythonModule> {
    let mut graph = Graph::new();

    for filepath in files {
        let file_path = Path::new(&filepath);

        let module_name = extract_module_name_from_file_path(&filepath);
        let packages = extract_packages(root_dir, file_path);

        let module = PythonModule::new(&module_name, &packages);

        _ = graph.add_node(&module);

        for dependency in get_all_dependencies(&filepath, root_dir) {
            if !graph.is_node_in_graph(&dependency) {
                _ = graph.add_node(&dependency);
            }
            _ = graph.add_edge(&module, &dependency);
        }
    }

    graph
}

fn extract_module_name_from_file_path(filepath: &String) -> String {
    String::from(Path::new(filepath).file_stem().unwrap().to_str().unwrap())
}

fn extract_packages(root_dir: &str, file_path: &Path) -> Vec<String> {
    String::from(
        file_path
            .strip_prefix(root_dir)
            .unwrap()
            .parent()
            .unwrap()
            .to_str()
            .unwrap(),
    )
    .split("/")
    .map(String::from)
    .collect()
}

fn get_all_dependencies(filepath: &String, root_dir: &str) -> HashSet<PythonModule> {
    let content = String::from_utf8(read(filepath).unwrap()).unwrap();
    let result = ruff_python_parser::parse_module(&content).unwrap();

    let mut names: HashSet<PythonModule> = HashSet::new();

    for item in result.syntax().body.clone() {
        names.extend(extract_names(item.clone(), root_dir).into_iter());
    }

    names
}

fn extract_names(item: Stmt, root_dir: &str) -> HashSet<PythonModule> {
    let names = if item.is_import_from_stmt() {
        extract_names_from_import_from_statement(item)
    } else if item.is_import_stmt() {
        extract_names_from_import_statement(item)
    } else {
        HashSet::new()
    };

    names
        .iter()
        .map(|name| extract_module_name_from_import(name, root_dir))
        .filter(|name| is_import_internal(name, root_dir))
        .map(|name| split_import(&name))
        .map(|names| {
            PythonModule::new(
                names.last().unwrap_or(&String::new()),
                &names
                    .split_last()
                    .map(|(_, rest)| rest.to_vec())
                    .unwrap_or_default(),
            )
        })
        .filter(|module| module.get_name() != "")
        .collect()
}

fn extract_names_from_import_statement(item: Stmt) -> HashSet<String> {
    // TODO - This could return just an iterator
    item.import_stmt()
        .unwrap()
        .names
        .iter()
        .map(|import| import.name.id.clone())
        .collect()
}

fn extract_names_from_import_from_statement(item: Stmt) -> HashSet<String> {
    // TODO - This could return just an iterator
    let statement = item.import_from_stmt().unwrap();

    let Some(module) = statement.module else {
        // TODO - This ignores imports from parent package
        return HashSet::new();
    };

    statement
        .names
        .iter()
        .map(|alias| module.id.clone() + "." + &alias.name.id)
        .collect()
}
