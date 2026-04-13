from textual.app import App
from textual.binding import Binding

from nba_api import NBAClient
from cli.screens.scoreboard import ScoreboardScreen


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

    def on_mount(self) -> None:
        self.push_screen(ScoreboardScreen(self.client))

    def action_show_scoreboard(self) -> None:
        self.switch_screen(ScoreboardScreen(self.client))

    def action_show_standings(self) -> None:
        from cli.screens.standings import StandingsScreen
        self.switch_screen(StandingsScreen(self.client))

    def action_show_stats(self) -> None:
        from cli.screens.stats import StatsScreen
        self.switch_screen(StatsScreen(self.client))
