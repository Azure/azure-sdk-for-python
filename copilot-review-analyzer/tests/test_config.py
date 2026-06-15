"""Tests for configuration loading and validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from analyzer.config import Config, ConfigError


def _write(tmp_path: Path, text: str) -> Path:
    p = tmp_path / "config.yaml"
    p.write_text(text, encoding="utf-8")
    return p


VALID = """
repos:
  - owner/name
copilot_logins:
  - Copilot[bot]
model: gpt-4o
"""


def test_load_valid(tmp_path: Path) -> None:
    cfg = Config.load(_write(tmp_path, VALID))
    assert cfg.repos == ("owner/name",)
    assert cfg.copilot_logins == ("copilot[bot]",)  # lower-cased
    assert cfg.model == "gpt-4o"
    assert cfg.max_prs == 50
    assert "other" in cfg.vocab
    assert cfg.config_hash  # deterministic, non-empty


def test_config_hash_stable(tmp_path: Path) -> None:
    a = Config.load(_write(tmp_path, VALID))
    b = Config.load(_write(tmp_path, VALID))
    assert a.config_hash == b.config_hash


def test_missing_required_key(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="Missing required"):
        Config.load(_write(tmp_path, "repos:\n  - owner/name\nmodel: gpt-4o\n"))


def test_unknown_key(tmp_path: Path) -> None:
    text = VALID + "bogus: 1\n"
    with pytest.raises(ConfigError, match="Unknown config keys"):
        Config.load(_write(tmp_path, text))


def test_invalid_repo(tmp_path: Path) -> None:
    text = "repos:\n  - badrepo\ncopilot_logins:\n  - c[bot]\nmodel: gpt-4o\n"
    with pytest.raises(ConfigError, match="Invalid repo"):
        Config.load(_write(tmp_path, text))


def test_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="not found"):
        Config.load(tmp_path / "nope.yaml")


def test_empty_file(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="empty"):
        Config.load(_write(tmp_path, ""))


def test_bad_confidence_threshold(tmp_path: Path) -> None:
    text = VALID + "confidence_threshold: 1.5\n"
    with pytest.raises(ConfigError, match="confidence_threshold"):
        Config.load(_write(tmp_path, text))


def test_vocab_always_includes_other(tmp_path: Path) -> None:
    text = "repos:\n  - o/n\ncopilot_logins:\n  - c[bot]\nmodel: m\nvocab:\n  - security\n"
    cfg = Config.load(_write(tmp_path, text))
    assert cfg.vocab[-1] == "other"
