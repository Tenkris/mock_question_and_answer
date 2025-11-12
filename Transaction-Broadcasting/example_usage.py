"""
Example script that broadcasts a transaction and waits for a final status.

Run:
    python example_usage.py --symbol ETH --price 4500
"""
from __future__ import annotations

import argparse
import sys
import time

from transaction_client import TransactionClient, TransactionTimeout, TransactionError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Broadcast a transaction and monitor its status.")
    parser.add_argument("--symbol", required=True, help="Asset symbol, e.g., BTC")
    parser.add_argument("--price", required=True, type=int, help="Quote price (uint64 on the node).")
    parser.add_argument(
        "--timestamp",
        type=int,
        default=None,
        help="Optional unix timestamp. Defaults to current time if omitted.",
    )
    parser.add_argument("--timeout", type=float, default=5.0, help="Per-request timeout (s).")
    parser.add_argument("--max-retries", type=int, default=3, help="Retry attempts on transient failures.")
    parser.add_argument("--backoff", type=float, default=0.5, help="Initial backoff delay in seconds.")
    parser.add_argument("--poll-interval", type=float, default=2.0, help="Seconds between status checks.")
    parser.add_argument(
        "--max-wait",
        type=float,
        default=60.0,
        help="Maximum time to wait for a terminal status before exiting with an error.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    timestamp = args.timestamp or int(time.time())
    client = TransactionClient(
        timeout=args.timeout,
        max_retries=args.max_retries,
        backoff_factor=args.backoff,
    )

    print(f"Broadcasting {args.symbol} @ {args.price} (timestamp={timestamp})")

    try:
        result, status = client.broadcast_and_wait(
            args.symbol,
            args.price,
            timestamp,
            poll_interval=args.poll_interval,
            max_wait=args.max_wait,
            on_status=lambda s: print(f"[{time.strftime('%X')}] status -> {s.value}"),
        )
    except TransactionTimeout as exc:
        print(f"Timed out while waiting for confirmation: {exc}", file=sys.stderr)
        return 1
    except TransactionError as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        return 1

    print(f"Transaction {result.tx_hash} finalized with status: {status.value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
