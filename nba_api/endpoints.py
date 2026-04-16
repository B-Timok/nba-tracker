class NBAEndpoints:
    _CDN_BASE = "https://cdn.nba.com/static/json/liveData"
    _CDN_STATIC = "https://cdn.nba.com/static/json/staticData"
    _STATS_BASE = "https://stats.nba.com/stats"

    @staticmethod
    def scoreboard_today() -> str:
        return f"{NBAEndpoints._CDN_BASE}/scoreboard/todaysScoreboard_00.json"

    @staticmethod
    def schedule() -> str:
        return f"{NBAEndpoints._CDN_STATIC}/scheduleLeagueV2_1.json"

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
        # stats.nba.com sits behind Akamai Bot Manager, which inspects both
        # headers and TLS fingerprint. These headers match what nba.com's
        # own web app sends; the TLS side is handled by curl_cffi's
        # browser impersonation in NBAClient.
        return {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://www.nba.com",
            "Referer": "https://www.nba.com/",
            "x-nba-stats-origin": "stats",
            "x-nba-stats-token": "true",
            "Connection": "keep-alive",
        }
