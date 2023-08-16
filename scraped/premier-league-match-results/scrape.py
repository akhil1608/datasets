import requests
from bs4 import BeautifulSoup
import numpy as np

def getResult(f, a):
    result = "Won" if f > a else ("Lost" if f < a else "Drew")
    score = "{0}-{1}".format(f, a)
    return result, score

teams = ["Arsenal", "Aston Villa", "Burnley", "Bournemouth", "Brentford", "Brighton", "Crystal Palace", "Chelsea", "Everton", "Fulham", "Liverpool", "Luton Town", "Manchester City", "Manchester United", "Newcastle United", "Nottingham", "Tottenham", "Sheffield United", "West Ham United", "Wolverhampton"]
collected = [["Year", "Season", "Team", "Opponent", "Result", "Score", "Goals For", "Goals Against"]]
for yy in range(1992, 2023):
    # Making a GET request
    r = requests.get("https://www.worldfootball.net/all_matches/eng-premier-league-{0}-{1}/".format(yy, yy+1))
    # Parsing the HTML
    soup = BeautifulSoup(r.content, 'html.parser')
    tr = soup.find_all('tr')[1:13]
    for team in teams:
        for td in tr:
            anchor = td.find_all("a")
            if len(anchor) == 4:
                anchor.pop(0)
            if len(anchor) == 3:
                if team in anchor[0].text or team in anchor[1].text:
                    # season
                    year, season = yy, "{0}-{1}".format(str(yy)[-2:], str(yy + 1)[-2:])
                    # team and their opponent
                    t, o = (0,1) if team in anchor[0].text else (1,0)
                    team, opponent = anchor[t].text, anchor[o].text
                    # goals for and against
                    scores = anchor[2].text.split(":")
                    gf, ga = scores[t].split(" ")[0], scores[o].split(" ")[0]
                    # match result
                    result, score = getResult(int(gf), int(ga))
                    collected.append([year, season, team, opponent, result, score, gf, ga])
np.savetxt("opening_day.csv", collected, delimiter =",", fmt ='%s')