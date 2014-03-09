mncaa
=========
The Massey library provides scraping and parsing functionality for the Massey Ratings NCAA men's basketball datasets.

Usage
---
For a full usage example, see ncaa_predictor.py.

Typical usage:
```sh
# Create the library instance
mcsv = MNCAA()

# Grab all massey data from 2000-2013
mcsv.download_massey_csvs()

# Create a list of all games during the downloaded times
gamelist = mcsv.create_game_list()
```

Each game in the above gamelist will be a dict with the following keys:
* **date**: The date that the game was played on.
* **team1_name**: The name of the winning team
* **team2_name**: The name of the losing team
* **team1_score**: The score of the winning team
* **team2_score**: The score of the losing team
* **hometeam**: Which team was home (1 or 2, 0 for neither)

Creating a pandas dataframe for manipulation is easy:
```sh
gameframe = pandas.DataFrame(gamelist)
```

Requirements
---
* pandas (for sample app only)
<br><br><br>
***Happy Hacking***