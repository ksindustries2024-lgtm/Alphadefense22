# ============================================================
# script13_5_generators.py
# AlphaDefense Learning Track — Generators & yield
# Author: km | DAV Jalandhar | AI Engineering Sem 4
# ============================================================
#
# CORE PROBLEM THIS SOLVES:
# A normal function dies completely when it hits `return` — every
# local variable and its execution position is destroyed. Calling
# it again starts fresh from line 1, with zero memory of the last call.
# This is fine for small computations, but breaks down at scale:
# if you build an entire result as a list before returning it,
# ALL of it must sit in RAM at once.
#
# A generator can PAUSE mid-execution, hand back one value, and
# stay alive — remembering exactly where it left off — so the next
# call resumes from that exact point instead of starting over.
# ============================================================

# TASK 1: Basic generator — pause and resume demonstration
# Pattern: yield freezes state instead of destroying it (unlike return)

def transaction_stream():
    print("the first transaction")
    yield 100          # pause point 1 — function freezes here, state preserved
    print("the second transaction")
    yield 250          # pause point 2
    print("the third transaction")
    yield 75           # pause point 3
    print("Stream done")   # runs on the 4th next() call, then StopIteration fires


# Calling transaction_stream() does NOT run any code inside it.
# It only creates a generator object — paused before line 1.
gen = transaction_stream()

print("call 1 returned:", next(gen))   # runs to first yield, returns 100
print("call 2 returned:", next(gen))   # resumes after yield 100, returns 250
print("call 3 returned:", next(gen))   # resumes after yield 250, returns 75

# A 4th next(gen) call here would run "Stream done", hit the end of the
# function body, and raise StopIteration — the same exhaustion signal
# every iterator uses. A `for` loop catches this automatically; manual
# next() calls do not.

# ============================================================
# KEY DISTINCTIONS
#
# return                              | yield
# ------------------------------------|------------------------------------
# Destroys all local state            | Freezes local state (bookmark)
# Function cannot be resumed          | Resumes exactly where it paused
# Calling again = fresh execution     | next() resumes from the yield point
# Produces the value once             | Produces one value per next() call
#
# Precision point: what's preserved between next() calls is the
# function's EXECUTION POSITION and LOCAL VARIABLES — not a copy of
# previously yielded values. Once a value is yielded and consumed,
# it's gone; the generator does not retain a history of outputs.
# ============================================================

# ============================================================
# WHY THIS MATTERS FOR ALPHADEFENSE
#
# IEEE-CIS fraud dataset: ~590,000 transaction rows.
# Loading all of them into a list first (return [all rows]) forces
# Python to hold every row in RAM simultaneously — a large, avoidable
# memory spike on a laptop-class machine.
#
# A generator-based loader produces ONE row at a time. The row gets
# processed (scored, checked, whatever the pipeline step needs) and
# discarded before the next row is even generated. Memory usage stays
# FLAT and CONSTANT regardless of dataset size — 500 rows or 590,000.
# ============================================================

# ============================================================
# CRITICAL LIMITATION — single-use, forward-only
#
# A generator can only move forward. No rewind, no restart on the
# same generator object. Once exhausted, it stays exhausted.
#
# This matters for a two-pass fraud pipeline (e.g. one pass to
# compute mean/std for scoring thresholds, a second pass to actually
# flag anomalies using those stats). Real options:
#   1. Create a FRESH generator by calling the function again.
#   2. If the dataset is small enough, materialize once with
#      list(transaction_stream()) and loop over the list repeatedly
#      — trades away the memory benefit for reusability.
#   3. itertools.tee() to split one generator into independent ones
#      — more advanced, rarely needed at this stage.
#
# AlphaDefense pattern: first pass computes and stores only small
# aggregate numbers (mean, std) — not raw rows — then a second,
# freshly created generator handles the actual scoring pass. Memory
# stays flat on both passes.
# ============================================================

# Scope note: send(), yield from, and coroutine-style generators were
# deliberately excluded here — not needed for AlphaDefense's data-
# loading and streaming use case. Revisit only if a future phase
# requires bidirectional generator communication.
