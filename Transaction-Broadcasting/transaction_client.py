"""
Transaction broadcasting client with polling-based status monitoring.

The module exposes the TransactionClient class that can be embedded into other
applications to broadcast price transactions to the mock node and wait for a
final status. Only stdlib modules are used to avoid external dependencies.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, Optional


class TransactionStatus(str, Enum):
    """Known lifecycle states returned by the remote service."""

    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"
    PENDING = "PENDING"
    DNE = "DNE"


@dataclass(frozen=True)
class BroadcastResult:
    """Return type for broadcast calls."""

    tx_hash: str
    payload: Dict[str, int | str]


class TransactionError(RuntimeError):
    """Base exception for failures communicating with the service."""


class TransactionTimeout(TransactionError):
    """Raised when polling for a final status takes too long."""


class TransactionClient:
    """
    HTTP client that can broadcast a transaction and monitor its status.

    Parameters
    ----------
    base_url:
        Base endpoint of the remote node (no trailing slash required).
    timeout:
        Per-request timeout in seconds.
    max_retries:
        Number of times to retry transient network/server failures.
    backoff_factor:
        Base delay (seconds) for exponential backoff between retries.
    user_agent:
        Optional identifier sent with each request.
    """

    def __init__(
        self,
        base_url: str = "https://mock-node-wgqbnxruha-as.a.run.app",
        *,
        timeout: float = 5.0,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        user_agent: str = "TransactionClient/1.0",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.broadcast_endpoint = f"{self.base_url}/broadcast"
        self.status_endpoint = f"{self.base_url}/check"
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.user_agent = user_agent

    # Public API -----------------------------------------------------------------
    def broadcast_transaction(self, symbol: str, price: int, timestamp: int) -> BroadcastResult:
        """
        Broadcasts a transaction to the remote node.

        Returns
        -------
        BroadcastResult containing the tx hash and the payload that was sent.
        """
        payload = {"symbol": symbol, "price": int(price), "timestamp": int(timestamp)}
        response = self._request_with_retries(
            method="POST",
            url=self.broadcast_endpoint,
            body=payload,
        )

        if not isinstance(response, dict) or "tx_hash" not in response:
            raise TransactionError(f"Malformed broadcast response: {response}")

        return BroadcastResult(tx_hash=str(response["tx_hash"]), payload=payload)

    def check_status(self, tx_hash: str) -> TransactionStatus:
        """
        Fetches the status of an existing transaction.
        """
        response = self._request_with_retries(
            method="GET",
            url=f"{self.status_endpoint}/{tx_hash}",
            body=None,
        )

        if isinstance(response, dict) and "tx_status" in response:
            status_value = response["tx_status"]
        else:
            status_value = response

        try:
            return TransactionStatus(str(status_value).strip())
        except ValueError as exc:
            raise TransactionError(f"Unknown transaction status: {status_value}") from exc

    def wait_for_finality(
        self,
        tx_hash: str,
        *,
        poll_interval: float = 2.0,
        max_wait: float = 60.0,
        on_status: Optional[Callable[[TransactionStatus], None]] = None,
    ) -> TransactionStatus:
        """
        Polls the remote node until the transaction reaches a terminal state.

        Parameters
        ----------
        tx_hash:
            Transaction hash returned from `broadcast_transaction`.
        poll_interval:
            Seconds between poll attempts. Lower values give quicker feedback but
            increase load on the server.
        max_wait:
            Maximum time to wait for a terminal status before raising.
        on_status:
            Optional callback invoked on every observed status (useful for logging).
        """
        start = time.monotonic()
        terminal_states = {
            TransactionStatus.CONFIRMED,
            TransactionStatus.FAILED,
            TransactionStatus.DNE,
        }

        last_status: Optional[TransactionStatus] = None

        while True:
            status = self.check_status(tx_hash)
            if status != last_status and on_status is not None:
                on_status(status)
            last_status = status

            if status in terminal_states:
                return status

            elapsed = time.monotonic() - start
            if elapsed >= max_wait:
                raise TransactionTimeout(
                    f"Transaction {tx_hash} stayed {status.value} for {elapsed:.1f}s "
                    f"(max_wait={max_wait}s)"
                )
            time.sleep(poll_interval)

    def broadcast_and_wait(
        self,
        symbol: str,
        price: int,
        timestamp: int,
        *,
        poll_interval: float = 2.0,
        max_wait: float = 60.0,
        on_status: Optional[Callable[[TransactionStatus], None]] = None,
    ) -> tuple[BroadcastResult, TransactionStatus]:
        """
        Convenience helper that broadcasts a transaction and waits for finality.
        """
        result = self.broadcast_transaction(symbol, price, timestamp)
        status = self.wait_for_finality(
            result.tx_hash,
            poll_interval=poll_interval,
            max_wait=max_wait,
            on_status=on_status,
        )
        return result, status

    # Internal helpers -----------------------------------------------------------
    def _request_with_retries(
        self,
        *,
        method: str,
        url: str,
        body: Optional[Dict[str, int | str]],
    ) -> dict | str:
        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                return self._make_request(method=method, url=url, body=body)
            except TransactionError as exc:  # type: ignore[catching-non-error]
                # For client errors (4xx except 429) there is no reason to retry.
                raise
            except Exception as exc:  # noqa: BLE001 - want to capture urllib exceptions
                last_error = exc
                if attempt >= self.max_retries:
                    break
                time.sleep(self.backoff_factor * (2**attempt))

        raise TransactionError(f"Request to {url} failed") from last_error

    def _make_request(
        self,
        *,
        method: str,
        url: str,
        body: Optional[Dict[str, int | str]],
    ) -> dict | str:
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json,text/plain;q=0.9,*/*;q=0.8",
        }

        data_bytes: Optional[bytes] = None
        if body is not None:
            data_bytes = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = urllib.request.Request(url=url, data=data_bytes, headers=headers, method=method)

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
                encoding = response.headers.get_content_charset("utf-8")
                text = raw.decode(encoding)
                content_type = response.headers.get("Content-Type", "")

                if "application/json" in content_type:
                    return json.loads(text)
                return text.strip()
        except urllib.error.HTTPError as exc:
            body_text = exc.read().decode("utf-8", errors="ignore")
            if 400 <= exc.code < 500 and exc.code != 429:
                raise TransactionError(
                    f"{method} {url} failed with {exc.code}: {body_text or exc.reason}"
                ) from exc
            raise TransactionError(
                f"{method} {url} failed with {exc.code}: {body_text or exc.reason}"
            ) from exc
        except urllib.error.URLError as exc:
            raise TransactionError(f"Network error calling {url}: {exc}") from exc
