# Boss Baby's Revenge

Given a day-long sequence of kid shots (`S`) and Boss Baby revenge shots (`R`), we must confirm two rules:

1. Boss Baby never fires before the kids have shot at least once that day.
2. Every kid shot ultimately receives at least one revenge shot, though he may keep firing after the kids are done.

The output is `Good boy` if both rules hold, otherwise `Bad boy`.

## Approach

1. Count how many kid shots still lie ahead in the timeline. This lets us know whether we are mid-day or already past the final shot.
2. Traverse the sequence once while tracking how many shots remain unrevenged.
3. When we read `S`, we increase both the outstanding counter and mark that another shot has been seen (and decrement the "remaining shots" counter because this shot is no longer in the future).
4. When we read `R`:
   - If we have never seen an `S`, Boss Baby initiated the conflict → `Bad boy`.
   - If there are outstanding shots, consume one.
   - If there are no outstanding shots but future kid shots exist, Boss Baby is shooting too early → `Bad boy`.
   - Otherwise, the kids are finished, so extra end-of-day revenge is allowed.
5. After the scan, any remaining outstanding shots mean somebody was never revenged → `Bad boy`.

This single pass uses O(1) auxiliary space and runs in O(n) time for n events.

## Running the solver

```bash
python bossbaby.py <<<'SRSSRRR'
```

The command above prints `Good boy`.

## Tests

Manual spot checks (feel free to run them yourself):

```bash
# Provided samples
python bossbaby.py <<<'SRSSRRR'   # Good boy
python bossbaby.py <<<'RSSRR'     # Bad boy
python bossbaby.py <<<'SSSRRRRS'  # Bad boy
python bossbaby.py <<<'SRRSSR'    # Bad boy
python bossbaby.py <<<'SSRSRR'    # Good boy

# Extra edge cases
python bossbaby.py <<<'SRRR'      # Good boy
python bossbaby.py <<<'RRR'       # Bad boy
```
