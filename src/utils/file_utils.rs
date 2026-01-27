use walkdir::{WalkDir, DirEntry};


pub fn discover_files(root: &str) -> Vec<String> {
    let all_paths = WalkDir::new(root)
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| e.path().is_file())
        .filter(|e| {
            if let Some(ext) = e.path().extension() {
                ext == "py" && !is_path_ignored(e)
            } else {
                false
            }
        })
        .map(|e| e.path().to_string_lossy().to_string())
        .collect::<Vec<String>>();

    all_paths
}

fn is_path_ignored(path: &DirEntry) -> bool {
    let ignore_list  = vec![".venv", "tests", "docs", "__init__.py"];

    ignore_list.iter().any(|&item| path.path().to_str().unwrap().contains(item))
    
}