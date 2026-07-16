# AlphaDefense — Progress Log
Cross-session/cross-account context source. Update after every gate-cleared script or phase milestone.

---

## Phase 0 — Python Scripting Track (Scripts 1–13)

| Script | Topic | Status |
|---|---|---|
| 1 | Loops / Conditionals | ✅ Gate-cleared |
| 2 | Functions | ✅ Gate-cleared |
| 3 | Default Args / *args / **kwargs | ✅ Gate-cleared |
| 4 | Function Composition | ✅ Gate-cleared |
| 5 | OOP | ✅ Gate-cleared |
| 6 | Lists / Dicts | ✅ Gate-cleared |
| 7 | CSV + Pandas Basics | ✅ Gate-cleared |
| 8 | Pandas Advanced (data leakage, fit vs transform) | ✅ Gate-cleared |
| 9 | Comprehensions | ✅ Gate-cleared |
| 10 | Decorators | ✅ Gate-cleared |
| 11 | Error Handling + Logging | ✅ Gate-cleared |
| 12 | File I/O + JSON | 🔓 Unlocked — active |
| 13 | Modules + Imports | 🔒 Locked |

---

## Script 11 — Error Handling + Logging (GATE-CLEARED)
**Date:** 2026-07-16

**Deliverable 1:** `transaction_processor.py` — `score_transaction()` handling three
distinct failure modes with separate except blocks:
- `ValueError` — amount present but not a valid number
- `KeyError` — amount field missing entirely
- `InvalidTransactionError` (custom, inherits `Exception`) — amount is a valid
  number but violates a business rule (negative), which Python has no built-in
  concept of — only domain logic can catch it
- Every except block returns explicitly to avoid falling through to code that
  assumes success (see deliberate-error trace below)
- Logging via `basicConfig` (filename, `level=INFO`, timestamped format),
  replacing print-based debugging

**Deliverable 2:** Written trace of the `UnboundLocalError` deliberate-error bug.
- Root cause: in a buggy version, `except Exception` logged the failure but had
  no `return`, so execution fell through to `return risk_score` — a variable
  never assigned because the line that would have created it was skipped by
  the exception.
- Real traceback obtained by execution: `UnboundLocalError: cannot access local
  variable 'risk_score' where it is not associated with a value`.
- Key distinction established: logging records that something went wrong; it
  does not change control flow. Only an explicit `return` (or safe fallback
  assignment) stops execution from reaching code that assumes success.
- AlphaDefense compliance stake: in a production batch loop, an uncaught
  `UnboundLocalError` from one bad transaction propagates out of
  `score_transaction` and crashes the entire batch — every transaction after
  the failure point never gets scored.

**Gate quiz:** 3/3 passed (final attempt) — logging-vs-control-flow distinction,
severity threshold filtering (WARNING suppresses INFO/DEBUG), UnboundLocalError
propagation mechanism through an unprotected batch loop.

**Artifacts:**
- `Script11_Full_Journey_Notes.pdf` — full theory, layer-by-layer construction
  log of every bug found and fixed, gap tracker, quiz record
- `transaction_processor.py` — tested, working, verified via real execution
  against 5 transactions covering all failure modes + success paths

**Bugs found and fixed during construction (real, not idealized):**
1. Custom exception class incorrectly inherited from a function
   (`score_transaction`) with the function nested inside the exception class body
2. `logging.basicConfig` typos: `file_name` → `filename`, duplicate
   `format=format=` → single `format=`
3. `logging.get_Logger` → `logging.getLogger` (capitalization)
4. `logged.debug(...)` referenced an undefined variable → corrected to `logger`
5. `risk_sore` typo → `risk_score`
6. Custom exception class was defined but never actually raised — added the
   negative-amount business rule check
7. Deliberate-error exercise: found and explained the `UnboundLocalError` root
   cause via a real traceback, not a guess
8. First deliverable draft nested the transaction loop inside
   `score_transaction()` itself instead of wrapping external calls — restructured
9. Test data syntax error (`{'txn_id': 5, :200}` — value with no key) — corrected
   to `{'txn_id': 5}` to properly trigger the `KeyError` path

---

## Currently Active: Script 12 — File I/O + JSON
Started: 2026-07-16. Not yet gate-cleared.

---

## Parallel Tracks
- Google SWE Internship: applied 2026-06-28 (deadline day). OA contact expected
  late July–mid August 2026.
- 21-day DSA sprint: Week 1 arrays/hashmaps/two pointers/sliding window,
  Week 2 binary search/trees/linked lists/heaps, Week 3 graphs/DP/backtracking.
- Phase 0 revision week (5 days, Mon–Fri, 1–2 hrs/day) scheduled to run after
  Script 13 gate-clears and before Phase 1 EDA begins. Structure: Day 1
  Scripts 1–4, Day 2 Scripts 5–7, Day 3 Scripts 8–10 (including two open
  Script 10 retrieval gaps logged 2026-07-16: fit/transform explanation,
  fraud-filter list comprehension), Day 4 Scripts 11–13, Day 5 integration
  test combining decorators + comprehensions + pandas + error handling in
  one fraud-scoring pipeline snippet.

---

## Next Milestone
Complete Script 12 (File I/O + JSON) → Script 13 (Modules + Imports) →
Phase 0 revision week → begin Phase 1 (EDA on IEEE-CIS dataset).
