from datetime import date
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, DataTable, TabbedContent, TabPane, Static, Input
from textual.binding import Binding
from textual import work

from nba_api import NBAClient, game_date_to_season


class StatsScreen(Screen):
    BINDINGS = [
        Binding("escape", "go_back", "Back", show=True),
        Binding("slash", "search", "Search", show=True),
        Binding("s", "search", "Search", show=False),
    ]

    CSS = """
    .stats-table {
        height: 1fr;
    }
    #search-input {
        dock: top;
        display: none;
        margin: 0 1;
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
        self.all_player_stats: list = []
        self.all_team_stats: list = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Input(placeholder="Search players or teams...", id="search-input")
        yield Static("Loading stats...", id="loading")
        with TabbedContent():
            with TabPane("Player Stats", id="player-tab"):
                yield DataTable(id="player-table", cursor_type="row", classes="stats-table")
            with TabPane("Team Stats", id="team-tab"):
                yield DataTable(id="team-table", cursor_type="row", classes="stats-table")
        yield Footer()

    def on_mount(self) -> None:
        player_table = self.query_one("#player-table", DataTable)
        player_table.add_columns(
            "Player", "Team", "GP", "MPG", "PPG", "RPG", "APG",
            "SPG", "BPG", "FG%", "3P%", "FT%", "+/-",
        )
        team_table = self.query_one("#team-table", DataTable)
        team_table.add_columns(
            "Team", "GP", "W", "L", "PPG", "RPG", "APG",
            "SPG", "BPG", "FG%", "3P%", "FT%", "+/-",
        )
        self.load_stats()

    @work(thread=True)
    def load_stats(self) -> None:
        try:
            season = game_date_to_season(date.today())
            player_stats = self.client.get_player_stats(season)
            team_stats = self.client.get_team_stats(season)
            self.app.call_from_thread(self._populate, player_stats, team_stats)
        except Exception as e:
            self.app.call_from_thread(self._show_error, str(e))

    def _show_error(self, msg: str) -> None:
        self.query_one("#loading").update(f"Error: {msg}")

    def _populate(self, player_stats: list, team_stats: list) -> None:
        self.query_one("#loading").display = False
        self.all_player_stats = sorted(player_stats, key=lambda p: p.ppg, reverse=True)
        self.all_team_stats = sorted(team_stats, key=lambda t: t.ppg, reverse=True)
        self._fill_player_table(self.all_player_stats)
        self._fill_team_table(self.all_team_stats)

    def _fill_player_table(self, stats: list) -> None:
        table = self.query_one("#player-table", DataTable)
        table.clear()
        for p in stats:
            table.add_row(
                p.player_name, p.team_abbreviation,
                str(p.gp), f"{p.mpg:.1f}", f"{p.ppg:.1f}",
                f"{p.rpg:.1f}", f"{p.apg:.1f}", f"{p.spg:.1f}",
                f"{p.bpg:.1f}", f"{p.fg_pct:.3f}", f"{p.fg3_pct:.3f}",
                f"{p.ft_pct:.3f}", f"{p.plus_minus:+.1f}",
            )

    def _fill_team_table(self, stats: list) -> None:
        table = self.query_one("#team-table", DataTable)
        table.clear()
        for t in stats:
            table.add_row(
                t.team_name, str(t.gp), str(t.wins), str(t.losses),
                f"{t.ppg:.1f}", f"{t.rpg:.1f}", f"{t.apg:.1f}",
                f"{t.spg:.1f}", f"{t.bpg:.1f}", f"{t.fg_pct:.3f}",
                f"{t.fg3_pct:.3f}", f"{t.ft_pct:.3f}", f"{t.plus_minus:+.1f}",
            )

    def action_search(self) -> None:
        search_input = self.query_one("#search-input", Input)
        search_input.display = True
        search_input.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        query = event.value.lower().strip()
        if not query:
            self._fill_player_table(self.all_player_stats)
            self._fill_team_table(self.all_team_stats)
            return

        filtered_players = [
            p for p in self.all_player_stats
            if query in p.player_name.lower() or query in p.team_abbreviation.lower()
        ]
        filtered_teams = [
            t for t in self.all_team_stats
            if query in t.team_name.lower()
        ]
        self._fill_player_table(filtered_players)
        self._fill_team_table(filtered_teams)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        search_input = self.query_one("#search-input", Input)
        search_input.display = False

    def action_go_back(self) -> None:
        self.app.pop_screen()
