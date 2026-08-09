"""
AlphaDefense — Script 13: Modules + Imports
exceptions.py

Custom exception definitions live here, in their own file, deliberately
importing nothing of the project's own code. This keeps exceptions.py at
the bottom of the dependency chain — it can be imported BY other files
(scoring.py, and eventually many more) without ever risking a circular
import, since it never needs to import anything back from them.
"""


class InvalidTransactionError(Exception):
    """Raised when a transaction is syntactically valid but violates a
    fraud-scoring business rule (e.g. negative amount) — something Python's
    built-in exceptions (ValueError, KeyError) have no concept of, since
    it's a domain-specific rule, not a language-level type error."""
    pass
