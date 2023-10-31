# NBA Live Scoreboard CLI

## Table of Contents
- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [How to Run](#how-to-run)
- [Program Description](#program-description)
- [Example Usage](#example-usage)
- [Author](#author)
- [License](#license)

## Introduction

This is a Python CLI application that provides live NBA game scoreboard data using the NBA API. It displays information about the ongoing and completed games, including team names, scores, and stat leaders.

## Prerequisites

- Python installed on your system (Python 3 is recommended).
- Required Python libraries (requests, datetime, pytz).

You can install the required libraries using pip:

## How to Run

1. Open your terminal or command prompt.
2. Navigate to the directory where the Python script is located.
3. Run the script using the following command:

    ```
    python CLI_Scores.py
    ```

## Program Description

The program makes an HTTP GET request to the NBA API to fetch live scoreboard data.

It processes the JSON response to extract information about NBA games.

The program displays the following information for each game:
    
- Home team and away team names.
- Wins and losses for both teams.
- Game scores.
- Game status (whether the game has started, is ongoing(with quarter information), or has ended).
- If the game hasn't started yet, it also displays the scheduled start time in Pacific Time (PST).

For ongoing or completed games, the program displays stat leaders for both the home and away teams, including points, rebounds, and assists.

## Example Usage

Here's an example of what the program output might look like:

    Milwaukee Bucks (1-0) vs Philadelphia 76ers (0-1): 118-117 (Final)

    Milwaukee Bucks Leaders: Damian Lillard - Points: 39, Rebounds: 8, Assists: 4
    Philadelphia 76ers Leaders: Tyrese Maxey - Points: 31, Rebounds: 4, Assists: 8
    --------------------------------------------------

    Los Angeles Lakers (1-1) vs Phoenix Suns (1-1): 100-95 (Final)

    Los Angeles Lakers Leaders: Anthony Davis - Points: 30, Rebounds: 12, Assists: 2
    Phoenix Suns Leaders: Kevin Durant - Points: 39, Rebounds: 11, Assists: 2
    --------------------------------------------------
    
