import urllib2 as ul

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

def scrape(year):
    game_template = "http://masseyratings.com/scores.php?s=cb{year}&sub=11590&all=1&mode=3&format=1"
    team_template = "http://masseyratings.com/scores.php?s=cb{year}&sub=11590&all=1&mode=3&format=2"
    print "Downloading game history for year " + str(year)
    game_response = ul.urlopen(game_template.format(year=str(year)))
    print "Downloading team conversions for year " + str(year)
    team_response = ul.urlopen(team_template.format(year=str(year)))
    return game_response, team_response

def generate_game_filename(year):
    return "data/" + str(year) + "gi.txt"

def generate_team_filename(year):
    return "data/" + str(year) + "ti.txt"

