__author__ = 'Will'

import sys
import json

def query_applies_to_song(q, song):
    return q in song["artist"] or q in song["lyrics"] or q in song["album"]

filename = sys.argv[1]

songs = []
with open(filename, "r") as file:
    songs = json.load(file)
    file.close()

while True:
    q = raw_input("Enter a query: ")
    filtered_songs = filter(lambda song:  query_applies_to_song(q, song), songs)
    print "query applies to ", len(filtered_songs), "songs"

    if len(filtered_songs) > 0:
        attr = raw_input("Enter attribute of song: ")
        for song in filtered_songs:
            if attr in song:
                print song[attr]