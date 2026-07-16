"""
AlphaDefense — Script 11: Error Handling + Logging
transaction_processor.py

Handles three distinct failure modes for fraud-scoring input, each with its
own except block and an explicit return to avoid falling through to code
that assumes success (see UnboundLocalError trace in revision notes):

  - ValueError            : amount present but not a valid number
  - KeyError              : 'amount' field missing entirely
  - InvalidTransactionError (custom): amount is a valid number but violates
                            a business rule (negative), which Python itself
                            has no concept of — only domain logic can catch it

Tested by running this file directly. Check fraud_audit.log after running.
"""

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

    except KeyError as e:
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
        # Only runs if try succeeded with zero exceptions
        logger.info(
            f"Scored txn {txn['txn_id']} successfully: risk_score={risk_score}"
        )
        return risk_score

    finally:
        # Always runs, success or failure — guaranteed audit trail entry.
        # Logged at DEBUG, so it is silently filtered out while
        # level=INFO is set (proves severity-threshold filtering live).
        logger.debug(
            f"Finished processing attempt for txn "
            f"{txn.get('txn_id', 'UNKNOWN')}"
        )


if __name__ == "__main__":
    transactions = [
        {'txn_id': 1, 'amount': -50},     # InvalidTransactionError path
        {'txn_id': 2, 'amount': 'abc'},   # ValueError path
        {'txn_id': 3, 'amount': 120},     # success path
        {'txn_id': 4, 'amount': 200},     # success path
        {'txn_id': 5},                    # KeyError path (amount missing)
    ]

    for txn in transactions:
        score_transaction(txn)

    print("Run complete. Check fraud_audit.log for the audit trail.")
