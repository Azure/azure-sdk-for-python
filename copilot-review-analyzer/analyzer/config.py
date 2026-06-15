"""Configuration loading and validation.

Loads ``config.yaml`` into a frozen, typed dataclass with explicit validation so
every stage references a single validated source of truth.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

_REQUIRED_KEYS = {"repos", "copilot_logins", "model"}

_ALLOWED_KEYS = _REQUIRED_KEYS | {
    "max_prs",
    "line_fuzz",
    "vocab",
    "confidence_threshold",
    "max_unjudged_ratio",
    "judge_batch_size",
}

_DEFAULT_VOCAB = (
    "null-handling",
    "error-handling",
    "test-coverage",
    "security",
    "api-design",
    "concurrency",
    "perf",
    "docs",
    "other",
)


class ConfigError(ValueError):
    """Raised when configuration is missing required fields or has invalid values."""


@dataclass(frozen=True)
class Config:
    """Validated analyzer configuration."""

    repos: tuple[str, ...]
    copilot_logins: tuple[str, ...]
    model: str
    max_prs: int = 50
    line_fuzz: int = 2
    vocab: tuple[str, ...] = field(default=_DEFAULT_VOCAB)
    confidence_threshold: float = 0.5
    max_unjudged_ratio: float = 0.5
    judge_batch_size: int = 10

    @property
    def config_hash(self) -> str:
        """Stable hash of the config for run reproducibility."""
        payload = {
            "repos": list(self.repos),
            "copilot_logins": list(self.copilot_logins),
            "model": self.model,
            "max_prs": self.max_prs,
            "line_fuzz": self.line_fuzz,
            "vocab": list(self.vocab),
            "confidence_threshold": self.confidence_threshold,
            "max_unjudged_ratio": self.max_unjudged_ratio,
            "judge_batch_size": self.judge_batch_size,
        }
        blob = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()[:16]

    @classmethod
    def load(cls, path: str | Path) -> Config:
        """Load and validate configuration from a YAML file."""
        p = Path(path)
        if not p.exists():
            raise ConfigError(f"Config file not found: {p}")
        try:
            raw = yaml.safe_load(p.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise ConfigError(f"Invalid YAML in {p}: {exc}") from exc
        if raw is None:
            raise ConfigError(f"Config file is empty: {p}")
        if not isinstance(raw, dict):
            raise ConfigError(f"Config root must be a mapping, got {type(raw).__name__}")
        return cls.from_dict(raw)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Config:
        """Validate a raw mapping and build a :class:`Config`."""
        unknown = set(raw) - _ALLOWED_KEYS
        if unknown:
            raise ConfigError(f"Unknown config keys: {sorted(unknown)}")
        missing = _REQUIRED_KEYS - set(raw)
        if missing:
            raise ConfigError(f"Missing required config keys: {sorted(missing)}")

        repos = _str_tuple(raw["repos"], "repos")
        if not repos:
            raise ConfigError("'repos' must contain at least one entry")
        for repo in repos:
            if repo.count("/") != 1 or repo.startswith("/") or repo.endswith("/"):
                raise ConfigError(f"Invalid repo '{repo}'; expected 'owner/name'")

        copilot_logins = tuple(
            s.lower() for s in _str_tuple(raw["copilot_logins"], "copilot_logins")
        )
        if not copilot_logins:
            raise ConfigError("'copilot_logins' must contain at least one entry")

        model = raw["model"]
        if not isinstance(model, str) or not model.strip():
            raise ConfigError("'model' must be a non-empty string")

        max_prs = _positive_int(raw.get("max_prs", 50), "max_prs")
        line_fuzz = _non_negative_int(raw.get("line_fuzz", 2), "line_fuzz")
        judge_batch_size = _positive_int(raw.get("judge_batch_size", 10), "judge_batch_size")

        vocab = tuple(_str_tuple(raw["vocab"], "vocab")) if "vocab" in raw else _DEFAULT_VOCAB
        if "other" not in vocab:
            vocab = (*vocab, "other")

        confidence_threshold = _unit_float(
            raw.get("confidence_threshold", 0.5), "confidence_threshold"
        )
        max_unjudged_ratio = _unit_float(raw.get("max_unjudged_ratio", 0.5), "max_unjudged_ratio")

        return cls(
            repos=repos,
            copilot_logins=copilot_logins,
            model=model.strip(),
            max_prs=max_prs,
            line_fuzz=line_fuzz,
            vocab=vocab,
            confidence_threshold=confidence_threshold,
            max_unjudged_ratio=max_unjudged_ratio,
            judge_batch_size=judge_batch_size,
        )


def _str_tuple(value: Any, key: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise ConfigError(f"'{key}' must be a list of strings")
    return tuple(v.strip() for v in value if v.strip())


def _positive_int(value: Any, key: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ConfigError(f"'{key}' must be a positive integer")
    return value


def _non_negative_int(value: Any, key: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ConfigError(f"'{key}' must be a non-negative integer")
    return value


def _unit_float(value: Any, key: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigError(f"'{key}' must be a number in [0, 1]")
    f = float(value)
    if not 0.0 <= f <= 1.0:
        raise ConfigError(f"'{key}' must be within [0, 1]")
    return f
