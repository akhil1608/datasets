import requests
from bs4 import BeautifulSoup
import numpy as np
import time

# constants
metrics = []
metrics.extend(["game", "possession_home", "possession_away"])
metrics.extend(["passing_home_attempts", "passing_away_attempts", "passing_home_success", "passing_away_success", "passing_home_accuracy", "passing_away_accuracy"])
metrics.extend(["shots_home", "shots_away", "shots_on_home", "shots_on_away", "shot_accuracy_home", "shot_accuracy_away"])
metrics.extend(["saves_home", "saves_away", "saves_made_home", "saves_made_away", "save_percent_home", "save_percent_away"])
root = "https://fbref.com"
# helper
def clean(s, safe=""):
    return s.replace("\n", safe).replace("\r", safe).replace("\t", safe).replace("\xa0", safe)
def clearEmptyItems(lst):
    return [x.strip() for x in lst if x]
# get list of match report links
r = requests.get(root + "/en/comps/106/schedule/Womens-World-Cup-Scores-and-Fixtures")
soup = BeautifulSoup(r.content, "html.parser")
results = soup.findAll("td", {"data-stat" : "match_report"})
# remove duplicates
results = list(dict.fromkeys(results))
# loop over each match report
game = 0
stats = [metrics]
events = {}
for result in results[:10]:
    if result.find("a"):
        link = root + result.find("a").get("href")
        game += 1
        game_stat = [game]
        print(game, link)
        stat_r = requests.get(link)
        stat_soup = BeautifulSoup(stat_r.content, "html.parser")
        # scrape stats section
        stats_div = stat_soup.find("div", {"id": "team_stats"})
        stats_tr = stats_div.findChildren("tr")
        # possession
        possession = stats_tr[2].findAll("strong")
        possession_home, possession_away = possession[0].text, possession[1].text
        game_stat.extend([possession_home, possession_away])
        # passing
        passing = stats_tr[4].findAll("strong")
        passing_h, passing_a = clean(passing[0].parent.text, " ").split(" "), clean(passing[1].parent.text, " ").split(" ")
        passing_home_attempts, passing_home_success, passing_home_accuracy = passing_h[2], passing_h[0], passing_h[4] if passing_h[4] != "%" else "0%"
        passing_away_attempts, passing_away_success, passing_away_accuracy = passing_a[4], passing_a[2], passing_a[0] if passing_a[0] != "%" else "0%"
        game_stat.extend([passing_home_attempts, passing_away_attempts, passing_home_success, passing_away_success, passing_home_accuracy, passing_away_accuracy])
        # shooting
        shooting = stats_tr[6].findAll("strong")
        shooting_h, shooting_a = clean(shooting[0].parent.text, " ").split(" "), clean(shooting[1].parent.text, " ").split(" ")
        shots_home, shots_on_home, shot_accuracy_home = shooting_h[2], shooting_h[0], shooting_h[4] if shooting_h[4] != "%" else "0%"
        shots_away, shots_on_away, shot_accuracy_away = shooting_a[4], shooting_a[2], shooting_a[0] if shooting_a[0] != "%" else "0%"
        game_stat.extend([shots_home, shots_away, shots_on_home, shots_on_away, shot_accuracy_home, shot_accuracy_away])
        # saves
        saves = stats_tr[6].findAll("strong")
        saves_h, saves_a = clean(saves[0].parent.text, " ").split(" "), clean(saves[1].parent.text, " ").split(" ")
        saves_home, saves_made_home, save_percent_home = saves_h[2], saves_h[0], saves_h[4] if saves_h[4] != "%" else "0%"
        saves_away, saves_made_away, save_percent_away = saves_a[4], saves_a[2], saves_a[0] if saves_a[0] != "%" else "0%"
        game_stat.extend([saves_home, saves_away, saves_made_home, saves_made_away, save_percent_home, save_percent_away])
        stats.append(game_stat)

        # scrape events section
        events_div = stat_soup.find("div", {"id": "events_wrap"})
        game_events = events_div.find_all("div", class_="event a")
        game_events.extend(events_div.find_all("div", class_="event b"))
        # home
        for event in game_events:
            details = event.findChildren("div", recursive=False)
            event_time = clearEmptyItems(clean(details[0].text, " ").split("  "))[0]
            event_details = clearEmptyItems(clean(details[1].text, " ").split("  "))
            # substitute
            if "for" in event_details[1]:
               continue
            # penalty
            elif "Penalty" in event_details[1]:
                if "Kick" in event_details[1]:
                    primary, secondary, info = event_details[0], "", "Goal (P)"
                elif "Miss" in event_details[1]:
                    primary, secondary, info = event_details[0], "", "Penalty Miss"
                elif "Save" in event_details[1]:
                    primary, secondary, info = event_details[2], event_details[0], "Penalty Saved"
            # goal
            elif "Goal" in event_details[1]:
                primary, secondary, info = event_details[0].strip(), "", "Goal"
            elif len(event_details) > 3 and "Goal" in event_details[3]:
                primary, secondary, info = event_details[0], event_details[2], "Goal"
            else:
                continue
        events[event_time] = [primary, secondary, info]
        # fbref dot com allows a maximum of 20 requests per minute
        # sleep time set to 5s (12 req/min) [min sleep time 3s]
        time.sleep(5)
events = dict(sorted(events.items()))
print(events)
#np.savetxt("match_stats.csv", stats, delimiter=",", fmt='%s')