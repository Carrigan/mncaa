from massey import *
import os
import datetime
import operator
import pprint

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

# Add or subtract a game's margins from each team involved in a game
def append_game_dict(game_dict, game):
    w, l, m = game.winner, game.loser, (float(game.margin) / (game.score_1 + game.score_2))
    if w not in game_dict:
        game_dict[w] = 0
    if l not in game_dict:
        game_dict[l] = 0
    game_dict[w] += m
    game_dict[l] -= m

# Generate a list of Games from the massery files.
def generate_gamelist(desired_years, filter=None):
    games = []
    for year in desired_years:
        print "------- " + str(year) + " -------"
        csv = open(generate_game_filename(year), "r")
        team_dict = create_team_dictionary(year)
        for line in csv:
            parsed = parse_game_line(line)
            if filter:
                if( filter(parsed) ):
                    games.append(Game(tokens=parsed, team_dict=team_dict))
            else:    
                games.append(Game(tokens=parsed, team_dict=team_dict))
    return games


# Create a dictionary of all the teams that played on 1/23 and
# sum their win/loss margins
def build_cumulative_margin(game_list):
    cummarge = {}
    for game in game_list:
        append_game_dict(cummarge, game)
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

# This is a test filter to be used when making margins
def anniversary_filter(parsed_str):
    anniv = datetime.date(2010, 1, 23)
    try:
        date_of_game = get_game_date(parsed_str)
    except:
        return False
    return ((date_of_game.day == anniv.day) and (date_of_game.month == anniv.month))


def main():
    anniv = datetime.date(2010, 1, 23)
    years = range(2000, 2014, 1)
    
    # Grab all of the massey CSVs
    download_massey_csvs(years)

    # Create a list of all games filtered by anniversary_filter
    gamelist = generate_gamelist(years, filter=anniversary_filter)

    # Use this list to accumulate the win/loss margins
    margins = build_cumulative_margin(gamelist)

    # Take the win loss margins of all teams and strip out any teams not in
    # this year's NCAA bracket.
    thisyears = build_teamlist("teamlist.txt", margins)
    relevant_margins = build_relevant_cum_margin(thisyears, margins)

    # 1. Sort the scores from highest to lowest
    # 2. Enter them into a bracket
    # 3. ?
    # 4  Win 1,000,000,000 from Mr. Buffet
    sorted_winners = sorted(relevant_margins.iteritems(), key=operator.itemgetter(1), reverse=True)
    pprint.pprint(sorted_winners)

if __name__ == "__main__":
    main()
