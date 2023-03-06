import os
import sys
from datetime import datetime, timedelta

import omglol
from thttp import request

try:
    intervals_id = os.environ["INTERVALS_ATHLETE_ID"]
    intervals_api_key = os.environ["INTERVALS_API_KEY"]

    omg_lol_username = os.environ["OMGLOL_USERNAME"]
    omg_lol_key = os.environ["OMGLOL_API_KEY"]
except KeyError:
    print("All environment variables must be configured")
    sys.exit(1)


def format_mins_seconds(d):
    d = int(d)
    minutes, seconds = divmod(d, 60)
    return f"{minutes:02}:{seconds:02}"


def get_most_recent_run():
    today = datetime.now()
    url = f"https://intervals.icu/api/v1/athlete/{intervals_id}/activities"

    response = request(
        url,
        params={
            "oldest": (today - timedelta(days=20)).isoformat().split("T")[0],
            "newest": (today + timedelta(days=1)).isoformat().split("T")[0],
        },
        basic_auth=("API_KEY", intervals_api_key),
    )

    runs = [x for x in response.json if x["type"] == "Run"]
    return runs[0]


def get_actual_kms(week_offset=0):
    today = datetime.now() + timedelta(weeks=week_offset)
    target_week = today.isocalendar().week

    url = f"https://intervals.icu/api/v1/athlete/{intervals_id}/activities"

    response = request(
        url,
        params={
            "oldest": (today - timedelta(days=20)).isoformat().split("T")[0],
            "newest": (today + timedelta(days=120)).isoformat().split("T")[0],
        },
        basic_auth=("API_KEY", intervals_api_key),
    )

    current_week_volume = []

    for event in response.json:
        start_date = datetime.fromisoformat(event["start_date_local"])
        event_week = start_date.isocalendar().week

        if event_week != target_week:
            continue

        if event.get("type", "") == "Run" and event.get("distance"):
            current_week_volume.append(event["distance"])

    return int(sum(current_week_volume) / 1000)


def get_target_kms(week_offset=0):
    today = datetime.now() + timedelta(weeks=week_offset)
    target_week = today.isocalendar().week

    url = f"https://intervals.icu/api/v1/athlete/{intervals_id}/events"

    response = request(
        url,
        params={
            "oldest": (today - timedelta(days=20)).isoformat().split("T")[0],
            "newest": (today + timedelta(days=120)).isoformat().split("T")[0],
        },
        basic_auth=("API_KEY", intervals_api_key),
    )

    current_week_planned = []

    for event in response.json:
        start_date = datetime.fromisoformat(event["start_date_local"])
        event_week = start_date.isocalendar().week

        if event_week != target_week:
            continue

        if event.get("type", "") == "Run" and event.get("distance"):
            current_week_planned.append(event["distance"])

    return int(sum(current_week_planned) / 1000)


def get_upcoming_races():
    today = datetime.now()
    url = f"https://intervals.icu/api/v1/athlete/{intervals_id}/events"

    response = request(
        url,
        params={
            "oldest": today.isoformat().split("T")[0],
            "newest": (today + timedelta(days=365)).isoformat().split("T")[0],
        },
        basic_auth=("API_KEY", intervals_api_key),
    )

    runs = [x for x in response.json if x["type"] == "Run" and x["category"].startswith("RACE_")]
    return runs


def get_yearly_stats():
    today = datetime.now()

    today.isocalendar().week

    url = f"https://intervals.icu/api/v1/athlete/{intervals_id}/activities"

    response = request(
        url,
        params={
            "oldest": f"{today.year - 1}-12-31",
            "newest": f"{today.year + 1}-01-01",
        },
        basic_auth=("API_KEY", intervals_api_key),
    )

    ytd_kms = []
    ytd_mins = []
    ytd_elevation = []

    for event in response.json:
        start_date = datetime.fromisoformat(event["start_date_local"])

        if start_date.year == today.year:
            if event.get("type", "") == "Run" and event.get("distance"):
                ytd_kms.append(event["distance"])
                ytd_mins.append(event["moving_time"] / 60)
                ytd_elevation.append(event.get("total_elevation_gain", 0))

    return (
        len(ytd_kms),
        int(sum(ytd_kms) / 1000),
        int(sum(ytd_mins)),
        int(sum(ytd_elevation)),
    )


def intervals(
    *,
    include_this_week=True,
    include_recent_run=True,
    include_year_to_date=True,
    include_upcoming_races=True,
):
    s = "## 🏃‍♂️ Running Stats and Goals (via [intervals.icu](https://intervals.icu))\n\n"

    if include_this_week:
        target_kms = get_target_kms()
        actual_kms = get_actual_kms()

        if target_kms:
            s += f"- This week: {actual_kms}/{target_kms}km\n"
        else:
            s += f"- This week: {actual_kms}km"

    if include_recent_run:
        most_recent = get_most_recent_run()
        strava_id = most_recent.get("strava_id", "")
        distance_km = most_recent["distance"] / 1000
        formatted_pace = format_mins_seconds(most_recent["moving_time"] / distance_km)
        name = most_recent["name"]

        if strava_id:
            strava_url = f"https://strava.com/activities/{strava_id}"
            s += f"- Latest Run: [{name}]({strava_url}) ({distance_km:.1f}km @ {formatted_pace} min/km)\n"
        else:
            s += f"- Latest Run: {name} ({distance_km:.1f}km @ {formatted_pace} min/km)\n"

    if include_year_to_date:
        num_runs, distance, duration, elevation = get_yearly_stats()
        s += "- Year to Date:\n"
        s += f"  - {num_runs} runs\n"
        s += f"  - {distance}km\n"
        s += f"  - {format_mins_seconds(duration).replace(':', 'h')}m of running\n"
        s += f"  - {elevation} meters of climbing\n"

    if include_upcoming_races:
        upcoming = get_upcoming_races()

        if upcoming:
            s += "- Upcoming Events:\n"

            for race in upcoming:
                race_cat = race["category"].replace("RACE_", "")
                s += f'  - ({race_cat}) {race["name"]} ({race["start_date_local"].split("T")[0]})\n'

    return s


if __name__ == "__main__":
    start_wrapper = "<!-- block intervals-now -->"
    end_wrapper = "<!-- end intervals-now -->"

    intervals_content = intervals(
        include_this_week=True,
        include_recent_run=True,
        include_year_to_date=True,
        include_upcoming_races=True,
    )

    now_page = omglol.get_now_page(omg_lol_username)
    content = now_page["content"]

    if start_wrapper in content and end_wrapper in content:
        before, _ = content.split(start_wrapper, 1)
        _, after = content.split(end_wrapper, 1)

        content = f"{before}\n\n{start_wrapper}\n{intervals_content}\n{end_wrapper}\n\n{after}"
    else:
        content = f"{content}\n\n{start_wrapper}\n{intervals_content}\n{end_wrapper}"

    omglol.update_now_page(omg_lol_username, content, omg_lol_key)
