use clap::Parser;
use std::path::PathBuf;

#[derive(Parser)]
#[command(
    author,
    version,
    about = "Generate PlantUML dependency diagrams for Python projects"
)]
pub struct Args {
    /// Path to the Python project root directory
    #[arg(help = "Path to the Python project root")]
    pub input_path: PathBuf,

    /// Path to save the PlantUML diagram
    #[arg(help = "Output file for the PlantUML diagram (must end with .puml)")]
    pub output_path: PathBuf,
}

impl Args {
    pub fn validate(&self) -> Result<(), String> {
        // Validate input path exists and is a directory
        if !self.input_path.exists() {
            return Err(format!(
                "Input path '{}' does not exist",
                self.input_path.display()
            ));
        }
        if !self.input_path.is_dir() {
            return Err(format!(
                "Input path '{}' is not a directory",
                self.input_path.display()
            ));
        }

        // Validate output path extension
        match self.output_path.extension() {
            Some(ext) if ext == "puml" => Ok(()),
            _ => Err(format!(
                "Output path '{}' must have .puml extension",
                self.output_path.display()
            )),
        }
    }
}
