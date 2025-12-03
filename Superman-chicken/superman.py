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

    Time Complexity: O(n) because each index enters and leaves the sliding window
    at most once.
    Memory Complexity: O(1) extra space beyond the input list.
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
    header = sys.stdin.readline().split()
    if len(header) < 2:
        return

    n, k = map(int, header[:2])
    if n <= 0:
        print(0)
        return

    positions: List[int] = []
    for line in sys.stdin:
        positions.extend(map(int, line.split()))
        if len(positions) >= n:
            positions = positions[:n]
            break

    if len(positions) < n:
        return

    print(max_chickens_under_roof(positions, k))


if __name__ == "__main__":
    solve()
