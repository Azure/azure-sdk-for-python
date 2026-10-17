// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use std::sync::{Arc, Mutex};

use azure_core::http::{
    headers::Headers, AsyncRawResponse, Body, HttpClient, Request, RetryOptions, StatusCode,
    Transport, Url,
};
use azure_storage_blob::{BlobClient, BlobClientOptions};

#[derive(Clone, Debug)]
pub(crate) struct RecordedRequest {
    pub method: String,
    pub url: Url,
    pub headers: Headers,
    pub body: Vec<u8>,
}

type Handler = dyn Fn(&RecordedRequest) -> azure_core::Result<AsyncRawResponse> + Send + Sync;

pub(crate) struct MockHttpClient {
    requests: Mutex<Vec<RecordedRequest>>,
    handler: Box<Handler>,
}

impl std::fmt::Debug for MockHttpClient {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("MockHttpClient").finish_non_exhaustive()
    }
}

impl MockHttpClient {
    pub fn new(
        handler: impl Fn(&RecordedRequest) -> azure_core::Result<AsyncRawResponse>
            + Send
            + Sync
            + 'static,
    ) -> Arc<Self> {
        Arc::new(Self {
            requests: Mutex::new(Vec::new()),
            handler: Box::new(handler),
        })
    }

    pub fn requests(&self) -> Vec<RecordedRequest> {
        self.requests.lock().unwrap().clone()
    }

    pub fn options(self: &Arc<Self>) -> BlobClientOptions {
        let mut options = BlobClientOptions::default();
        options.client_options.transport = Some(Transport::new(self.clone()));
        options.client_options.retry = RetryOptions::none();
        options
    }

    pub fn client(self: &Arc<Self>) -> BlobClient {
        crate::build_blob_client_with_options(
            "https://account.blob.core.windows.net/container/blob",
            None,
            None,
            self.options(),
        )
        .unwrap()
    }
}

#[async_trait::async_trait]
impl HttpClient for MockHttpClient {
    async fn execute_request(&self, request: &Request) -> azure_core::Result<AsyncRawResponse> {
        let body = match request.body() {
            Body::Bytes(bytes) => bytes.to_vec(),
            _ => panic!("Unexpected streaming body in a bytes-only transfer test"),
        };
        let recorded = RecordedRequest {
            method: request.method().to_string(),
            url: request.url().clone(),
            headers: request.headers().clone(),
            body,
        };
        self.requests.lock().unwrap().push(recorded.clone());
        (self.handler)(&recorded)
    }
}

pub(crate) fn response(
    status: StatusCode,
    headers: &[(&str, &str)],
    body: impl Into<azure_core::Bytes>,
) -> azure_core::Result<AsyncRawResponse> {
    let mut result = Headers::new();
    for (name, value) in headers {
        result.insert((*name).to_string(), (*value).to_string());
    }
    Ok(AsyncRawResponse::from_bytes(status, result, body))
}
