class NBAEndpoints:
    _CDN_BASE = "https://cdn.nba.com/static/json/liveData"
    _STATS_BASE = "https://stats.nba.com/stats"

    @staticmethod
    def scoreboard_today() -> str:
        return f"{NBAEndpoints._CDN_BASE}/scoreboard/todaysScoreboard_00.json"

    @staticmethod
    def scoreboard(game_date: str) -> str:
        return f"{NBAEndpoints._STATS_BASE}/scoreboardv3?GameDate={game_date}&LeagueID=00"

    @staticmethod
    def boxscore(game_id: str) -> str:
        return f"{NBAEndpoints._CDN_BASE}/boxscore/boxscore_{game_id}.json"

    @staticmethod
    def playbyplay(game_id: str) -> str:
        return f"{NBAEndpoints._CDN_BASE}/playbyplay/playbyplay_{game_id}.json"

    @staticmethod
    def standings(season: str) -> str:
        return (
            f"{NBAEndpoints._STATS_BASE}/leaguestandingsv3"
            f"?LeagueID=00&Season={season}&SeasonType=Regular+Season"
        )

    @staticmethod
    def player_stats(season: str) -> str:
        return (
            f"{NBAEndpoints._STATS_BASE}/leaguedashplayerstats"
            f"?College=&Conference=&Country=&DateFrom=&DateTo="
            f"&Division=&DraftPick=&DraftYear=&GameScope="
            f"&GameSegment=&Height=&ISTRound=&LastNGames=0"
            f"&LeagueID=00&Location=&MeasureType=Base&Month=0"
            f"&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N"
            f"&PerMode=PerGame&Period=0&PlayerExperience="
            f"&PlayerPosition=&PlusMinus=N&Rank=N&Season={season}"
            f"&SeasonSegment=&SeasonType=Regular+Season"
            f"&ShotClockRange=&StarterBench=&TeamID=0"
            f"&VsConference=&VsDivision=&Weight="
        )

    @staticmethod
    def team_stats(season: str) -> str:
        return (
            f"{NBAEndpoints._STATS_BASE}/leaguedashteamstats"
            f"?Conference=&DateFrom=&DateTo=&Division=&GameScope="
            f"&GameSegment=&Height=&ISTRound=&LastNGames=0"
            f"&LeagueID=00&Location=&MeasureType=Base&Month=0"
            f"&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N"
            f"&PerMode=PerGame&Period=0&PlayerExperience="
            f"&PlayerPosition=&PlusMinus=N&Rank=N&Season={season}"
            f"&SeasonSegment=&SeasonType=Regular+Season"
            f"&ShotClockRange=&StarterBench=&TeamID=0"
            f"&VsConference=&VsDivision="
        )

    @staticmethod
    def stats_headers() -> dict[str, str]:
        return {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.nba.com/",
            "Accept": "application/json",
        }
