#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pulls the live numbers the signal graphics are drawn from into data.json.

    python .github/assets/fetch_data.py && python .github/assets/generate.py

Two API calls, no auth needed. generate.py reads data.json and never touches
the network, so the artwork can always be rebuilt offline.
"""

import io
import json
import os
import datetime
import urllib.request

USER = "LennyDany-03"
HERE = os.path.dirname(os.path.abspath(__file__))
MONTHS = 12


def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": "profile-asset-builder"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8"))


def month_key(iso):
    return iso[:7]


def main():
    user = get("https://api.github.com/users/%s" % USER)
    repos = get("https://api.github.com/users/%s/repos?per_page=100&sort=pushed" % USER)
    repos = [r for r in repos if not r.get("fork")]

    # Repos by primary language, biggest first.
    langs = {}
    for r in repos:
        if r.get("language"):
            langs[r["language"]] = langs.get(r["language"], 0) + 1
    langs = sorted(langs.items(), key=lambda kv: -kv[1])

    # Pushes per month across the trailing year.
    today = datetime.date.today().replace(day=1)
    keys = []
    y, m = today.year, today.month
    for _ in range(MONTHS):
        keys.append("%04d-%02d" % (y, m))
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    keys.reverse()

    pushed = dict((k, 0) for k in keys)
    for r in repos:
        k = month_key(r["pushed_at"])
        if k in pushed:
            pushed[k] += 1

    created = dict((k, 0) for k in keys)
    for r in repos:
        k = month_key(r["created_at"])
        if k in created:
            created[k] += 1

    started = datetime.datetime.strptime(user["created_at"][:10], "%Y-%m-%d").date()
    years = (datetime.date.today() - started).days / 365.25

    # Repos carrying a homepage are the ones actually deployed and reachable --
    # a far better headline than a small star count.
    live = sum(1 for r in repos if (r.get("homepage") or "").startswith("http"))

    data = {
        "user": USER,
        "repos": user["public_repos"],
        "followers": user["followers"],
        "live": live,
        "stars": sum(r["stargazers_count"] for r in repos),
        "years": round(years, 1),
        "since": started.strftime("%b %Y"),
        "languages": langs,
        "months": keys,
        "pushed": [pushed[k] for k in keys],
        "created": [created[k] for k in keys],
        "generated": datetime.date.today().isoformat(),
    }

    io.open(os.path.join(HERE, "data.json"), "w", encoding="utf-8", newline="\n").write(
        json.dumps(data, indent=2))

    print("repos %(repos)d  live %(live)d  stars %(stars)d  followers %(followers)d  years %(years)s" % data)
    print("languages:", ", ".join("%s %d" % (k, v) for k, v in langs))
    print("pushes/mo:", data["pushed"])


if __name__ == "__main__":
    main()
