from textual.app import App
from textual.binding import Binding

from nba_api import NBAClient
from cli.screens.scoreboard import ScoreboardScreen
from cli.screens.standings import StandingsScreen
from cli.screens.stats import StatsScreen


class NBAApp(App):
    """NBA Live Scoreboard TUI."""

    TITLE = "NBA Scoreboard"
    BINDINGS = [
        Binding("1", "show_scoreboard", "Scores", show=True),
        Binding("2", "show_standings", "Standings", show=True),
        Binding("3", "show_stats", "Stats", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    CSS = """
    Screen {
        background: $surface;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self.client = NBAClient()
        self._current_view = "scoreboard"

    def on_mount(self) -> None:
        self.install_screen(ScoreboardScreen(self.client), name="scoreboard")
        self.install_screen(StandingsScreen(self.client), name="standings")
        self.install_screen(StatsScreen(self.client), name="stats")
        self.push_screen("scoreboard")
        self._current_view = "scoreboard"

    def _switch_to(self, name: str) -> None:
        if self._current_view == name:
            return
        # Pop all screens back to the default, then push the new one
        while len(self.screen_stack) > 1:
            self.pop_screen()
        self.push_screen(name)
        self._current_view = name

    def action_show_scoreboard(self) -> None:
        self._switch_to("scoreboard")

    def action_show_standings(self) -> None:
        self._switch_to("standings")

    def action_show_stats(self) -> None:
        self._switch_to("stats")
