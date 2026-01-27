mod class_diagram;
mod cli;
mod constants;
mod dependency_graph;
mod utils;

use clap::Parser;
use std::fs::File;
use std::io::Write;

use crate::class_diagram::model_to_uml;
use crate::class_diagram::python_to_model::generate_models;

use crate::cli::Args;
use crate::dependency_graph::graph_to_uml::generate_plantuml;
use crate::dependency_graph::python_to_graph::build_dependency_graph;
use crate::utils::file_utils::discover_files;

fn run() -> Result<(), String> {
    let args = Args::parse();
    args.validate()?;

    let files = discover_files(args.input_path.to_str().unwrap());
    let graph = build_dependency_graph(files, args.input_path.to_str().unwrap());
    let content = generate_plantuml(&graph);

    let mut file = File::create(&args.output_path)
        .map_err(|e| format!("Failed to create output file: {}", e))?;

    for line in content {
        writeln!(file, "{}", line).map_err(|e| format!("Failed to write to output file: {}", e))?;
    }

    Ok(())
}

fn main() {
    // if let Err(e) = run() {
    //     eprintln!("Error: {}", e);
    //     std::process::exit(1);
    // }

    let models = generate_models(&vec![String::from("/Users/lyubolp/py2uml/sample.py")]);

    let content = model_to_uml::generate_plantuml(&models);

    println!("{:#?}", models);

    let mut file = File::create("sample.puml")
        .map_err(|e| format!("Failed to create output file: {}", e))
        .unwrap();

    for line in content {
        writeln!(file, "{}", line)
            .map_err(|e| format!("Failed to write to output file: {}", e))
            .unwrap();
    }
}
