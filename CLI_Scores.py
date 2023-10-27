import requests
from datetime import datetime
import pytz

# Define the API endpoint URL
url = "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"


# Create a time zone object for the UTC time
utc_timezone = pytz.utc

# Create a time zone object for the PST time
pst_timezone = pytz.timezone("US/Pacific")

# Send an HTTP GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    
    # Extract the scoreboard data
    scoreboard = data.get("scoreboard", {})

    # Extract the list of games
    games = scoreboard.get("games", [])
    
    # Iterate through the games and display relevant information
    for game in games:
        home_team = game["homeTeam"]["teamName"]
        away_team = game["awayTeam"]["teamName"]
        home_wins = game["homeTeam"]["wins"]
        home_losses = game["homeTeam"]["losses"]
        away_wins = game["awayTeam"]["wins"]
        away_losses = game["awayTeam"]["losses"]
        home_score = game["homeTeam"]["score"]
        away_score = game["awayTeam"]["score"]
        game_status = game["gameStatusText"]

        # Check if the game hasn't started yet
        if game_status == "Final":
            game_info = f"{home_team} ({home_wins}-{home_losses}) vs {away_team} ({away_wins}-{away_losses}): {home_score}-{away_score} ({game_status})"
        else:
            game_time_utc = game.get("gameTimeUTC", "")
            
            # Convert UTC time to PST
            game_time_utc = datetime.fromisoformat(game_time_utc.replace('Z', '+00:00')).replace(tzinfo=utc_timezone)
            game_time_pst = game_time_utc.astimezone(pst_timezone)
            
            # Format the time without leading zeros
            game_time_pst_str = game_time_pst.strftime("%Y-%m-%d %I:%M %p").replace(" 0", " ")
            
            game_info = f"{home_team} ({home_wins}-{home_losses}) vs {away_team} ({away_wins}-{away_losses}): Game starts at {game_time_pst_str} PST"
        
        print(game_info)
        print()

        if game_status == "Final":
            # Display home team leaders
            home_leaders = game["gameLeaders"]["homeLeaders"]
            print(f"{home_team} Leaders: {home_leaders['name']} - Points: {home_leaders['points']}, Rebounds: {home_leaders['rebounds']}, Assists: {home_leaders['assists']}")
            
            # Display away team leaders
            away_leaders = game["gameLeaders"]["awayLeaders"]
            print(f"{away_team} Leaders: {away_leaders['name']} - Points: {away_leaders['points']}, Rebounds: {away_leaders['rebounds']}, Assists: {away_leaders['assists']}")
            
        # Add a separator between games
        print("-" * 50)
        print()
else:
    print("Failed to retrieve data")
