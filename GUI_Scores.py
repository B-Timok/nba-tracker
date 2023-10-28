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
            game_status = game["gameStatus"]
            game_status_text = game["gameStatusText"]

            game_info = f"{home_team} ({home_wins}-{home_losses}) vs {away_team} ({away_wins}-{away_losses}): {home_score}-{away_score} ({game_status_text})"

            if game_status == 1:
                # Game hasn't started yet
                output_text.insert(tk.END, game_info + " (Game hasn't started yet)\n\n")
            else:
                # Display home team leaders
                home_leaders = game["gameLeaders"]["homeLeaders"]
                home_leader_info = f"{home_team} Leaders: {home_leaders['name']} - Points: {home_leaders['points']}, Rebounds: {home_leaders['rebounds']}, Assists: {home_leaders['assists']}"
                
                # Display away team leaders
                away_leaders = game["gameLeaders"]["awayLeaders"]
                away_leader_info = f"{away_team} Leaders: {away_leaders['name']} - Points: {away_leaders['points']}, Rebounds: {away_leaders['rebounds']}, Assists: {away_leaders['assists']}"
                
                output_text.insert(tk.END, game_info + "\n\n")
                output_text.insert(tk.END, home_leader_info + "\n")
                output_text.insert(tk.END, away_leader_info + "\n")
                output_text.insert(tk.END, "-" * 50 + "\n")
    else:
        output_text.insert(tk.END, "Failed to retrieve data\n")

# Create the main application window
app = tk.Tk()
app.title("NBA Live Scoreboard")

# Create a fetch button
fetch_button = ttk.Button(app, text="Fetch Data", command=fetch_data)
fetch_button.pack()

# Create a text widget for displaying the data
output_text = tk.Text(app, wrap=tk.WORD, width=80, height=30)
output_text.pack()

app.mainloop()
