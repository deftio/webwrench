"""Global configuration options for webwrench."""

from __future__ import annotations


class Options:
    """Module-level configuration.

    Attributes:
        assets: Where to load JS libraries from. 'local' (default) serves
            from webwrench's bundled _assets directory. 'cdn' uses public CDNs.
        debug: Enable debug logging and verbose error messages.
        keep_alive_interval: Seconds between SSE keep-alive pings.
    """

    def __init__(self) -> None:
        self.assets: str = "local"
        self.debug: bool = False
        self.keep_alive_interval: int = 15

    def reset(self) -> None:
        """Reset all options to defaults."""
        self.assets = "local"
        self.debug = False
        self.keep_alive_interval = 15


# Singleton instance
options = Options()
