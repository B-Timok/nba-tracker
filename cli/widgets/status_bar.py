from datetime import datetime
from textual.widgets import Static
from textual.reactive import reactive


class StatusBar(Static):
    """Shows last refresh time and connection status."""

    last_refresh: reactive[str] = reactive("")
    status: reactive[str] = reactive("Ready")
    has_live: reactive[bool] = reactive(False)

    def render(self) -> str:
        refresh_text = f"Last refresh: {self.last_refresh}" if self.last_refresh else ""
        live_indicator = " \u25cf LIVE" if self.has_live else ""
        return f"  {self.status}{live_indicator}  {refresh_text}"

    def mark_refreshed(self) -> None:
        self.last_refresh = datetime.now().strftime("%I:%M:%S %p")

    def set_error(self, msg: str) -> None:
        self.status = f"Error: {msg}"

    def set_ready(self) -> None:
        self.status = "Ready"

    def set_loading(self) -> None:
        self.status = "Loading..."
