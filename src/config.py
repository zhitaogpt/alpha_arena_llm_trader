"""
Configuration loader for Alpha Arena LLM Trader.

This module loads the top‑level `config.yaml` file and merges it
with environment variables.  Environment variables should be
defined in a `.env` file (see `.env.example`) and are loaded via
`python‑dotenv`.  Secrets such as API keys are never committed
to source control.
"""

from __future__ import annotations

import os
import pathlib
from typing import Any, Dict

import yaml
from dotenv import load_dotenv


def load_config() -> Dict[str, Any]:
    """Load the project configuration from YAML and environment variables.

    Returns a nested dictionary containing all configuration values.
    The YAML file defines defaults for models, exchange and risk
    settings.  Environment variables are loaded from `.env` and may
    override sensitive fields (e.g. API keys).
    """
    # Load environment variables from `.env` file in project root
    load_dotenv()

    project_root = pathlib.Path(__file__).resolve().parents[1]
    config_file = project_root / "config.yaml"
    with config_file.open("r", encoding="utf-8") as fh:
        config: Dict[str, Any] = yaml.safe_load(fh)

    # Populate API keys from environment variables.  Keys are
    # optional; missing keys are left as None to be handled by
    # downstream code.
    for provider in config.get("llm_providers", {}).values():
        name = provider.get("model")
        if name:
            env_key = f"{name.upper()}_API_KEY"
            api_key = os.getenv(env_key)
            if api_key:
                provider["api_key"] = api_key

    # Exchange API keys
    if "exchange" in config:
        config["exchange"]["api_key"] = os.getenv("EXCHANGE_API_KEY")
        config["exchange"]["secret"] = os.getenv("EXCHANGE_SECRET")
        config["exchange"]["password"] = os.getenv("EXCHANGE_PASSWORD")

    return config
