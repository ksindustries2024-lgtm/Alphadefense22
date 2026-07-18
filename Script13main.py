"""
AlphaDefense — Script 13: Modules + Imports
main.py

Entry point. Owns the single logging.basicConfig() call for the whole
program — scoring.py's logger plugs into this same configuration
automatically, without needing its own basicConfig call.

Import chain, one-directional, no circular imports:
    main.py  -->  scoring.py  -->  exceptions.py

(exceptions.py imports nothing of its own — it sits at the bottom of the
chain on purpose, which is what makes this structure safe as more files
get added later.)
"""

import logging
from scoring import score_transaction

logging.basicConfig(
    filename='fraud_audit.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
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

    print("Run complete across 3 files: main.py -> scoring.py -> exceptions.py")
    print("Check fraud_audit.log for the audit trail.")
