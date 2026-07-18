"""
AlphaDefense — Script 13: Modules + Imports
scoring.py

Contains score_transaction(), imported and reused from Script 11/12.
Imports InvalidTransactionError from exceptions.py — this is the one
import direction allowed (scoring depends on exceptions, never the
reverse), which is what keeps the whole chain circular-import-free.

Note: this file sets up its own logger via getLogger(__name__), but does
NOT call logging.basicConfig() itself. basicConfig is called exactly once,
in main.py, for the whole running program — every file's logger plugs into
that single shared configuration automatically.
"""

import logging
from exceptions import InvalidTransactionError

logger = logging.getLogger(__name__)


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
        logger.debug(
            f"Finished processing attempt for txn "
            f"{txn.get('txn_id', 'UNKNOWN')}"
        )
