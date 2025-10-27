"""
Core arena logic for Alpha Arena LLM Trader.

This module brings together the other modules: it builds
prompts, calls each configured LLM, validates the responses,
calculates position sizing, executes trades and logs the
results.  The agent can run once for a single decision or run
continuously in a loop.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Tuple

from .config import load_config
from .llm_clients import build_llm_clients
from .market_data import compute_features
from .sentiment import get_sentiment_features
from .prompts import build_messages
from .schemas import decision_schema, parse_decision, Decision
from .util import extract_json_from_text
from .risk import size_position
from .execution import execute_trade
from .telemetry import log_trade
from .exchanges import init_exchange


class ArenaAgent:
    """Combines LLMs, market data, risk, execution and logging."""

    def __init__(self, config: Dict[str, Any], paper: bool = True):
        self.config = config
        self.paper = paper
        self.exchange = init_exchange(config["exchange"], paper=paper)
        self.llms = build_llm_clients(config)
        self.schema = decision_schema()
        self.equity = 10000.0  # default equity for sizing; replace with account balance retrieval

    def fetch_snapshot(self, symbol: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Fetch market and sentiment data for a symbol."""
        features = compute_features(self.exchange, symbol, self.config["exchange"]["timeframe"])
        sentiment = get_sentiment_features() if self.config.get("sentiment", {}).get("use_fear_and_greed", False) else {}
        return features, sentiment

    def run_once(self) -> None:
        """Execute a single iteration: call each LLM, pick a trade and execute it."""
        symbols = self.config["exchange"].get("symbols", [])
        if not symbols:
            logging.error("No symbols configured for trading")
            return
        # For simplicity, trade only the first symbol
        symbol = symbols[0]
        features, sentiment = self.fetch_snapshot(symbol)
        decisions: List[Tuple[str, Decision, float, float, int]] = []

        # Query each model
        for name, client in self.llms.items():
            messages = build_messages(features, sentiment, self.schema)
            try:
                response = client.chat(messages)
                # Extract the content; handle different response shapes
                if "choices" in response and response["choices"]:
                    content = response["choices"][0]["message"].get("content", "")
                else:
                    content = ""
                data = extract_json_from_text(content)
                decision = parse_decision(data)
            except Exception as exc:
                logging.error("Model %s returned invalid response: %s", name, exc)
                continue
            # Size the position
            amount, stop_price, leverage = size_position(
                decision,
                price=features["price"],
                atr=features["atr_14"],
                equity=self.equity,
                risk_cfg=self.config.get("risk", {}),
            )
            decisions.append((name, decision, amount, stop_price, leverage))

        if not decisions:
            logging.warning("No valid decisions were generated")
            return
        # Choose the decision with highest confidence (fallback to first)
        decisions.sort(key=lambda x: (x[1].confidence or 0.0), reverse=True)
        chosen_name, chosen_decision, amount, stop_price, leverage = decisions[0]
        # Execute trade
        result = execute_trade(
            self.exchange,
            decision=chosen_decision,
            amount=amount,
            stop_price=stop_price,
            leverage=leverage,
            paper=self.paper,
        )
        # Log
        log_file = self.config.get("logging", {}).get("log_file", "trades.jsonl")
        result.update({
            "model": chosen_name,
            "decision": chosen_decision.dict(),
        })
        log_trade(result, log_file)
        logging.info("Executed trade from %s: %s", chosen_name, result)

    def run(self) -> None:
        """Run the agent loop continuously."""
        interval = self.config["exchange"].get("poll_interval", 60)
        while True:
            self.run_once()
            time.sleep(interval)
