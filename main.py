"""
Command‑line interface for Alpha Arena LLM Trader.

Run this script with optional flags to control the mode:

```
python main.py --paper        # run continuously in paper mode
python main.py --paper --once # run a single iteration in paper mode
python main.py --live         # run continuously in live mode (caution)
```
"""

from __future__ import annotations

import argparse
import logging

from src.config import load_config
from src.agent import ArenaAgent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Alpha Arena LLM Trader")
    parser.add_argument("--paper", action="store_true", help="Run in paper trading mode (default)")
    parser.add_argument("--live", action="store_true", help="Run in live trading mode (danger)")
    parser.add_argument("--once", action="store_true", help="Run a single iteration and exit")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    # Set up basic logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    config = load_config()
    paper = not args.live
    agent = ArenaAgent(config=config, paper=paper)
    if args.once:
        agent.run_once()
    else:
        agent.run()


if __name__ == "__main__":
    main()
