import urllib2 as ul
import os
import datetime
import operator
import pprint

def scrape_game_history(year):
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

class Game(object):
    def __init__(self, *args, **kwargs):
        csv_tokens = kwargs.pop('tokens', None)
        team_dict = kwargs.pop('team_dict', None)
        if csv_tokens and team_dict:
            self.team_1 = team_dict[csv_tokens["team1_id"]]
            self.team_2 = team_dict[csv_tokens["team2_id"]]
            self.score_1 = int(csv_tokens["team1_score"])
            self.score_2 = int(csv_tokens["team2_score"])                  
        else:           
            self.team_1 = args[0]
            self.team_2 = args[1]
            self.score_1 = args[2]
            self.score_2 = args[3]
        
    @property
    def winner(self):
        if(self.score_1 > self.score_2):
            return self.team_1
        return self.team_2

    @property
    def loser(self):
        if(self.score_1 > self.score_2):
            return self.team_2
        return self.team_1  
    
    @property
    def margin(self):
        if(self.score_1 > self.score_2):
            return self.score_1 - self.score_2
        return self.score_1 - self.score_2

    @property
    def score(self):
        return self.winner, self.loser, (float(self.margin) / (self.score_1 + self.score_2))


def csv_str_to_date(str_in):
    return datetime.date(int(str_in[:4]), int(str_in[4:6]), int(str_in[6:8]))

def gamestring_on_date(str_in, date):
    try:
        date_of_game = csv_str_to_date(str_in)
    except:
        return False
    return ((date_of_game.day == date.day) and (date_of_game.month == date.month))

def fill_dict_by_year(year):
    team_dict = {}
    team_file = open("data/{year}ti.txt".format(year = year), "r")
    for line in team_file:
        parsed = parse_team_line(line)
        team_dict[parsed["team_id"]] = parsed["team_name"]
    team_file.close()
    return team_dict

def update_game_dict(game_dict, game):
    w, l, m = game.score
    if w not in game_dict:
        game_dict[w] = 0
    if l not in game_dict:
        game_dict[l] = 0
    game_dict[w] += m
    game_dict[l] -= m

def get_game_data_by_years(desired_years):
    # Grab the date from the following years if it doesn't exist
    if not os.path.exists("data"):
        os.makedirs("data")
        for year in desired_years:
            games, teams = scrape_game_history(year)
            try:
                game_file = open(generate_game_filename(year), "w")
                print "Writing " + generate_game_filename(year) + "..."
                game_file.write(games.read())
                game_file.close()
            except:
                print "Error: could not open file " + generate_game_filename(year)
                quit()
            try:
                team_file = open(generate_team_filename(year), "w")
                print "Writing " + generate_team_filename(year) + "..."
                team_file.write(teams.read())
                team_file.close()
            except:
                print "Error: could not open file " + generate_game_filename(year)
                quit()

def generate_gamelist_by_date(date, desired_years):
    games = []
    for year in desired_years:
        print "------- " + str(year) + " -------"
        csv = open("data/{year}gi.txt".format(year=year), "r")
        team_dict = fill_dict_by_year(year)
        for line in csv:
            parsed = parse_game_line(line)
            if gamestring_on_date(parsed["datestr"], date):
                games.append(Game(tokens=parsed, team_dict=team_dict))
    return games
        

# Create a dictionary of all the teams that played on 1/23 and
# sum their win/loss margins
def build_cumulative_margin(game_list):
    cummarge = {}
    for game in game_list:
        update_game_dict(cummarge, game)
    return cummarge

# Get this years teams
def build_teamlist(filename, team_filter):
    this_years_teams = open(filename, "r")
    relevant_teams = []
    for line in this_years_teams:
        team = line.strip()
        if team in team_filter:
            relevant_teams.append(team)
        else:
            print "Warning! Team " + team + " not found in data!"
    this_years_teams.close
    return relevant_teams

# Create a new dict with just the relevant teams
def build_relevant_cum_margin(relevant, cum_marg):
    relevant_scores = {}
    for team in cum_marg:
            if team in relevant:
                    relevant_scores[team] = cum_marg[team]
    return relevant_scores

def main():
    anniv = datetime.date(2010, 1, 23)
    years = range(2000, 2014, 1)
    
    get_game_data_by_years(years)
    gamelist = generate_gamelist_by_date(anniv, years)
    margins = build_cumulative_margin(gamelist)
    thisyears = build_teamlist("teamlist.txt", margins)
    relevant_margins = build_relevant_cum_margin(thisyears, margins)

    sorted_winners = sorted(relevant_margins.iteritems(), key=operator.itemgetter(1), reverse=True)
    pprint.pprint(sorted_winners)

if __name__ == "__main__":
    main()
    


