"""
audit_log_decorator.py

AlphaDefense — Phase 0, Script 10 (Decorators)

Purpose
-------
Provides an @audit_log decorator for fraud-scoring functions. Every call to a
decorated function is logged with its final input parameters and result,
guaranteed to fire even if the underlying function raises an exception.

This exists because fraud detection systems are regulated: if a transaction
is flagged (or cleared) as fraud, the company must be able to prove exactly
what inputs drove that decision if it is ever challenged by a regulator or
customer.

Known bug this file intentionally avoids (see PROGRESS_LOG.md for the full
trace): if @audit_log is stacked ABOVE a decorator that mutates kwargs (e.g.
one that injects a default threshold), audit_log's log() call fires before
the mutation happens, so the log becomes a false record.

IMPORTANT — the real fix is stack ORDER, not "log later inside the same
wrapper." Each wrapper's **kwargs is a separate dictionary created fresh at
that function boundary; a mutation made two layers down does not propagate
back up automatically, so logging in `finally` inside the OUTER wrapper does
NOT see an inner wrapper's mutation. The correct fix is to put the mutating
decorator (add_default_threshold) OUTER, so it runs first, and put audit_log
INNER — closer to the real function — so it logs the dictionary only after
it is already complete.
"""

import functools
import logging
from datetime import datetime, timezone

# --- Logger setup -----------------------------------------------------
logging.basicConfig(
    filename="audit_trail.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("alphadefense.audit")


def audit_log(func):
    """
    Decorator that logs every call to a fraud-scoring function: its final
    arguments, its result, and whether it succeeded or raised an exception.

    Guarantees a log entry is written even on failure, using try/finally.
    Uses functools.wraps so the wrapped function keeps its real name and
    docstring for debugging, tracebacks, and auto-generated documentation.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = None
        error = None
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            error = e
            raise
        finally:
            # Log the FINAL state of kwargs (post any upstream mutation),
            # not an early snapshot — this is the fix for the timing bug
            # documented in Script 10's written trace.
            timestamp = datetime.now(timezone.utc).isoformat()
            if error is None:
                logger.info(
                    f"func={func.__name__} args={args} kwargs={kwargs} "
                    f"result={result} status=SUCCESS time={timestamp}"
                )
            else:
                logger.error(
                    f"func={func.__name__} args={args} kwargs={kwargs} "
                    f"result=None status=FAILED error={error!r} time={timestamp}"
                )

    return wrapper


def add_default_threshold(func):
    """
    Decorator that injects a default fraud-flag threshold into kwargs if the
    caller did not explicitly provide one. Must run BEFORE audit_log logs,
    which is why it sits as the OUTER decorator (applied last, executes
    first) — it mutates kwargs first, then hands the completed dictionary
    down to audit_log.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        kwargs.setdefault("threshold", 0.5)
        return func(*args, **kwargs)

    return wrapper


@add_default_threshold
@audit_log
def score_transaction(**kwargs):
    """
    Placeholder fraud-scoring function. Real scoring logic (XGBoost model
    inference) will replace this body in Phase 3.
    """
    txn_id = kwargs.get("txn_id")
    threshold = kwargs.get("threshold")
    # Dummy scoring logic for now — real model output plugs in later.
    fraud_score = 0.73
    is_flagged = fraud_score >= threshold
    return {"txn_id": txn_id, "fraud_score": fraud_score, "flagged": is_flagged}


if __name__ == "__main__":
    # Manual smoke test — run this file directly to see a real log entry
    # written to audit_trail.log with the correct, final kwargs state.
    print(score_transaction(txn_id=1))
    print(f"Wrapped function identity preserved: {score_transaction.__name__}")
