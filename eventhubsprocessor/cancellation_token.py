"""
Author: Aaron (Ari) Bornstien
Based on https://stackoverflow.com/questions/43229939/how-to-pass-a-boolean-by-reference-across-threads-and-modules
"""
class CancellationToken:
    """
    Thread Safe Mutable Cancellation Token
    """
    def __init__(self):
        self.is_cancelled = False

    def cancel(self):
        """
        Cancel the token
        """
        self.is_cancelled = True
