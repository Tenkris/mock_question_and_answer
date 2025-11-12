# Superman's Chicken Rescue

Superman has to cover as many chickens as possible on a 1-D number line with a roof segment of length `k`, covering chickens located in the half-open interval `[p, p + k)`. Chicken positions are provided already sorted.

## Approach

The optimal strategy is a classic sliding-window / two-pointer technique:

1. Start both pointers (`left`, `right`) at the first chicken.
2. Expand `right` while the current interval still fits inside length `k`.
3. Whenever `positions[right] - positions[left] >= k`, increment `left` to shrink the window until it fits again.
4. Track the largest window size encountered; that is the maximum number of chickens that fit beneath one roof segment.

Because the positions are sorted, each pointer moves at most `n` times, so the algorithm is linear.

### Correctness Sketch

- The window `[left, right]` always represents chickens that can be covered by a single roof segment.
- If adding a new chicken violates the length constraint, moving `left` forward is the only way to restore feasibility while keeping `right` fixed.
- Every feasible set of consecutive chickens appears as some window during this process, so the recorded maximum window size equals the optimal answer.

### Complexity

- **Time:** `O(n)` per test case (each index advances at most once).
- **Space:** `O(1)` auxiliary beyond the input list of positions.

## Usage

```bash
python3 superman.py <<'EOF'
5 5
2 5 10 12 15
EOF
# -> 2
```

You can concatenate multiple test cases in the same input stream; one answer is printed per line.

## Testing

The following checks were run from the project root:

```bash
python3 Superman-chicken/superman.py <<'EOF'
5 5
2 5 10 12 15
EOF

python3 Superman-chicken/superman.py <<'EOF'
6 10
1 11 30 34 35 37
EOF

python3 Superman-chicken/superman.py <<'EOF'
5 5
2 5 10 12 15
6 10
1 11 30 34 35 37
EOF
```

These include the samples from the prompt and a chained multi-case input to verify robustness.
