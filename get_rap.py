__author__ = 'Will'

from bs4 import BeautifulSoup
import requests
import sys
import json

def get_soup(url):
    return BeautifulSoup(requests.get(url).text, "html5lib")

base_url = "http://ohhla.com"
artist_url_srcs = [
    base_url + "/all.html",
    base_url + "/all_two.html",
    base_url + "/all_three.html",
    base_url + "/all_four.html",
    base_url + "/all_five.html"
]

# all song pages on this site end in .txt
# find them
def find_text_links(link, tried_links=None, max_text_links=sys.maxint):
    if tried_links is None:
        tried_links = []

    if link not in tried_links:
        print "finding link: ", link, " ... number of tried links: ", len(tried_links)
        soup = get_soup(link)
        tried_links.append(link)

        links = soup.find_all("a")
        # remove links without href
        links = map(lambda l: l.get("href"),
                    filter(lambda l: l.get("href") is not None, links))

        # only want links associated with base_url
        links = filter(lambda l: base_url in l or "http" not in l, links)

        # only ls with .txt at the end
        txt_links = filter(lambda l: len(l) > 4 and l[-4:] == ".txt", links)

        # links to follow recursively
        links_to_try = filter(lambda l: l not in tried_links + txt_links, links)

        if len(links_to_try) > 0:
            for link_to_try in links_to_try:
                if "http://" not in link_to_try:
                    link_to_try = base_url + "/" + link_to_try
                if len(txt_links) < max_text_links:
                    txt_links += find_text_links(link_to_try, tried_links)
        return txt_links
    else:
        return []


def get_song_from_txt_link(link):
    soup = get_soup(link)
    pre = soup.find("pre")

    if pre is not None:
        text = pre.get_text()
        lines = text.split("\n")
        artist = "unknown"
        song = "unknown"
        album = "unknown"
        lyrics = "unknown"
        lyrics_start_on_line = 0

        while "unknown" in [artist, song, album] and len(lines) > 0:
            lyrics_start_on_line += 1
            line = lines[0].lower()
            lines = lines[1:]
            if "artist: " in line:
                artist = line.split(":")[1].strip()
            elif "song: " in line:
                song = line.split(":")[1].strip()
            elif "album: " in line:
                album = line.split(":")[1].strip()

        lyrics = " ".join(lines[lyrics_start_on_line - 1:])

        return {
            "artist": artist,
            "song": song,
            "album": album,
            "lyrics": lyrics
        }
    else:
        return {
            "artist": "unknown",
            "song": "unknown",
            "album": "unknown",
            "lyrics": "unknown"
        }

filename = sys.argv[1]
max_links = sys.maxint
if len(sys.argv) > 2:
    max_links = int(sys.argv[2])

print "starting, filename ", filename, " max_links: ", max_links
songs = []
txt_links = find_text_links(base_url, [], max_links)

# save links
links_file_name = "links-" + filename
print "Done finding links, found: ", len(txt_links)
with open(links_file_name,"w+") as file:
    json.dump(txt_links, file)
    file.close()

for i in range(len(txt_links)):
    link = txt_links[i]
    if "http" not in link:
        link = base_url + "/" + link
    try:
        songs.append(get_song_from_txt_link(link))
    except Exception as e:
        print "!!!!!!!!!!!!!", e
    if i % 1000 == 0:
        print i , "/", len(txt_links), " (", float(i)/len(txt_links), ")"

print "saving to ", filename, "..."
with open(filename, "w+") as file:
    json.dump(songs, file)
    file.close()
print "done!"