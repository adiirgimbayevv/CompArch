"""
Swap area — a backing store for pages evicted from physical memory.

This is a simulated swap. We don't actually save bytes; we just
remember "VPN X is currently in swap (and was dirty / clean)" so
the fault handler can find it again.

Owner: Person 5.
"""


class SwapArea:
    """Tracks VPNs currently swapped out."""

    def __init__(self, capacity: int = 1_000_000) -> None:
        self.capacity = capacity
        self._stored: dict[int, dict] = {}  # vpn -> {"dirty": bool, ...}
        self.swap_outs = 0
        self.swap_ins = 0

    def swap_out(self, vpn: int, dirty: bool) -> None:
        """Push a page to swap. Only dirty pages truly need writing,
        but we track all evicted pages here."""
        if len(self._stored) >= self.capacity and vpn not in self._stored:
            raise RuntimeError("swap area is full")

        self._stored[vpn] = {"dirty": dirty}
        self.swap_outs += 1

    def swap_in(self, vpn: int) -> dict | None:
        """Retrieve metadata for a previously-swapped-out page.
        Returns None if this VPN was never swapped (so the fault
        handler knows it's the page's first touch -> zero-fill)."""
        metadata = self._stored.pop(vpn, None)
        if metadata is not None:
            self.swap_ins += 1
        return metadata

    def contains(self, vpn: int) -> bool:
        return vpn in self._stored

    def __len__(self) -> int:
        return len(self._stored)
