from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, DataTable, Static, TabbedContent, TabPane
from textual.binding import Binding
from textual import work

from nba_api import NBAClient, Game


class BoxScoreScreen(Screen):
    BINDINGS = [
        Binding("escape", "go_back", "Back", show=True),
        Binding("p", "show_pbp", "Play-by-Play", show=True),
    ]

    CSS = """
    #game-header {
        height: 3;
        content-align: center middle;
        text-style: bold;
        background: $primary-background;
    }
    .box-table {
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
            f"{away.city} {away.name} ({away.record}) {away.score}"
            f"  -  "
            f"{home.score} {home.city} {home.name} ({home.record})"
            f"  [{self.game.status_text}]"
        )
        yield Static(header_text, id="game-header")

        yield Static("Loading box score...", id="loading")

        with TabbedContent():
            with TabPane(f"{away.city} {away.name}", id="away-tab"):
                yield DataTable(id="away-table", cursor_type="row", classes="box-table")
            with TabPane(f"{home.city} {home.name}", id="home-tab"):
                yield DataTable(id="home-table", cursor_type="row", classes="box-table")

        yield Footer()

    def on_mount(self) -> None:
        for table_id in ("away-table", "home-table"):
            table = self.query_one(f"#{table_id}", DataTable)
            table.add_columns(
                "Player", "MIN", "PTS", "REB", "AST", "STL", "BLK",
                "FG", "3PT", "FT", "+/-",
            )
        self.load_boxscore()

    @work(thread=True)
    def load_boxscore(self) -> None:
        try:
            home_box, away_box = self.client.get_boxscore(self.game_id)
            self.app.call_from_thread(self._populate_table, "away-table", away_box)
            self.app.call_from_thread(self._populate_table, "home-table", home_box)
            self.app.call_from_thread(self._hide_loading)
        except Exception as e:
            self.app.call_from_thread(self._show_error, str(e))

    def _hide_loading(self) -> None:
        self.query_one("#loading").display = False

    def _show_error(self, msg: str) -> None:
        self.query_one("#loading").update(f"Error: {msg}")

    def _populate_table(self, table_id: str, team_box) -> None:
        table = self.query_one(f"#{table_id}", DataTable)
        table.clear()

        starters = [p for p in team_box.players if p.starter]
        bench = [p for p in team_box.players if not p.starter]

        for player in starters + bench:
            fg = f"{player.fg_made}-{player.fg_attempted}"
            fg3 = f"{player.fg3_made}-{player.fg3_attempted}"
            ft = f"{player.ft_made}-{player.ft_attempted}"
            pm = f"+{player.plus_minus:.0f}" if player.plus_minus > 0 else f"{player.plus_minus:.0f}"
            table.add_row(
                player.name,
                player.minutes_display,
                str(player.points),
                str(player.rebounds),
                str(player.assists),
                str(player.steals),
                str(player.blocks),
                fg, fg3, ft, pm,
            )

        # Totals row
        table.add_row(
            "TOTALS", "",
            str(team_box.total_points),
            str(team_box.total_rebounds),
            str(team_box.total_assists),
            str(team_box.total_steals),
            str(team_box.total_blocks),
            f"{team_box.fg_made}-{team_box.fg_attempted}",
            f"{team_box.fg3_made}-{team_box.fg3_attempted}",
            f"{team_box.ft_made}-{team_box.ft_attempted}",
            "",
        )

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_show_pbp(self) -> None:
        from cli.screens.playbyplay import PlayByPlayScreen
        self.app.push_screen(PlayByPlayScreen(self.client, self.game_id, self.game))
