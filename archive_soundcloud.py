#!/usr/bin/env python3

from urllib.request import urlopen

import csv
import io
import json
import os
import shutil
import sys

# Media roots radio
USER_ID = 1808429
CLIENT_ID = 'JlZIsxg2hY5WnBgtn3jfS0UYCl0K8DOg'

def main(argv=None):

    # get all tracks
    if os.path.exists("all_tracks.json"):
        with open("all_tracks.json") as f:
            all_tracks = json.load(f)
    else:
        all_tracks = []
        href = 'https://api-v2.soundcloud.com/users/%d/tracks?representation=&limit=20&offset=0&linked_partitioning=1&app_version=1502368172' % (USER_ID,)
        while href is not None:
            href += '&client_id=%s' % (CLIENT_ID,)
            print("going to", href)
            with urlopen(href) as resp:
                data = json.load(io.TextIOWrapper(resp))
            all_tracks.extend(data['collection'])
            href = data.get('next_href')

        with open("all_tracks.json", "w") as f:
            json.dump(all_tracks, f, indent=2)

    # get all comments
    if os.path.exists("all_comments.json"):
        with open("all_comments.json") as f:
            all_comments = json.load(f)
    else:
        # now get all comments
        all_comments = []
        for track in all_tracks:
            href = 'https://api.soundcloud.com/app/v2/tracks/%d/comments?limit=20&offset=0&linked_partitioning=1&app_version=1502368172' % (track['id'],)
            href += '&client_id=%s' % (CLIENT_ID,)
            while href is not None:
                print("going to", href)
                with urlopen(href) as resp:
                    data = json.load(io.TextIOWrapper(resp))
                all_comments.extend(data['collection'])
                href = data.get("next_href")

        with open("all_comments.json", "w") as f:
            json.dump(all_comments, f, indent=2)

    # create tracks csv
    with open("all_tracks.csv", "w", newline='') as csvfile:
        writer = csv.writer(csvfile)

        columns = ["id", "created_at", "last_modified", "display_date", "reposts_count", "playback_count", "likes_count", "duration", "artwork_url", "permalink_url", "title", "description"]

        writer.writerow(columns)
        for track in all_tracks:
            writer.writerow([track[col] for col in columns])


    with open("all_comments.csv", "w", newline='') as csvfile:
        writer = csv.writer(csvfile)

        columns = ["id", "track_id", "created_at", "thread_id", "username", "body"]
        writer.writerow(columns)
        for comment in all_comments:
            writer.writerow([comment["user"]["username"]
                             if col == "username" else
                             comment["timestamp"]
                             if col == "thread_id" else
                             comment[col]
                             for col in columns])

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
