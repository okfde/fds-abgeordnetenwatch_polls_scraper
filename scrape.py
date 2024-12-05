"""
Scrape poll data from abgeordnetenwatch
"""

from pprint import pprint
import json
import traceback
import requests

# pylint: disable=line-too-long
# pylint: disable=consider-using-dict-items
# pylint: disable=bare-except
# pylint: disable=broad-exception-caught
# pylint: disable=invalid-name

legislature = 132
range_end = 1000

URL = f"https://www.abgeordnetenwatch.de/api/v2/polls?field_legislature%5Bentity.id%5D={legislature}&range_end={range_end}"

resp = requests.get(url=URL)
polls = resp.json()

if "meta" in polls:
    print(f"Status : {polls['meta']['status']}")
    print(f"Results: {polls['meta']['result']['count']}")
    print("")

i = 0
err = 0
vote_results = {}
for poll in polls["data"]:
    i = i + 1
    POLL_URL = "https://www.abgeordnetenwatch.de/api/v2/polls/"+str(poll['id'])
    params = {
        "related_data": "votes",
        "range_end": 1
    }
    poll_resp = requests.get(url=POLL_URL, params=params)
    poll_data = poll_resp.json()

    if range_end < polls['meta']['result']['count']:
        print("WARNING: Got more results than range_end, results will be incomplete!")

    try:
        print(f"Request    : {i}/{polls['meta']['result']['count']}")
        print(f"API call   : {poll_resp.url}")
        print(f"Poll       : {poll['label']}")
        print(f"URL        : {poll['abgeordnetenwatch_url']}")
        print(f"Legislature: {poll['field_legislature']['label']}")
        print(f"Topics     :")

        if not poll["label"] in vote_results:
            vote_results[poll["label"]] = {}
            vote_results[poll["label"]]["meta"] = {
                "id": i,
                "url": poll['abgeordnetenwatch_url'],
                "topics": [],
                "date": poll['field_poll_date']
            }

            if poll["field_topics"] is not None:
                for topic in poll["field_topics"]:
                    vote_results[poll["label"]]["meta"]["topics"].append(topic["label"])
                    print(f"              * {topic['label']}")
            else:
                vote_results[poll["label"]]["meta"]["topics"].append("None")
                print(f"              * None")

        for vote in poll_data["data"]["related_data"]["votes"]:
            if not "label" in vote["fraction"]:
                vote["fraction"] = {
                    "label": "Unknown"
                }
            if not "votes" in vote_results[poll["label"]]:
                vote_results[poll["label"]]["votes"] = {}
            if not vote["fraction"]["label"] in vote_results[poll["label"]]["votes"]:
                vote_results[poll["label"]]["votes"][vote["fraction"]["label"]] = {
                    "no_show": 0,
                    "yes": 0,
                    "no": 0,
                    "abstain": 0
                }
            vote_results[poll["label"]]["votes"][vote["fraction"]["label"]][vote["vote"]] = vote_results[poll["label"]]["votes"][vote["fraction"]["label"]][vote["vote"]] + 1

        print("Votes      :")
        for pf in vote_results[poll["label"]]["votes"]:
            print(f'             * {pf}')
            for key, value in vote_results[poll["label"]]["votes"][pf].items():
                print(f'               * {key}: {value}')
        print(f"Date       : {poll['field_poll_date']}")
        print("")
    except Exception as e:
        err = err + 1
        print(f"Could not fully parse poll {i}")
        pprint(poll)
        print(traceback.format_exc())

if err > 0:
    print(f"{err} polls could not be fully parsed")

# json
with open("votes.json", "w", encoding="utf-8") as f:
    json.dump(vote_results, f)
f.close()

# csv
csv_lines = []
csv_lines.append("id, vote, fraction, no_show, yes, no, abstain, topics, date, URL")
for vote in vote_results:
    for fraction in vote_results[vote]["votes"]:
        vote_name = vote.replace("\"", "'")
        csv_lines.append(f'{vote_results[vote]["meta"]["id"]}, "{vote_name}", "{fraction}", "{vote_results[vote]["votes"][fraction]["no_show"]}", "{vote_results[vote]["votes"][fraction]["yes"]}", "{vote_results[vote]["votes"][fraction]["no"]}", "{vote_results[vote]["votes"][fraction]["abstain"]}", "{vote_results[vote]["meta"]["topics"]}", "{vote_results[vote]["meta"]["date"]}", "{vote_results[vote]["meta"]["url"]}"')

with open("votes.csv", "w", encoding="utf-8") as f:
    for line in csv_lines:
        f.write(line)
        f.write("\n")
f.close()
