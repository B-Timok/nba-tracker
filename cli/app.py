from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.binding import Binding


class NBAApp(App):
    """NBA Live Scoreboard TUI."""

    TITLE = "NBA Scoreboard"
    BINDINGS = [
        Binding("1", "switch_screen('scoreboard')", "Scores", show=True),
        Binding("2", "switch_screen('standings')", "Standings", show=True),
        Binding("3", "switch_screen('stats')", "Stats", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    CSS = """
    Screen {
        background: $surface;
    }
    #placeholder {
        width: 100%;
        height: 100%;
        content-align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Loading scoreboard...", id="placeholder")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "NBA Scoreboard"
        self.sub_title = "Loading..."
