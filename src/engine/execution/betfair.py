from ..config import ENABLE_LIVE_EXECUTION
class BetfairExecutor:
    """Execution boundary. Disabled by default. Requires the user's own eligible account/app key/certificates."""
    def __init__(self,client=None): self.client=client
    def place(self,order):
        if not ENABLE_LIVE_EXECUTION: raise RuntimeError('LIVE EXECUTION IS DISABLED')
        if self.client is None: raise RuntimeError('Betfair client not configured')
        raise NotImplementedError('Map validated Order to venue-specific market/selection IDs before enabling placement')
