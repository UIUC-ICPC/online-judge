use serde::Deserialize;
use std::{collections::HashMap, fs, path::Path};

#[derive(Debug, Deserialize)]
pub struct Command {
    pub program: String,
    pub args: Vec<String>,
}

#[derive(Debug, Deserialize)]
pub struct LanguageConfig {
    pub environment: String,
    pub compile: Vec<Command>,
    pub run: Command,
}

pub type LanguageConfigs = HashMap<String, LanguageConfig>;

pub fn load_language_configs(
    path: impl AsRef<Path>,
) -> Result<LanguageConfigs, Box<dyn std::error::Error>> {
    let contents = fs::read_to_string(path)?;
    Ok(serde_json::from_str(&contents)?)
}
