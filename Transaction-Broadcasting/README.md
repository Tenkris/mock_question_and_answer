# Transaction Broadcasting and Monitoring Client

Reliable, dependency-free Python client for broadcasting price transactions to the mock node and monitoring their lifecycle until a terminal status is reached.

## Features
- Broadcasts signed payloads via `POST /broadcast` and polls `GET /check/<tx_hash>` until finality.
- Built-in retries with exponential backoff, bounded per-request timeouts, and structured exceptions.
- Handles both JSON and plaintext responses, making it resilient to server inconsistencies.
- Lightweight standard-library implementation that can be embedded into other Python services.

```
++ Caller +++             + Mock Node +
     | POST /broadcast (symbol, price, ts) |
     |----------------------------------->|
     |<-----------------------------------| tx_hash
loop | GET /check/<hash>                  |
     |----------------------------------->|
     |<-----------------------------------| status (PENDING/…)
     |    stop when CONFIRMED/FAILED/DNE  |
```

## Repository Layout
| Path | Description |
| --- | --- |
| `transaction_client.py` | Core client module (`TransactionClient`, enums, exceptions). |
| `example_usage.py` | Executable sample showing how to broadcast and wait for finality. |

## Quick Start
```bash
cd Transaction-Broadcasting
python example_usage.py --symbol ETH --price 4500
```
Optional flags: `--timestamp`, `--timeout`, `--max-retries`, `--backoff`, `--poll-interval`, and `--max-wait`.

## Embedding the Client
```python
from transaction_client import TransactionClient, TransactionTimeout

client = TransactionClient(timeout=3.0, max_retries=2)
payload = {"symbol": "BTC", "price": 100_000, "timestamp": 1710000000}

result = client.broadcast_transaction(**payload)
print("tx hash:", result.tx_hash)

try:
    status = client.wait_for_finality(result.tx_hash, poll_interval=1.0, max_wait=30.0)
    print("final status:", status.value)
except TransactionTimeout:
    # escalate, enqueue retry, or alert depending on your system's needs
    ...
```

### Status Handling Strategy
- `CONFIRMED`: safely commit dependent business logic (e.g., unlock funds, notify user).
- `FAILED`: treat as permanently rejected; inspect logs/metrics, optionally rebroadcast with fixes.
- `PENDING`: continue polling (client already handles this with jitterless intervals, configurable via `poll_interval`).
- `DNE`: indicates an invalid or expired hash; upstream services should reconcile (possible inconsistency or double-send).
- Timeout (client-side): transaction remained non-terminal beyond `max_wait`. Escalate or reschedule based on your SLA.

## Design Decisions, Trade-offs, and Assumptions
1. **Standard-library HTTP stack** – Using `urllib` avoids extra dependencies and simplifies deployment. The trade-off is less ergonomic APIs compared to `requests`, so helper methods abstract repetitive boilerplate.
2. **Exponential backoff retries** – Retrying only on transient failures (network errors and 5xx) smooths over brief outages. Client errors (4xx except 429) fail fast to surface integration bugs instead of hiding them behind retries.
3. **Explicit polling contract** – The client exposes `wait_for_finality` and `broadcast_and_wait` instead of an asynchronous callback model. This keeps the module composable: callers can run it in worker threads, tasks, or orchestrators of their choice.
4. **Status normalization** – The service documentation mixes plaintext and JSON responses. Parsing logic accepts either format to stay robust against upstream changes.
5. **Observability hooks** – An optional `on_status` callback allows the host application to plug in logging/metrics without modifying the module.
6. **Assumptions** – Timestamps and prices fit into unsigned 64-bit integers; clock skew is acceptable for the downstream node; callers provide idempotency at a higher layer if required.

## Error Handling
- `TransactionError`: base exception wrapping network/HTTP errors or malformed responses.
- `TransactionTimeout`: raised when `wait_for_finality` exceeds `max_wait`.

Wrap calls in try/except blocks to map failures to your retry/alerting systems.

## Testing Ideas
- Run `example_usage.py` with realistic inputs and observe console status updates.
- Mock `_make_request` in unit tests to simulate each status and ensure `wait_for_finality` returns or raises as expected.
