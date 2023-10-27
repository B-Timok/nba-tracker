import requests
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import pytz

def fetch_data():
    # Define the API endpoint URL
    url = "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"
    
    # Create a time zone object for the UTC time
    utc_timezone = pytz.utc
    
    # Create a time zone object for the PST time
    pst_timezone = pytz.timezone("US/Pacific")
    
    # Send an HTTP GET request to the URL
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        scoreboard = data.get("scoreboard", {})
        games = scoreboard.get("games", [])
        
        output_text.delete(1.0, tk.END)  # Clear previous data
        
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
            
            if game_status == "Final":
                game_info = f"{home_team} ({home_wins}-{home_losses}) vs {away_team} ({away_wins}-{away_losses}): {home_score}-{away_score} ({game_status})"
            else:
                game_time_utc = game.get("gameTimeUTC", "")
                
                game_time_utc = datetime.fromisoformat(game_time_utc.replace('Z', '+00:00')).replace(tzinfo=utc_timezone)
                game_time_pst = game_time_utc.astimezone(pst_timezone)
                game_time_pst_str = game_time_pst.strftime("%Y-%m-%d %I:%M %p").replace(" 0", " ")
                
                game_info = f"{home_team} ({home_wins}-{home_losses}) vs {away_team} ({away_wins}-{away_losses}): Game starts at {game_time_pst_str} PST"
            
            output_text.insert(tk.END, game_info + "\n\n")
            
            if game_status == "Final":
                home_leaders = game["gameLeaders"]["homeLeaders"]
                output_text.insert(tk.END, f"{home_team} Leaders: {home_leaders['name']} - Points: {home_leaders['points']}, Rebounds: {home_leaders['rebounds']}, Assists: {home_leaders['assists']}\n")
                
                away_leaders = game["gameLeaders"]["awayLeaders"]
                output_text.insert(tk.END, f"{away_team} Leaders: {away_leaders['name']} - Points: {away_leaders['points']}, Rebounds: {away_leaders['rebounds']}, Assists: {away_leaders['assists']}\n")
            
            output_text.insert(tk.END, "-" * 50 + "\n\n")
    else:
        output_text.insert(tk.END, "Failed to retrieve data\n")

# Create the main application window
app = tk.Tk()
app.title("NBA Live Scoreboard")

# Create a fetch button
fetch_button = ttk.Button(app, text="Fetch Data", command=fetch_data)
fetch_button.pack()

# Create a text widget for displaying the data
output_text = tk.Text(app, wrap=tk.WORD, width=60, height=20)
output_text.pack()

app.mainloop()
