import requests
from bs4 import BeautifulSoup
import numpy as np

# constants
stages = {"Group Stage": 48, "8th Final": 56, "Quarter Final": 60, "Semi Final": 62, "3rd Place": 63, "Final": 64}
metrics = ["game", "stage", "home", "away", "home_img", "away_img", "goals_home", "goals_away", "extra_time", "penalties", "pens_home", "pens_away", "link"]
# helper methods
def getStage(game):
    for stage, end_stage in stages.items():
        if game <= end_stage:
            return stage
# get list of matches
r = requests.get("https://www.fastscore.com/world/womens-world-cup/results")
soup = BeautifulSoup(r.content, "html.parser")
divs = soup.find_all("div", class_="match-link")
matches = [metrics]
# iterating in reverse order since recent matches are shown first
for i in range(len(divs) - 1, -1, -1):
    div = divs[i]
    children = div.findChildren("div", recursive=False)
    # game info
    game = len(divs) - i
    stage = getStage(game)
    link = div.get("data-href")
    # request to get match details
    sub_r = requests.get(link)
    sub_soup = BeautifulSoup(sub_r.content, "html.parser")
    scorecard = sub_soup.find("div", class_="container mb-4 bg-light stadium-bg").findChildren("div", recursive=False)
    # teams
    teams = children[1].findChildren("div", recursive=False)
    home, away = teams[0].text.strip(), teams[1].text.strip()
    images = scorecard[2].find_all("img")
    home_img, away_img = images[0].get("src"), images[1].get("src")
    # goals
    scores = children[2].find_all("div", class_="row m-0")[0].findChildren("div", recursive=False)
    goals = scores[2].findChildren("div", recursive=False)
    goals_home, goals_away = goals[0].text.strip(), goals[1].text.strip()
    # extra time
    et = scores[0].text.strip()
    if et == "AET":
        goals = scores[1].findChildren("div", recursive=False)
        goals_home, goals_away = goals[0].text.strip(), goals[1].text.strip()
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
    print(summary)
    matches.append([game, stage, home, away, home_img, away_img, goals_home, goals_away, extra_time, penalties, pens_home, pens_away, link])
np.savetxt("match_results.csv", matches, delimiter =",", fmt ='%s')