use judge_worker::isolate::IsolateBox;
use judge_worker::language_config;

use axum::{
    Json, Router,
    extract::State,
    http::StatusCode,
    routing::{get, post},
};
use clap::Parser;
use std::path::PathBuf;

#[derive(Parser)]
struct Args {
    #[arg(short, long)]
    config: PathBuf,

    #[arg(short, long)]
    language: String,
}

#[derive(serde::Deserialize)]
struct PayLoad {
    language: String,
    source: String,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = Args::parse();
    let configs = language_config::load_language_configs(&args.config)?;

    let app = Router::new()
        .route("/", post(submission_handler))
        .with_state(configs.clone());

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
    Ok(())
}

#[axum_macros::debug_handler]
async fn submission_handler(
    State(configs): State<language_config::LanguageConfigs>,
    Json(payload): Json<PayLoad>,
) -> Result<String, StatusCode> {
    let language = configs
        .get(&payload.language)
        .ok_or_else(|| StatusCode::BAD_REQUEST)?;

    let sandbox = IsolateBox::new(0, None).map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    // TODO: figure out better representation for problems
    // sandbox.run_submission(language, &payload.source);
    Ok(format!("Data would go here"))
}
