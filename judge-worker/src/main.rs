use judge_worker::isolate::IsolateBox;
use judge_worker::language_config;

use clap::Parser;
use std::path::PathBuf;

#[derive(Parser)]
struct Args {
    #[arg(short, long)]
    config: PathBuf,

    #[arg(short, long)]
    language: String,

    #[arg(short, long)]
    source: PathBuf,

    #[arg(short, long)]
    problem: PathBuf,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = Args::parse();

    let configs = language_config::load_language_configs(&args.config)?;
    let language = configs
        .get(&args.language)
        .ok_or_else(|| format!("unknown language: {}", args.language))?;

    let sandbox = IsolateBox::new(0, None)?;
    // TODO: figure out better representation for problems
    sandbox.run_submission(language, &args.source, &args.problem)?;
    Ok(())
}
