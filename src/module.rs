use std::fmt::{Display, Formatter};

#[derive(Clone, Hash, Eq, PartialEq, Debug)]
pub struct PythonModule {
    name: String,
    packages: Vec<String>,
}

impl PythonModule {
    pub fn new(name: &str, packages: &Vec<String>) -> Self {
        PythonModule {
            name: String::from(name),
            packages: packages.clone(),
        }
    }

    pub fn get_name(&self) -> &String {
        &self.name
    }

    pub fn get_packages(&self) -> &Vec<String> {
        &self.packages
    }
}

impl Display for PythonModule {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "Module '{}' with dependencies: [{}]",
            self.name,
            self.packages.join(", ")
        )
    }
}
