"""
AlphaDefense — Script 12: File I/O + JSON
batch_processor.py

Reads a batch of transactions from transactions.json, scores each one using
score_transaction() (Script 11), and writes a labeled results summary to
results_summary.json.

Handles three file-level failure modes on the input side (missing file,
malformed JSON) plus the three per-transaction failure modes already built
into score_transaction() (wrong type, missing field, negative amount).

Guard clause note: process_batch() explicitly checks if transactions is None
before looping — load_transactions() can legitimately return None on failure,
and looping over None crashes with TypeError: 'NoneType' object is not
iterable. This mirrors the Script 11 UnboundLocalError lesson: never assume
a returned value is safe to use without checking first.
"""

import json
import logging

logging.basicConfig(
    filename='fraud_audit.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)


class InvalidTransactionError(Exception):
    """Raised when a transaction is syntactically valid but violates a
    fraud-scoring business rule (e.g. negative amount)."""
    pass


def score_transaction(txn):
    try:
        amount = txn['amount']
        amount = float(amount)

        if amount < 0:
            raise InvalidTransactionError(
                f"Negative amount {amount} is not valid for fraud scoring"
            )

        risk_score = amount * 0.01

    except ValueError as e:
        logger.error(
            f"Wrong data type for amount in txn "
            f"{txn.get('txn_id', 'UNKNOWN')}: {e}"
        )
        return None

    except KeyError:
        logger.error(
            f"Missing amount field in txn {txn.get('txn_id', 'UNKNOWN')}"
        )
        return None

    except InvalidTransactionError as e:
        logger.error(
            f"Business-rule violation in txn "
            f"{txn.get('txn_id', 'UNKNOWN')}: {e}"
        )
        return None

    else:
        logger.info(
            f"Scored txn {txn['txn_id']} successfully: risk_score={risk_score}"
        )
        return risk_score

    finally:
        logger.debug(f"Finished processing attempt for txn {txn.get('txn_id', 'UNKNOWN')}")


def load_transactions():
    """Reads transactions.json into a list of dicts. Returns None on either
    a missing file or malformed JSON — callers must check for None before use."""
    try:
        with open('transactions.json', 'r') as f:
            transactions = json.load(f)
            return transactions

    except FileNotFoundError as e:
        logger.error(f"transactions.json not found: {e}")
        return None

    except json.decoder.JSONDecodeError as e:
        logger.error(f"transactions.json contains malformed JSON: {e}")
        return None


def process_batch():
    transactions = load_transactions()

    # Guard clause: load_transactions() can legitimately return None.
    # Looping over None crashes with TypeError — verified live by deleting
    # transactions.json and running this pipeline without this check.
    if transactions is None:
        return {'success_count': 0, 'error_count': 0}

    success_count = 0
    error_count = 0

    for txn in transactions:
        result = score_transaction(txn)
        if result is None:
            error_count += 1
        else:
            success_count += 1

    return {'success_count': success_count, 'error_count': error_count}


if __name__ == "__main__":
    summary = process_batch()

    with open('results_summary.json', 'w') as f:
        json.dump(summary, f)

    print(f"Batch complete: {summary}")
    print("Check fraud_audit.log for per-transaction detail, "
          "results_summary.json for the summary.")
