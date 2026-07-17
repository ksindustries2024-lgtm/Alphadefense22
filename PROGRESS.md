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
| 12 | File I/O + JSON | ✅ Gate-cleared |
| 13 | Modules + Imports | 🔓 Unlocked — active |
| 13.5 | Generators (yield, lazy iteration) — added for memory-efficient handling of 590K-row dataset in later phases | 🔒 Locked, queued after 13 |

---

## Script 12 — File I/O + JSON (GATE-CLEARED)
**Date:** 2026-07-17

**Deliverable:** `batch_processor.py` — reads a batch of transactions from
`transactions.json`, scores each with `score_transaction()` (Script 11 logic
reused directly), writes a labeled summary to `results_summary.json`.

**Core mechanics covered:** `with open()` file handling, `'r'`/`'w'`/`'a'`
mode selection matched to actual intent (corrected an early overcorrection
toward "always use `'a'`"), why JSON exists as a cross-language persistence
format, `f.read()` (string) vs `json.load()` (real parsed dict/list)
distinction, `json.dump(data, f)` argument order.

**Real bugs found and fixed during construction:**
1. Unclosed file handle in a plain `open()` (no `with`, no `.close()`) —
   deliberate-error exercise, correctly connected to OS file-handle exhaustion
   risk at AlphaDefense production scale
2. `json.decoder.JSONDecodeError` — discovered via real execution (deliberately
   broke a JSON file, read Python's actual traceback), not guessed; caught
   writing the bare name (`JSONDecodeError`) without the `json.` prefix twice
   before correcting to match the `json.load`/`json.dump` pattern
3. **Real crash reproduced live:** `process_batch()` initially had no guard
   against `load_transactions()` returning `None`. Deleted `transactions.json`
   and ran the pipeline — produced `TypeError: 'NoneType' object is not
   iterable` at `for txn in transactions:`. Fixed with a guard clause
   (`if transactions is None: return {...}`) before the loop — same defensive
   pattern as Script 11's `UnboundLocalError` fix
4. Output design: `process_batch()` initially returned an unlabeled tuple
   (`[1, 2]` in the JSON file, no way to tell which count was which) —
   corrected to a labeled dict (`{'success_count': ..., 'error_count': ...}`)

**Gate quiz:** 3/3 on reattempt (first attempt failed all three — required
redo before advancing, no rounding up). Final pass covered: why `for` loops
crash on `None` (not iterable, unrelated to JSON conversion), the nature and
correct discovery method for `JSONDecodeError`, and why a missing `return` in
an `except` block lets execution fall through to code after the whole
try/except/else/finally block (`else` is always skipped once an exception has
fired; `finally` always runs regardless).

**Artifacts:**
- `Script12_FileIO_JSON_Full_Notes.pdf` — theory, full construction log with
  every bug in the order it happened, gap tracker, quiz record
- `batch_processor.py` — tested, verified via real execution against 5
  transactions (negative, wrong-type, two valid, missing key) and separately
  against a missing-input-file scenario, both producing correct, crash-free
  output

**Verified output (real run):**
```
transactions.json (5 txns) → results_summary.json: {"success_count": 2, "error_count": 3}
transactions.json missing  → results_summary.json: {"success_count": 0, "error_count": 0}, no crash
```

---

## Currently Active: Script 13 — Modules + Imports
Started: 2026-07-17. Not yet gate-cleared.

Scope: `import` mechanics, `import module` vs `from module import thing` vs
`from module import *` (and why the last is discouraged in production),
splitting AlphaDefense's code across multiple files (`exceptions.py`,
`scoring.py`, `logging_config.py` etc. instead of one script), packages and
`__init__.py`, circular import errors.

Queued immediately after: **Script 13.5 — Generators** (`yield`, lazy
iteration) — added specifically for memory-efficient handling of the 590K-row
IEEE-CIS dataset and later streaming/batch use in Phase 4/5 real-time serving.

---

## Parallel Tracks
- Google SWE Internship: applied 2026-06-28 (deadline day). OA contact expected
  late July–mid August 2026.
- 21-day DSA sprint: Week 1 arrays/hashmaps/two pointers/sliding window,
  Week 2 binary search/trees/linked lists/heaps, Week 3 graphs/DP/backtracking.
- Phase 0 revision week (5 days, Mon–Fri, 1–2 hrs/day) scheduled to run after
  Script 13 (+ 13.5) gate-clears and before Phase 1 EDA begins. Structure:
  Day 1 Scripts 1–4, Day 2 Scripts 5–7, Day 3 Scripts 8–10 (including two open
  Script 10 retrieval gaps logged 2026-07-16: fit/transform explanation,
  fraud-filter list comprehension), Day 4 Scripts 11–13(.5), Day 5 integration
  test combining decorators + comprehensions + pandas + error handling + file
  I/O in one fraud-scoring pipeline snippet.

---

## Next Milestone
Complete Script 13 (Modules + Imports) → Script 13.5 (Generators) →
Phase 0 revision week → begin Phase 1 (EDA on IEEE-CIS dataset).

**Reality check, stated plainly:** Phase 0 is the Python foundation, not
AlphaDefense itself. Finishing Script 13 is a real milestone but is not
equivalent to having built the fraud detection system — the resume-relevant
work (EDA, XGBoost, SHAP, VaR/GARCH, Fairlearn, FastAPI/Streamlit, MLOps)
starts at Phase 1, after the revision week. 
