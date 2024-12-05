# fds-abgeordnetenwatch_polls_scraper

## Install

```
git clone git@github.com:okfde/fds-abgeordnetenwatch_polls_scraper.git
cd fds-abgeordnetenwatch_polls_scraper
python -m venv polls
source ./polls/bin/activate
pip install -r requirements.txt
```

## Config

Get `legislature`-id from https://www.abgeordnetenwatch.de/api/v2/parliament-periods (e.g. `132` is "Bundestag 2021-2025")

Set the proper value in `scrape.py`.

## Execute

Run `python ./scrape.py`.

When the script is done you will find the scraped values in `votes.json` and `votes.csv`.
