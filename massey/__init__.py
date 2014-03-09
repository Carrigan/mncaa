import urllib2 as ul
import os
import datetime

# Downloading the CSVs
def generate_game_filename(year):
    return "data/" + str(year) + "gi.txt"

def generate_team_filename(year):
    return "data/" + str(year) + "ti.txt"

def scrape_game_data(year):
    print "Downloading game history for year " + str(year)
    game_template = "http://masseyratings.com/scores.php?s=cb{year}&sub=11590&all=1&mode=3&format=1"
    game_response = ul.urlopen(game_template.format(year=str(year)))
    return game_response

def scrape_team_data(year):
    print "Downloading team conversions for year " + str(year)
    team_template = "http://masseyratings.com/scores.php?s=cb{year}&sub=11590&all=1&mode=3&format=2"
    team_response = ul.urlopen(team_template.format(year=str(year)))
    return team_response

def download_massey_csvs(years):
    if not os.path.exists("data"):
        os.makedir("data")
    for year in years:
        if not os.path.isfile(generate_game_filename(year)):
            games = scrape_game_data(year)
            try:
                game_file = open(generate_game_filename(year), "w")
                print "Writing " + generate_game_filename(year) + "..."
                game_file.write(games.read())
                game_file.close()
            except:
                print "Error: could not open file " + generate_game_filename(year)
                quit()

        if not os.path.isfile(generate_team_filename(year)):
            teams = scrape_team_data(year)
            try:
                team_file = open(data_folder + "/" + generate_team_filename(year), "w")
                print "Writing " + data_folder + "/" + generate_team_filename(year) + "..."
                team_file.write(teams.read())
                team_file.close()
            except:
                print "Error: could not open file " + generate_team_filename(year)
                quit()

# Loading the CSVs
def create_team_dictionary(year):
    team_dict = {}
    team_file = open(generate_team_filename(year), "r")
    for line in team_file:
        parsed = parse_team_line(line)
        team_dict[parsed["team_id"]] = parsed["team_name"]
    team_file.close()
    return team_dict

# Parsing the CSVs
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

def get_game_date(parsed_game):
    date_str = parsed_game["datestr"]
    return datetime.date(int(date_str[:4]), int(date_str[4:6]), int(date_str[6:8]))