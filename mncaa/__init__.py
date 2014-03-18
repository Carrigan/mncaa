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

import urllib2 as ul
import os
import datetime

def generate_game_filename(year):
    return str(year) + "gi.txt"

def generate_team_filename(year):
    return str(year) + "ti.txt"

def tokenize_csv_line(line_in):
    parsed = line_in.split(',')
    tokens = []
    for token in parsed:
        tokens.append(token.strip())
    return tokens

def parse_team_line(line_in):
    key_index = ["team_id", "team_name"]
    return dict(zip(key_index, tokenize_csv_line(line_in)))

def parse_game_line(line_in):
    key_index = ["epoch", "datestr", "team1_id", "team1_home", "team1_score", "team2_id", "team2_home", "team2_score"]
    return dict(zip(key_index, tokenize_csv_line(line_in)))

def get_game_date(date_str):
    return datetime.date(int(date_str[:4]), int(date_str[4:6]), int(date_str[6:8]))

class MNCAA(object):
    def __init__(self, data_dir="data", game_filename_gen = generate_game_filename, team_filename_gen=generate_team_filename, years=None):
        self.data_dir = data_dir
        self.game_filename_gen = game_filename_gen
        self.team_filename_gen = team_filename_gen
        if not years:
            self.years = range(2000, int(datetime.date.today().year) + 1, 1)
        else:
            self.years = years

    def _game_filename(self, year):
        return self.data_dir + "/" + self.game_filename_gen(year)
 
    def _team_filename(self, year):
        return self.data_dir + "/" + self.team_filename_gen(year)   

    def _scrape_game_data(self, year):
        print "Downloading game history for year " + str(year)
        game_template = "http://masseyratings.com/scores.php?s=cb{year}&sub=11590&all=1&mode=3&format=1"
        game_response = ul.urlopen(game_template.format(year=str(year)))
        return game_response

    def _scrape_team_data(self, year):
        print "Downloading team conversions for year " + str(year)
        team_template = "http://masseyratings.com/scores.php?s=cb{year}&sub=11590&all=1&mode=3&format=2"
        team_response = ul.urlopen(team_template.format(year=str(year)))
        return team_response

    def download_massey_csvs(self):
        if not os.path.exists(self.data_dir):
            if os.name is 'nt':
                os.makedirs(self.data_dir)
            else:
                os.makedir(self.data_dir)

        for year in self.years:
            if not os.path.isfile(self._game_filename(year)):
                games = self._scrape_game_data(year)
                try:
                    game_file = open(self._game_filename(year), "w")
                    print "Writing " + self._game_filename(year) + "..."
                    game_file.write(games.read())
                    game_file.close()
                except:
                    print "Error: could not write file " + self._game_filename(year)
                    quit()

            if not os.path.isfile(self._team_filename(year)):
                teams = self._scrape_team_data(year)
                try:
                    team_file = open(self._team_filename(year), "w")
                    print "Writing " + self._team_filename(year) + "..."
                    team_file.write(teams.read())
                    team_file.close()
                except:
                    print "Error: could not write file " + self._team_filename(year)
                    quit()

    # Loading the CSVs
    def create_team_dictionary(self, year):
        team_dict = {}
        team_file = open(self._team_filename(year), "r")
        for line in team_file:
            parsed = parse_team_line(line)
            team_dict[parsed["team_id"]] = parsed["team_name"]
        team_file.close()
        return team_dict

    # Create a list of dicts of all games
    def create_game_list(self):
        game_list = []

        for year in self.years:
            team_dict = self.create_team_dictionary(year)   
            game_file = open(self._game_filename(year), "r")
            for line in game_file:
                parsed = parse_game_line(line)

                # Turn the scores into ints
                parsed["team1_score"] = int(parsed["team1_score"])
                parsed["team2_score"] = int(parsed["team2_score"])

                # Remove the datestr and turn it into a date
                parsed["date"] = get_game_date(parsed.pop("datestr"))

                # Remove the team IDs and turn them into names
                parsed["team1_name"] = team_dict[parsed.pop("team1_id")]
                parsed["team2_name"] = team_dict[parsed.pop("team2_id")]

                # Remove the epoch time since we already have the datetime
                del parsed["epoch"]

                # Remove the team1/2 homes and make one column denoting the home team
                parsed["team1_home"] = int(parsed["team1_home"])
                home_team = parsed.pop("team1_home")
                del parsed["team2_home"]
                if home_team == -1:
                    home_team = 2
                parsed["hometeam"] = home_team

                # Add it
                game_list.append(parsed)
            game_file.close()
        return game_list
