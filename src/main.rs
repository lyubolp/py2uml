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

use crate::cli::{Args, DiagramType};
use crate::dependency_graph::graph_to_uml;
use crate::dependency_graph::python_to_graph::build_dependency_graph;
use crate::utils::file_utils::discover_files;

fn main() {
    let args = Args::parse();
    let args_validation = args.validate();

    if let Err(e) = args_validation {
        eprintln!("Error: {}", e);
        std::process::exit(1);
    }

    let files = discover_files(args.input_path.to_str().unwrap());

    let content = match args.diagram_type {
        DiagramType::Class => {
            println!("Generating class diagram...");
            let models = generate_models(&files);
            model_to_uml::generate_plantuml(&models)
        }
        DiagramType::Dependency => {
            println!("Generating dependency diagram...");
            let graph = build_dependency_graph(files, args.input_path.to_str().unwrap());
            graph_to_uml::generate_plantuml(&graph)
        }
    };

    if let Ok(mut file) = File::create(&args.output_path) {
        for line in content {
            let write_result = writeln!(file, "{}", line);
            if let Err(e) = write_result {
                eprintln!(
                    "Error: Failed to write to output file '{}': {}",
                    args.output_path.display(),
                    e
                );
                std::process::exit(1);
            }
        }
    } else {
        eprintln!(
            "Error: Failed to create output file '{}'",
            args.output_path.display()
        );
        std::process::exit(1);
    }

    println!(
        "PlantUML diagram successfully generated at '{}'",
        args.output_path.display()
    );
}
