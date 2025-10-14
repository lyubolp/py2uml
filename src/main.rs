mod cli;
mod constants;
mod file_utils;
mod graph;
mod graph_to_uml;
mod module;
mod python_to_graph;
mod python_utils;
mod tree;

use clap::Parser;
use std::fs::File;
use std::io::Write;

use crate::cli::Args;
use crate::file_utils::discover_files;
use crate::graph_to_uml::generate_plantuml;
use crate::python_to_graph::build_dependency_graph;

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
    if let Err(e) = run() {
        eprintln!("Error: {}", e);
        std::process::exit(1);
    }
}
