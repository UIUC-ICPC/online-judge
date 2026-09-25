mod language_config;

use clap::Parser;
use std::path::PathBuf;

#[derive(Parser)]
struct Args {
    path: PathBuf,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = Args::parse();
    let configs = language_config::load_language_configs(args.path)?;
    println!("{configs:#?}");
    Ok(())
}
