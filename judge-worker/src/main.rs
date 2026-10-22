mod isolate;
mod language_config;

use axum::{
    Json, 
    Router, 
    http::{StatusCode}, 
    routing::{post,get},
    extract::State,
};
use clap::Parser;
use isolate::IsolateBox;
use std::{path::PathBuf};
use axum::extract::rejection::JsonRejection;


#[derive(Parser)]
struct Args {
    #[arg(short, long)]
    config: PathBuf,
}

#[derive(serde::Deserialize)]
struct PayLoad {
    language: String,
    source: String
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

    let sandbox = IsolateBox::new(0, None)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
 
    sandbox.run_submission(language, &payload.source)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    Ok(format!("Data would go here"))
}