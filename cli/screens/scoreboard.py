from datetime import date
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, DataTable, Static
from textual.binding import Binding
from textual import work

from nba_api import NBAClient, game_date_to_season, next_day, prev_day
from cli.widgets.date_bar import DateBar
from cli.widgets.status_bar import StatusBar


class ScoreboardScreen(Screen):
    BINDINGS = [
        Binding("left", "prev_date", "Prev Day", show=False),
        Binding("right", "next_date", "Next Day", show=False),
        Binding("d", "pick_date", "Go to Date", show=True),
        Binding("enter", "select_game", "Game Detail", show=True),
        Binding("r", "refresh", "Refresh", show=True),
    ]

    CSS = """
    #scoreboard-table {
        height: 1fr;
    }
    #date-bar {
        height: 1;
        background: $primary-background;
        color: $text;
    }
    #status-bar {
        height: 1;
        background: $primary-background;
        color: $text-muted;
    }
    #no-games {
        width: 100%;
        height: 1fr;
        content-align: center middle;
        color: $text-muted;
    }
    """

    def __init__(self, client: NBAClient) -> None:
        super().__init__()
        self.client = client
        self.games: list = []
        self._refresh_timer = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield DateBar(id="date-bar")
        yield DataTable(id="scoreboard-table", cursor_type="row")
        yield Static("No games scheduled for this date.", id="no-games")
        yield StatusBar(id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#scoreboard-table", DataTable)
        table.add_columns("Status", "Away", "Score", "Home", "Leader")
        self.query_one("#no-games").display = False
        self.load_games()

    @work(thread=True)
    def load_games(self) -> None:
        status_bar = self.query_one("#status-bar", StatusBar)
        date_bar = self.query_one("#date-bar", DateBar)
        current = date_bar.current_date

        self.app.call_from_thread(status_bar.set_loading)

        try:
            games = self.client.get_scoreboard(current)
            self.app.call_from_thread(self._update_table, games)
        except Exception as e:
            self.app.call_from_thread(status_bar.set_error, str(e))

    def _update_table(self, games: list) -> None:
        self.games = games
        table = self.query_one("#scoreboard-table", DataTable)
        no_games = self.query_one("#no-games")
        status_bar = self.query_one("#status-bar", StatusBar)

        table.clear()

        if not games:
            table.display = False
            no_games.display = True
        else:
            table.display = True
            no_games.display = False
            for game in games:
                status = self._format_status(game)
                away = f"{game.away_team.city} {game.away_team.name} ({game.away_team.record})"
                home = f"{game.home_team.city} {game.home_team.name} ({game.home_team.record})"
                if game.is_scheduled:
                    score = "vs"
                else:
                    score = f"{game.away_team.score} - {game.home_team.score}"
                leader = self._format_leader(game)
                table.add_row(status, away, score, home, leader, key=game.game_id)

        status_bar.mark_refreshed()
        status_bar.set_ready()

        has_live = any(g.is_live for g in games)
        status_bar.has_live = has_live
        self._manage_auto_refresh(has_live)

    def _format_status(self, game) -> str:
        if game.is_live:
            return f"\u25cf {game.status_text}"
        elif game.is_final:
            return game.status_text
        else:
            return game.status_text

    def _format_leader(self, game) -> str:
        if game.home_leader and not game.is_scheduled:
            return f"{game.home_leader.name} {game.home_leader.points}pts"
        return ""

    def _manage_auto_refresh(self, has_live: bool) -> None:
        if self._refresh_timer:
            self._refresh_timer.stop()
            self._refresh_timer = None
        if has_live:
            self._refresh_timer = self.set_interval(15, self._auto_refresh)

    def _auto_refresh(self) -> None:
        self.load_games()

    def action_prev_date(self) -> None:
        date_bar = self.query_one("#date-bar", DateBar)
        date_bar.go_prev()

    def action_next_date(self) -> None:
        date_bar = self.query_one("#date-bar", DateBar)
        date_bar.go_next()

    def on_date_bar_date_changed(self, message: DateBar.DateChanged) -> None:
        if self._refresh_timer:
            self._refresh_timer.stop()
            self._refresh_timer = None
        self.load_games()

    def action_refresh(self) -> None:
        self.load_games()

    def action_select_game(self) -> None:
        table = self.query_one("#scoreboard-table", DataTable)
        if table.row_count == 0:
            return
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        game_id = str(row_key)
        game = next((g for g in self.games if g.game_id == game_id), None)
        if game and not game.is_scheduled:
            from cli.screens.boxscore import BoxScoreScreen
            self.app.push_screen(BoxScoreScreen(self.client, game_id, game))

    def action_pick_date(self) -> None:
        self.app.push_screen(DateInputScreen(self))


class DateInputScreen(Screen):
    """Simple screen to type a date."""

    CSS = """
    #date-input-container {
        align: center middle;
        width: 100%;
        height: 100%;
    }
    #date-prompt {
        text-align: center;
        width: 40;
        margin-bottom: 1;
    }
    #date-input {
        width: 40;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, parent_screen: ScoreboardScreen) -> None:
        super().__init__()
        self.parent_screen = parent_screen

    def compose(self) -> ComposeResult:
        from textual.widgets import Input
        from textual.containers import Center, Middle
        with Middle():
            with Center():
                yield Static("Enter date (YYYY-MM-DD):", id="date-prompt")
                yield Input(placeholder="2026-04-12", id="date-input")

    def on_input_submitted(self, event) -> None:
        from nba_api import parse_game_date
        d = parse_game_date(event.value)
        if d:
            date_bar = self.parent_screen.query_one("#date-bar", DateBar)
            self.app.pop_screen()
            date_bar.set_date(d)
        else:
            self.query_one("#date-prompt").update("Invalid date. Try YYYY-MM-DD:")

    def action_cancel(self) -> None:
        self.app.pop_screen()
