"""
Solve the "Superman's Chicken Rescue" problem.

Given sorted chicken positions on a number line and the length of the roof
Superman can carry, determine the maximum number of chickens that can be
covered by a roof segment of length k (covering interval [p, p + k)).
"""

from __future__ import annotations

import sys
from typing import List


def max_chickens_under_roof(positions: List[int], roof_length: int) -> int:
    """
    Return the maximum number of chickens covered by a roof of length roof_length.

    Since positions are sorted, we can slide a window and keep shrinking from the
    left whenever the current window no longer fits inside an interval of size k.
    """

    if roof_length <= 0:
        return 0

    best = 0
    left = 0

    for right, pos in enumerate(positions):
        # Shrink window until it fits inside an interval of length roof_length.
        while pos - positions[left] >= roof_length:
            left += 1
        best = max(best, right - left + 1)

    return best


def solve() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    if not data:
        return

    outputs = []
    idx = 0
    total = len(data)

    while idx + 2 <= total:
        n = data[idx]
        k = data[idx + 1]
        idx += 2

        if n < 0 or idx + n > total:
            # Invalid or incomplete input; stop processing further.
            break

        positions = data[idx : idx + n]
        idx += n

        outputs.append(str(max_chickens_under_roof(positions, k)))

    sys.stdout.write("\n".join(outputs))


if __name__ == "__main__":
    solve()
