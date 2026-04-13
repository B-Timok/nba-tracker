from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, DataTable, Static
from textual.binding import Binding
from textual import work

from nba_api import NBAClient, Game


class PlayByPlayScreen(Screen):
    BINDINGS = [
        Binding("escape", "go_back", "Back", show=True),
    ]

    CSS = """
    #pbp-header {
        height: 3;
        content-align: center middle;
        text-style: bold;
        background: $primary-background;
    }
    #pbp-table {
        height: 1fr;
    }
    #loading {
        width: 100%;
        height: 1fr;
        content-align: center middle;
    }
    """

    def __init__(self, client: NBAClient, game_id: str, game: Game) -> None:
        super().__init__()
        self.client = client
        self.game_id = game_id
        self.game = game

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        away = self.game.away_team
        home = self.game.home_team
        header_text = (
            f"{away.city} {away.name} {away.score}"
            f"  -  "
            f"{home.score} {home.city} {home.name}"
            f"  [{self.game.status_text}]"
        )
        yield Static(header_text, id="pbp-header")
        yield Static("Loading play-by-play...", id="loading")
        yield DataTable(id="pbp-table", cursor_type="row")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#pbp-table", DataTable)
        table.add_columns("Time", "Team", "Score", "Description")
        table.display = False
        self.load_pbp()

    @work(thread=True)
    def load_pbp(self) -> None:
        try:
            actions = self.client.get_playbyplay(self.game_id)
            self.app.call_from_thread(self._populate_table, actions)
        except Exception as e:
            self.app.call_from_thread(self._show_error, str(e))

    def _show_error(self, msg: str) -> None:
        self.query_one("#loading").update(f"Error: {msg}")

    def _populate_table(self, actions: list) -> None:
        self.query_one("#loading").display = False
        table = self.query_one("#pbp-table", DataTable)
        table.display = True
        table.clear()

        current_period = 0
        for action in actions:
            if action.period != current_period:
                current_period = action.period
                period_label = f"Q{current_period}" if current_period <= 4 else f"OT{current_period - 4}"
                table.add_row(f"--- {period_label} ---", "", "", "")

            if not action.description:
                continue

            clock = self._format_clock(action.clock)
            team = action.team_tricode or ""
            score = f"{action.score_away}-{action.score_home}" if action.score_away != "0" or action.score_home != "0" else ""
            table.add_row(clock, team, score, action.description)

        if table.row_count > 0:
            table.move_cursor(row=table.row_count - 1)

    def _format_clock(self, clock: str) -> str:
        import re
        match = re.match(r"PT(\d+)M([\d.]+)S", clock)
        if match:
            mins = int(match.group(1))
            secs = int(float(match.group(2)))
            return f"{mins}:{secs:02d}"
        return clock

    def action_go_back(self) -> None:
        self.app.pop_screen()
