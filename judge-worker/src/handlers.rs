use crate::{
    isolate::{IsolateBox, SubmissionResult},
    language_config,
};
use axum::{
    Json,
    extract::State,
    http::StatusCode,
    response::{IntoResponse, Response},
};
use azure_storage_blob::BlobContainerClient;
use std::sync::Arc;

pub struct AppError(anyhow::Error);

pub struct AppState {
    pub configs: language_config::LanguageConfigs,
    pub azure_client: BlobContainerClient,
}

#[derive(serde::Deserialize)]
pub struct SubmissionPayLoad {
    language: String,
    source: String,
    problem_name: String,
}

#[axum_macros::debug_handler]
pub async fn submission_handler(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<SubmissionPayLoad>,
) -> Result<Json<SubmissionResult>, AppError> {
    let language = state
        .configs
        .get(&payload.language)
        .ok_or_else(|| anyhow::anyhow!("Unsupported language"))?;

    let blob = state.azure_client.blob_client(&payload.problem_name);
    println!("Downloading problem {}...", &payload.problem_name);
    let res = blob.download(None).await?;
    let problem_data = res.body.collect().await?;

    let sandbox = IsolateBox::new(0, None)?;
    println!("Attempting to run sandboxed code...");
    let result = sandbox.run_submission(language, &payload.source, &problem_data)?;

    Ok(Json(result))
}

// TODO: fix the error handling
impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            format!("Something went wrong: {}", self.0),
        )
            .into_response()
    }
}

impl<E> From<E> for AppError
where
    E: Into<anyhow::Error>,
{
    fn from(err: E) -> Self {
        Self(err.into())
    }
}
