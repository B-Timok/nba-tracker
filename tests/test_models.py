from nba_api.models import Team, PeriodScore, GameLeader, Game, PlayerBoxScore, TeamBoxScore, PlayAction, StandingsEntry, PlayerStats, TeamStats


def test_team_basic_fields():
    team = Team(
        team_id=1610612738,
        name="Celtics",
        city="Boston",
        tricode="BOS",
        slug="celtics",
        wins=56,
        losses=26,
        score=113,
    )
    assert team.name == "Celtics"
    assert team.tricode == "BOS"
    assert team.record == "56-26"


def test_team_with_periods():
    team = Team(
        team_id=1610612738,
        name="Celtics",
        city="Boston",
        tricode="BOS",
        slug="celtics",
        wins=56,
        losses=26,
        score=113,
        periods=[
            PeriodScore(period=1, period_type="REGULAR", score=20),
            PeriodScore(period=2, period_type="REGULAR", score=32),
        ],
    )
    assert len(team.periods) == 2
    assert team.periods[0].score == 20


def test_game_leader():
    leader = GameLeader(
        person_id=1631248,
        name="Baylor Scheierman",
        jersey_num="55",
        position="G",
        team_tricode="BOS",
        points=30,
        rebounds=7,
        assists=7,
    )
    assert leader.name == "Baylor Scheierman"
    assert leader.points == 30


def _make_team(name="Celtics", tricode="BOS", score=113, wins=56, losses=26):
    return Team(
        team_id=1,
        name=name,
        city="Boston",
        tricode=tricode,
        slug=name.lower(),
        wins=wins,
        losses=losses,
        score=score,
    )


def test_game_scheduled():
    game = Game(
        game_id="0022501186",
        game_code="20260412/ORLBOS",
        status=1,
        status_text="7:00 pm ET",
        period=0,
        game_clock="",
        game_time_utc="2026-04-12T23:00:00Z",
        game_et="2026-04-12T19:00:00Z",
        home_team=_make_team(),
        away_team=_make_team("Magic", "ORL", 0, 45, 37),
    )
    assert game.is_scheduled
    assert not game.is_live
    assert not game.is_final


def test_game_live():
    game = Game(
        game_id="0022501186",
        game_code="20260412/ORLBOS",
        status=2,
        status_text="Q3 5:42",
        period=3,
        game_clock="PT05M42.00S",
        game_time_utc="2026-04-12T23:00:00Z",
        game_et="2026-04-12T19:00:00Z",
        home_team=_make_team(score=78),
        away_team=_make_team("Magic", "ORL", 72, 45, 37),
    )
    assert game.is_live
    assert not game.is_scheduled
    assert not game.is_final


def test_game_final():
    game = Game(
        game_id="0022501186",
        game_code="20260412/ORLBOS",
        status=3,
        status_text="Final",
        period=4,
        game_clock="",
        game_time_utc="2026-04-12T23:00:00Z",
        game_et="2026-04-12T19:00:00Z",
        home_team=_make_team(score=113),
        away_team=_make_team("Magic", "ORL", 108, 45, 37),
    )
    assert game.is_final
    assert not game.is_live


def test_game_overtime():
    game = Game(
        game_id="0022501186",
        game_code="20260412/ORLBOS",
        status=3,
        status_text="Final/OT",
        period=5,
        game_clock="",
        game_time_utc="2026-04-12T23:00:00Z",
        game_et="2026-04-12T19:00:00Z",
        regulation_periods=4,
        home_team=_make_team(score=120),
        away_team=_make_team("Magic", "ORL", 118, 45, 37),
    )
    assert game.is_final
    assert game.overtime_periods == 1


def test_player_box_score():
    player = PlayerBoxScore(
        person_id=1631248,
        name="Baylor Scheierman",
        name_short="B. Scheierman",
        jersey_num="55",
        position="SF",
        starter=True,
        minutes="PT38M48.40S",
        points=30,
        rebounds=7,
        assists=7,
        steals=2,
        blocks=1,
        turnovers=3,
        fouls=3,
        fg_made=8,
        fg_attempted=20,
        fg_pct=0.4,
        fg3_made=6,
        fg3_attempted=14,
        fg3_pct=0.429,
        ft_made=8,
        ft_attempted=8,
        ft_pct=1.0,
        plus_minus=15.0,
        reb_offensive=0,
        reb_defensive=7,
    )
    assert player.name == "Baylor Scheierman"
    assert player.starter is True
    assert player.points == 30
    assert player.minutes_display == "38:48"


def test_team_box_score():
    box = TeamBoxScore(
        team=_make_team(),
        players=[],
        total_points=113,
        total_rebounds=50,
        total_assists=24,
        total_steals=10,
        total_blocks=6,
        total_turnovers=17,
        total_fouls=23,
        fg_made=36,
        fg_attempted=87,
        fg_pct=0.414,
        fg3_made=19,
        fg3_attempted=50,
        fg3_pct=0.38,
        ft_made=22,
        ft_attempted=22,
        ft_pct=1.0,
        points_in_paint=32,
        points_fastbreak=18,
        points_second_chance=11,
        bench_points=17,
        biggest_lead=16,
    )
    assert box.total_points == 113
    assert box.bench_points == 17


def test_play_action():
    action = PlayAction(
        action_number=4,
        clock="PT11M57.00S",
        period=1,
        period_type="REGULAR",
        action_type="jumpball",
        description="Jump Ball W. Carter Jr. vs. L. Garza: Tip to P. Banchero",
        team_tricode="ORL",
        person_id=1631094,
        player_name="Banchero",
        score_home="0",
        score_away="0",
        is_field_goal=False,
    )
    assert action.description.startswith("Jump Ball")
    assert action.period == 1


def test_standings_entry():
    entry = StandingsEntry(
        team_id=1610612760,
        team_name="Thunder",
        team_city="Oklahoma City",
        team_tricode="OKC",
        conference="West",
        division="Northwest",
        division_rank=1,
        playoff_rank=1,
        wins=64,
        losses=18,
        win_pct=0.78,
        home_record="34-7",
        road_record="30-10",
        last_10="7-3",
        streak="L 2",
        games_back=0.0,
        clinch_indicator=" - w",
    )
    assert entry.team_name == "Thunder"
    assert entry.record == "64-18"


def test_player_stats():
    stats = PlayerStats(
        player_id=203999,
        player_name="Nikola Jokic",
        team_id=1610612743,
        team_abbreviation="DEN",
        age=31.0,
        gp=79,
        mpg=36.5,
        ppg=30.2,
        rpg=13.1,
        apg=10.5,
        spg=1.7,
        bpg=0.8,
        topg=3.8,
        fpg=2.6,
        fg_pct=0.580,
        fg3_pct=0.410,
        ft_pct=0.830,
        plus_minus=8.5,
    )
    assert stats.player_name == "Nikola Jokic"
    assert stats.ppg == 30.2


def test_team_stats():
    stats = TeamStats(
        team_id=1610612737,
        team_name="Atlanta Hawks",
        gp=82,
        wins=46,
        losses=36,
        win_pct=0.561,
        mpg=48.2,
        ppg=118.5,
        rpg=43.5,
        apg=30.1,
        spg=9.4,
        bpg=4.7,
        topg=14.2,
        fpg=19.7,
        fg_pct=0.474,
        fg3_pct=0.371,
        ft_pct=0.774,
        plus_minus=2.4,
    )
    assert stats.team_name == "Atlanta Hawks"
    assert stats.ppg == 118.5
