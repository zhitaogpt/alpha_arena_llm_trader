# Alpha Arena LLM Trader

This project implements an **Alpha Arena**–style trading tournament framework for cryptocurrency perpetual contracts.  It is designed to run multiple language models in parallel against the same market snapshot and select the best‑scoring decision under a unified risk management engine.  The original code was built for research and paper trading, but it can be extended to live environments with minimal changes.

## Features

* **Plug‑and‑play LLMs** – easily add new models by editing `config.yaml` and implementing a lightweight client class.
* **Consistent prompts** – all models receive the same structured market snapshot and JSON schema, inspired by the Alpha Arena competition.
* **Hard risk limits** – a sizing module ensures that no single trade blows up the account.  ATR‑based stop losses and daily drawdown limits are enforced.
* **Paper and live modes** – paper trading is supported out of the box.  Live trading uses the `ccxt` library and requires API keys.
* **Extensible market and sentiment features** – baseline technical features (momentum, ATR, funding rates, order book imbalance) and a simple Fear & Greed index stub are provided.  You can plug in your own data sources easily.

## Quick start

1. **Install dependencies**:

   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   ```

2. **Configure models and exchange** in `config.yaml`.  Provide API keys via the `.env` file for both your LLM providers and your exchange (if using live mode).

3. **Run a single decision** in paper mode:

   ```bash
   python main.py --paper --once
   ```

4. **Run continuously** (default interval 60 seconds) in paper mode:

   ```bash
   python main.py --paper
   ```

5. **Go live** (be careful!) after you have tested thoroughly:

   ```bash
   python main.py --live
   ```

## Project structure

```text
alpha_arena_llm_trader/
├── main.py                # CLI entry point
├── config.yaml            # Model/exchange settings
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── README.md              # This file
└── src/
    ├── config.py         # Configuration loader
    ├── exchanges.py      # Exchange connection helpers (ccxt)
    ├── market_data.py    # Market and order book feature extraction
    ├── sentiment.py      # External sentiment data
    ├── llm_clients.py    # Wrapper clients for various LLM endpoints
    ├── prompts.py        # Prompt templates
    ├── schemas.py        # Pydantic models for decisions
    ├── risk.py           # Position sizing and hard stops
    ├── execution.py      # Order execution and paper trading
    ├── agent.py          # Arena logic combining everything
    ├── telemetry.py      # Logging and telemetry
    └── util.py           # JSON extraction utilities
```

This codebase is a skeleton that can be built upon for your own quant research.  It intentionally separates “LLM logic” (prompts and model selection) from deterministic trading rules (market data, risk sizing, execution).  Feel free to adapt or extend any part of it.
