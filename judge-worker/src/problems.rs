use std::fs::read_to_string;
use std::path::{Path, PathBuf};

use serde::{Deserialize, Serialize};

#[derive(Debug)]
pub struct Testcase {
    pub input: PathBuf,
    pub output: PathBuf,
}

pub fn testcases_from_dir(
    path: &Path,
    testcase_name: &str,
) -> Result<Vec<Testcase>, Box<dyn std::error::Error>> {
    let entries = path.read_dir()?;

    let mut names = Vec::new();
    for entry in entries {
        let entry = entry?;
        if !entry.file_type()?.is_file() {
            continue;
        }

        let file_name = entry.file_name();
        let Some(file_name) = file_name.to_str() else {
            continue;
        };
        let Some(name) = file_name.strip_suffix(".in") else {
            continue;
        };
        if name.starts_with(testcase_name) {
            names.push(name.to_owned());
        }
    }

    // testcases should be in lexicographical order,
    // padding numbers with leading 0s as needed.
    // so we can naively use names.sort() here.
    names.sort();

    let mut testcases = Vec::with_capacity(names.len());
    for name in names {
        let input = path.join(format!("{name}.in"));
        let output = path.join(format!("{name}.ans"));
        if !output.is_file() {
            return Err(format!(
                "testcase '{name}' is missing answer file: {}",
                output.display()
            )
            .into());
        }
        testcases.push(Testcase { input, output });
    }

    Ok(testcases)
}

#[derive(Debug)]
pub struct Problem {
    // pub time_limit_seconds: Duration,
    // pub memory_limit_kib: u32,
    pub metadata: ProblemMetadata,
    pub sample_tests: Vec<Testcase>,
    pub secret_tests: Vec<Testcase>,
}

#[derive(Debug, Clone, Copy, Deserialize, Serialize)]
#[serde(default)]
pub struct Limits {
    // submission limits
    /// maximum time per test case, in seconds
    pub time_limit: f32,
    /// maximum memory usage in MiB
    pub memory: u32,
    /// maximum total output in MiB
    pub output: u32,
    /// maximum total size of the submitted files in KiB
    pub code: u32,

    // resource guarantees
    /// maximum compilation time, in seconds
    pub compilation_time: f32,
    /// maximum compilation memory in MiB
    pub compilation_memory: u32,
    /// maximum output validation time, in seconds
    pub validation_time: f32,
    /// maximum output validation memory in MiB
    pub validation_memory: u32,
    /// maximum output validator output in MiB
    pub validation_output: u32,
}

impl Default for Limits {
    fn default() -> Self {
        Limits {
            time_limit: 2.0,
            memory: 256,
            output: 8,
            code: 128,
            compilation_time: 60.0,
            compilation_memory: 2048,
            validation_time: 60.0,
            validation_memory: 2048,
            validation_output: 8,
        }
    }
}

/// https://www.kattis.com/problem-package-format/spec/2025-09.html#problem-metadata
/// only parses a subset of the spec.
/// importantly, the type key is currently ignored, and all problems are treated as pass-fail.
/// unknown keys are ignored.
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct ProblemMetadata {
    pub name: String,

    #[serde(default)]
    pub limits: Limits,
}

impl ProblemMetadata {
    pub fn from_yaml_file(path: impl AsRef<Path>) -> Result<Self, Box<dyn std::error::Error>> {
        let contents = read_to_string(path)?;
        Ok(yaml_serde::from_str(&contents)?)
    }

    pub fn from_yaml_str(contents: &str) -> Result<Self, yaml_serde::Error> {
        yaml_serde::from_str(contents)
    }

    pub fn to_yaml_str(&self) -> Result<String, yaml_serde::Error> {
        yaml_serde::to_string(self)
    }
}

/// checks the output file against the solution file.
/// returns true if output file passes, false if it fails (WA)
pub fn diff_files(output: &Path, solution: &Path) -> Result<bool, Box<dyn std::error::Error>> {
    let output_contents = read_to_string(output)?;
    let solution_contents = read_to_string(solution)?;
    Ok(output_contents == solution_contents)
}
