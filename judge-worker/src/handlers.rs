use crate::{isolate::IsolateBox, language_config};
use axum::{
    Json,
    extract::State,
    http::StatusCode,
    response::{IntoResponse, Response},
};
use azure_storage_blob::BlobContainerClient;
use std::path::PathBuf;
use std::sync::Arc;
use tokio::time::{Duration, sleep};

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

// TODO: implement downloading from blob storage
// TODO: implement basic file caching
// TODO: consider user input whatnot
#[axum_macros::debug_handler]
pub async fn submission_handler(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<SubmissionPayLoad>,
) -> Result<String, AppError> {
    let language = state
        .configs
        .get(&payload.language)
        .ok_or_else(|| anyhow::anyhow!("Unsupported language"))?;

    let blob = state.azure_client.blob_client(&payload.problem_name);
    let res = blob.download(None).await?;
    let data = res.body.collect().await?;

    // TODO: change path later later
    let path = PathBuf::from("./cache-test").join(&payload.problem_name);
    tokio::fs::write(&path, data).await?;

    let sandbox = IsolateBox::new(0, None)?;
    sandbox.run_submission(language, &payload.source, &path.as_path())?;

    // for testing purposes
    sleep(Duration::from_secs(5)).await;
    println!("Removing file from folder");
    tokio::fs::remove_file(&path).await?;

    // let box_id = match state.cores.lock().await.pop() {
    //     Some(id) => id,
    //     None => return Err(StatusCode::INTERNAL_SERVER_ERROR)
    // };
    // println!("ID {} is now taken", box_id);
    // state.cores.lock().await.push(box_id);
    // println!("ID {} is now free.", box_id);
    Ok(format!("Data returned here"))
}

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
