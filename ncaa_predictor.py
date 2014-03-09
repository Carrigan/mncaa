"""
Author: Brian Carrigan
Date: 3/9/2014
Email: brian.c.carrigan@gmail.com

This file is part of the the mncaa python software package.

The mncaa python software package is free software: you 
can redistribute it and/or modify it under the terms of the GNU 
General Public License as published by the Free Software Foundation, 
either version 3 of the License, or (at your option) any later 
version.

The mncaa python software package is distributed in 
the hope that it will be useful, but WITHOUT ANY WARRANTY; without 
even the implied warranty of MERCHANTABILITY or FITNESS FOR A 
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with the mncaa python software package.  If not, 
see <http://www.gnu.org/licenses/>.
"""

from mncaa import MNCAA
import datetime
import pandas as pd
import operator
import pprint

def build_teamlist(filename):
    this_years_teams = open(filename, "r")
    relevant_teams = []
    for line in this_years_teams:
        relevant_teams.append(line.strip())
    this_years_teams.close
    return relevant_teams

def create_margin(score1, score2):
    if(score1 > score2):
        return score1 - score2
    return score2 - score1

def create_total(score1, score2):
    return score1 + score2

def create_relative_margin(margin, total):
    return float(margin)/total

# Create the Massey object
mcsv = MNCAA()

# Grab all massey data from 2000-2013
mcsv.download_massey_csvs()

# Create a list of all games during the downloaded times
gamelist = mcsv.create_game_list()

# Import to pandas
gameframe = pd.DataFrame(gamelist)

# Find all games with at least 1 team in this years brackets
# Since these have not yet been released, pull from last years
relevant_teams = build_teamlist("teamlist.txt")
relevant_games = gameframe.team1_name.isin(relevant_teams) | gameframe.team2_name.isin(relevant_teams)
gameframe = gameframe[relevant_games]

# Add margin, total, relative margin
gameframe["margin"] = map(create_margin, gameframe["team1_score"], gameframe["team2_score"])
gameframe["total"] = map(create_total, gameframe["team1_score"], gameframe["team2_score"])
gameframe["rel_marg"] = map(create_relative_margin, gameframe["margin"], gameframe["total"])

# Find the average relative win margin for each of this years teams
team_ranking = {}
for team in relevant_teams:
    # Add all the wins
    wins =  gameframe[gameframe.team1_name == team].rel_marg
    marg_sum = sum(wins)
    marg_count = len(wins)

    # Subtract all the losses
    losses = wins =  gameframe[gameframe.team2_name == team].rel_marg
    marg_sum -= sum(losses)
    marg_count += len(losses)

    # Add it
    team_ranking[team] = marg_sum/marg_count

# 1. Sort the scores from highest to lowest
# 2. Enter them into a bracket
# 3. ?
# 4  Win $1,000,000,000 from Mr. Buffet
sorted_winners = sorted(team_ranking.iteritems(), key=operator.itemgetter(1), reverse=True)
pprint.pprint(sorted_winners)
