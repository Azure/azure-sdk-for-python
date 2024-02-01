from typing import Dict, Optional

from azure.ai.generative.evaluate._utils import _get_ai_studio_url


class EvaluationResult(object):

    def __init__(self, metrics_summary: Dict[str, float], artifacts: Dict[str, str], **kwargs):
        self._metrics_summary = metrics_summary
        self._artifacts = artifacts
        self._tracking_uri: Optional[str] = kwargs.get("tracking_uri")
        self._evaluation_id: str = kwargs.get("evaluation_id", "")
        if self._tracking_uri:
            self._studio_url = _get_ai_studio_url(self._tracking_uri, self._evaluation_id)

    @property
    def metrics_summary(self) -> Dict[str, float]:
        return self._metrics_summary

    @property
    def artifacts(self) -> Dict[str, str]:
        return self._artifacts

    @property
    def tracking_uri(self) -> str:
        return self._tracking_uri  # type: ignore[return-value]

    @property
    def studio_url(self) -> str:
        return self._studio_url

    def download_evaluation_artifacts(self, path: str) -> None:
        from mlflow.artifacts import download_artifacts
        for artifact, artifact_uri in self.artifacts.items():
            download_artifacts(
                artifact_uri=artifact_uri,
                tracking_uri=self.tracking_uri,
                dst_path=path
            )
