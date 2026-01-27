use std::path::{Path, PathBuf};

pub fn is_import_internal(import: &String, root_dir: &str) -> bool {
    let current_path = Path::new(root_dir).join(&split_import(import)[0]);

    current_path.is_dir()
}

pub fn split_import(import: &str) -> Vec<String> {
    import.split(".").map(|s| String::from(s)).collect()
}

pub fn extract_module_name_from_import(import: &String, root_dir: &str) -> String {
    let parts = split_import(import);

    let mut current_path = PathBuf::new();
    current_path.push(root_dir);

    let mut result = vec![];

    for part in &parts {
        let current_path_as_file = current_path.join(String::from(part) + ".py");

        current_path.push(part);
        if !(current_path.is_dir() || current_path_as_file.is_file()) {
            break;
        }

        result.push(part.clone());
    }

    result.join(".")
}
