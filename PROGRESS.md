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
| 11 | Error Handling + Logging | 🔓 Unlocked — active |
| 12 | File I/O + JSON | 🔒 Locked |
| 13 | Modules + Imports | 🔒 Locked |

---

## Script 10 — Decorators (GATE-CLEARED)
**Date:** 2026-07-13

**Deliverable 1:** `@audit_log` decorator for fraud-scoring functions.
- Uses `functools.wraps` to preserve original function identity.
- Uses `try/finally` to guarantee the audit log is written even if the underlying
  scoring function raises an exception.
- Generalized via `*args`/`**kwargs` to work on any scoring function signature.

**Deliverable 2:** Written trace of the decorator-stacking kwargs mutation bug.
- Root cause: with `@audit_log` on top of `@add_default_threshold`, audit_log becomes
  the outermost wrapper and its `log(kwargs)` call fires **before**
  `add_default_threshold` mutates the dictionary to add the `threshold` key.
- Result: `logged = {'txn_id': 1}` while `actually received by score_transaction =
  {'txn_id': 1, 'threshold': 0.5}`.
- Compliance risk: the audit log cannot serve as reliable proof of what parameters
  drove a fraud decision — regulatory/audit exposure if a flagged transaction is
  ever disputed.
- Fix direction identified: log the final kwargs state (post-mutation), not the
  early snapshot.

**Gate quiz:** 3/3 passed — stack-flip reasoning, concrete fix description,
functools.wraps rationale.

**Artifacts:** `Script10_Decorators_Revision_Notes.pdf` (definitions, mechanism
trace, correct-vs-lacked self-assessment, quiz record). Working, tested code
in `audit_log_decorator.py`.

**Post-gate correction:** first draft of `audit_log_decorator.py` still had
`@audit_log` on top of `@add_default_threshold` and claimed logging inside
`finally` would fix the timing bug. Running it proved this false — each
wrapper's `**kwargs` is a separate dict, so a mutation two layers down never
propagates back up. Real fix: reorder the stack so `add_default_threshold`
is OUTER (mutates first) and `audit_log` is INNER (logs the completed dict).
Verified by running the script and reading `audit_trail.log` directly.

---

## Currently Active: Script 11 — Error Handling + Logging
Started: 2026-07-13. Not yet gate-cleared.

---

## Parallel Tracks
- Google SWE Internship: applied 2026-06-28 (deadline day). OA contact expected
  late July–mid August 2026.
- 21-day DSA sprint: Week 1 arrays/hashmaps/two pointers/sliding window,
  Week 2 binary search/trees/linked lists/heaps, Week 3 graphs/DP/backtracking.

---

## Next Milestone
Complete Script 11 → Script 12 (File I/O + JSON) → Script 13 (Modules + Imports)
→ close out Phase 0 → begin Phase 1 (EDA on IEEE-CIS dataset).

