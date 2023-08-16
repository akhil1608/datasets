import requests
from bs4 import BeautifulSoup
import numpy as np

r = requests.get("https://www.fastscore.com/world/womens-world-cup/results")
soup = BeautifulSoup(r.content, "html.parser")
divs = soup.find_all("div", class_="match-link")

stages = {"Group Stage": 48, "8th Final": 56, "Quarter Final": 60, "Semi Final": 62, "3rd Place": 63, "Final": 64}
def getStage(game):
    for stage, end_stage in stages.items():
        if game <= end_stage:
            return stage

matches = [["match", "stage", "home", "away", "goals_home", "goals_away", "extra_time", "penalties", "pens_home", "pens_away", "link"]]
for i in range(len(divs) - 1, -1, -1):
    div = divs[i]
    children = div.findChildren("div", recursive=False)

    game = len(divs) - i
    stage = getStage(game)
    link = div.get("data-href")

    teams = children[1].findChildren("div", recursive=False)
    home, away = teams[0].text.strip(), teams[1].text.strip()

    scores = children[2].find_all("div", class_="row m-0")[0].findChildren("div", recursive=False)
    goals = scores[2].findChildren("div", recursive=False)
    goals_home, goals_away = goals[0].text.strip(), goals[1].text.strip()
    et = scores[0].text.strip()
    if et == "AET":
        extra_time, penalties, pens_home, pens_away = "Yes", "No", "", ""
        result = "{0} - {1} (AET)".format(goals_home, goals_away)
    elif et == "PSO":
        pen_goals = scores[1].findChildren("div", recursive=False)
        extra_time, penalties, pens_home, pens_away = "Yes", "Yes", pen_goals[0].text.strip(), pen_goals[1].text.strip()
        result = "{0} - {1} (AET); {2} - {3} (PENS)".format(goals_home, goals_away, pens_home, pens_away)
    else:
        extra_time, penalties, pens_home, pens_away = "No", "No", "", ""
        result = "{0} - {1}".format(goals_home, goals_away)
    summary = "Match {0}: {1} v {2}: {3}".format(game, home, away, result)
    # print(summary)
    matches.append([game, stage, home, away, goals_home, goals_away, extra_time, penalties, pens_home, pens_away, link])
np.savetxt("match_results.csv", matches, delimiter =",", fmt ='%s')