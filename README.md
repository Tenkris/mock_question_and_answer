## Tech Stack

- Python 3.10+ (stdlib only)
- No external services required beyond the mock transaction node used in Problem&nbsp;3

## Repository Map

| Problem                            | Folder                      | Language | Entry Point                                  | Brief Description                                                                                                  |
| ---------------------------------- | --------------------------- | -------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| 1. Superman’s Chicken Rescue       | `Superman-chicken/`         | Python   | `superman.py`                                | Sliding-window algorithm that maximizes the number of chickens covered by a length-`k` roof segment on a 1-D line. |
| 2. Boss Baby’s Revenge             | `bossbaby/`                 | Python   | `bossbaby.py`                                | One-pass validator that enforces revenge ordering rules between kid shots (`S`) and Boss Baby shots (`R`).         |
| 3. Transaction Broadcasting Client | `Transaction-Broadcasting/` | Python   | `transaction_client.py` / `example_usage.py` | HTTP client module that broadcasts transactions, polls their status, and documents integration strategies.         |

## Running the Solutions

1. **Superman’s Chicken Rescue**

   ```bash
   python Superman-chicken/superman.py <<'EOF'
   5 5
   2 5 10 12 15
   EOF
   ```

   See `Superman-chicken/readme.md` for algorithm notes and additional tests.

2. **Boss Baby’s Revenge**

   ```bash
   python bossbaby/bossbaby.py <<<'SRSSRRR'
   ```

   More examples and the reasoning behind the state machine live in `bossbaby/readme.md`.

3. **Transaction Broadcasting Client**
   ```bash
   cd Transaction-Broadcasting
   python example_usage.py --symbol ETH --price 4500
   ```
   The module (`transaction_client.py`) exposes `TransactionClient` for reuse, while `README.md` in the same folder documents error handling, polling strategy, and design trade-offs.

## Design Highlights

- Favor linear-time, constant-space algorithms for the discrete problems to guarantee performance on large inputs.
- Keep modules dependency-free so they embed cleanly in other systems or grading harnesses.
- Document assumptions, limitations, and status-handling guidance directly within each problem’s folder to streamline evaluation.

## Testing

- Problems 1 & 2: Exercised via command-line inputs in the respective readme instructions.
- Problem 3: Use `example_usage.py` for manual verification against the provided mock HTTP node; extend with mocks for automated testing as needed.
