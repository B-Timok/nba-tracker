from datetime import date
from textual.app import ComposeResult
from textual.widgets import Static
from textual.reactive import reactive
from textual.message import Message


class DateBar(Static):
    """Shows current date with navigation hints."""

    current_date: reactive[date] = reactive(date.today)

    class DateChanged(Message):
        def __init__(self, new_date: date) -> None:
            self.date = new_date
            super().__init__()

    def render(self) -> str:
        d = self.current_date
        today = date.today()
        label = ""
        if d == today:
            label = " (Today)"
        return f"  \u25c0 [{d.strftime('%A, %B %d, %Y')}{label}] \u25b6  (\u2190 / \u2192 to navigate, d for date)"

    def go_next(self) -> None:
        from nba_api import next_day
        self.current_date = next_day(self.current_date)
        self.post_message(self.DateChanged(self.current_date))

    def go_prev(self) -> None:
        from nba_api import prev_day
        self.current_date = prev_day(self.current_date)
        self.post_message(self.DateChanged(self.current_date))

    def set_date(self, d: date) -> None:
        self.current_date = d
        self.post_message(self.DateChanged(self.current_date))
