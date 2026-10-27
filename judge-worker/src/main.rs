use judge_worker::handlers::{AppState, submission_handler};
use std::env;

use axum::{Router, routing::{post}};
use azure_core::http::Url;
use azure_storage_blob::BlobContainerClient;
use clap::Parser;
use judge_worker::language_config;
use std::path::PathBuf;
use std::sync::Arc;

#[derive(Parser)]
struct Args {
    #[arg(short, long)]
    config: PathBuf,
}

// TODO: file caching based on last access
// TODO: cpu pinning
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    dotenvy::dotenv().ok();
    let args = Args::parse();
    let configs = language_config::load_language_configs(&args.config)?;
    let azure_client = connect_to_azure()?;

    let state = Arc::new(AppState {configs, azure_client});
    let app = Router::new()
        .route("/submissions", post(submission_handler))
        .with_state(state);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    println!("Starting server...");
    axum::serve(listener, app).await.unwrap();
    Ok(())
}

fn connect_to_azure() -> Result<BlobContainerClient, Box<dyn std::error::Error>> {
    let account = env::var("AZURE_ACCOUNT")?;
    let container = env::var("AZURE_CONTAINER")?;
    let sas = env::var("AZURE_SAS")?;

    let formmated = format!(
        "https://{}.blob.core.windows.net/{}?{}",
        account, container, sas
    );
    let service_url = Url::parse(&formmated)?;
    let client = BlobContainerClient::new(service_url, None, None)?;
    Ok(client)
}
