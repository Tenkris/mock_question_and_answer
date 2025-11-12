"""
Boss Baby's Revenge solver.

Algorithm
---------
1. Count how many kid shots ('S') are still to appear in the remainder of the
   day. This lets us distinguish between mid-day and end-of-day revenge.
2. Walk through the string once while tracking how many outstanding shots still
   need to be revenged.
3. When Boss Baby tries to fire ('R') with no outstanding shots:
     * If the kids still have future shots scheduled, he would be shooting
       before the next hit, so the timeline is invalid.
     * If the kids are done for the day, we allow the extra payback.
4. At the end there must be no outstanding shots left.

The scan is linear, so the time complexity is O(n) for n events, and we only
keep a few counters which gives O(1) auxiliary space.
"""
from __future__ import annotations

import sys

GOOD = "Good boy"
BAD = "Bad boy"


def evaluate_day(sequence: str) -> str:
    """Return the verdict for one day's sequence."""

    if not sequence:
        return BAD

    normalized = ''.join(sequence.split()).upper()
    shots_remaining = normalized.count('S')
    pending = 0  # shots that have not been revenged yet
    seen_shot = False

    for ch in normalized:
        if ch == 'S':
            seen_shot = True
            pending += 1
            shots_remaining -= 1
        elif ch == 'R':
            if not seen_shot:
                return BAD
            if pending > 0:
                pending -= 1
            elif shots_remaining > 0:
                return BAD
            # else: kids are done; surplus revenge is allowed
        else:
            # Inputs are restricted to 'S' and 'R', so any other symbol
            # invalidates the sequence.
            return BAD

    return GOOD if pending == 0 else BAD


def main() -> None:
    data = sys.stdin.read()
    verdict = evaluate_day(data)
    print(verdict)


if __name__ == "__main__":
    main()
