from datetime import date
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, DataTable, TabbedContent, TabPane, Static
from textual.binding import Binding
from textual import work

from nba_api import NBAClient, game_date_to_season


class StandingsScreen(Screen):
    BINDINGS = [
        Binding("escape", "go_back", "Back", show=True),
        Binding("r", "refresh", "Refresh", show=True),
    ]

    CSS = """
    .standings-table {
        height: 1fr;
    }
    #loading {
        width: 100%;
        height: 1fr;
        content-align: center middle;
    }
    """

    def __init__(self, client: NBAClient) -> None:
        super().__init__()
        self.client = client

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Loading standings...", id="loading")
        with TabbedContent():
            with TabPane("Eastern Conference", id="east-tab"):
                yield DataTable(id="east-table", cursor_type="row", classes="standings-table")
            with TabPane("Western Conference", id="west-tab"):
                yield DataTable(id="west-table", cursor_type="row", classes="standings-table")
        yield Footer()

    def on_mount(self) -> None:
        for table_id in ("east-table", "west-table"):
            table = self.query_one(f"#{table_id}", DataTable)
            table.add_columns("#", "Team", "W", "L", "PCT", "GB", "Home", "Road", "L10", "Streak")
        self.load_standings()

    @work(thread=True)
    def load_standings(self) -> None:
        try:
            season = game_date_to_season(date.today())
            entries = self.client.get_standings(season)
            self.app.call_from_thread(self._populate_tables, entries)
        except Exception as e:
            self.app.call_from_thread(self._show_error, str(e))

    def _show_error(self, msg: str) -> None:
        self.query_one("#loading").update(f"Error: {msg}")

    def _populate_tables(self, entries: list) -> None:
        self.query_one("#loading").display = False

        east = sorted(
            [e for e in entries if e.conference == "East"],
            key=lambda e: e.playoff_rank,
        )
        west = sorted(
            [e for e in entries if e.conference == "West"],
            key=lambda e: e.playoff_rank,
        )

        self._fill_table("east-table", east)
        self._fill_table("west-table", west)

    def _fill_table(self, table_id: str, entries: list) -> None:
        table = self.query_one(f"#{table_id}", DataTable)
        table.clear()
        for entry in entries:
            clinch = entry.clinch_indicator.strip() if entry.clinch_indicator else ""
            team_display = f"{entry.team_city} {entry.team_name}"
            if clinch:
                team_display += f" {clinch}"
            table.add_row(
                str(entry.playoff_rank),
                team_display,
                str(entry.wins),
                str(entry.losses),
                f"{entry.win_pct:.3f}",
                str(entry.games_back) if entry.games_back > 0 else "-",
                entry.home_record,
                entry.road_record,
                entry.last_10,
                entry.streak,
            )

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_refresh(self) -> None:
        self.load_standings()
