""" 
    Scrapes svtplay.se for all seasons and episodes belonging to the specified genres and saves them in a db. 
    You can specify one or more genres when using .execute(argv).
    
    Example: 
        argv = ["-g", "serier", "-g", "barn]
        scrapesvt.execute(argv)
"""

from bs4 import BeautifulSoup

import lxml
import requests
import re
import json
import os
import copy

from db import video_repo
from db.video_repo import Video 


class Show:
    def __init__(self, title, url):
        self.name = title
        self.url = url


SVT_URL = "https://www.svtplay.se"
json_data = {}
json_data['videos'] = []


def scrape_show(show, genre):
    # Extracts all json data from the show.url
    data = json.loads(re.findall(r"root\['__svtplay_apollo'\] = (\{.*?\});", requests.get(show.url).text)[0])
    video = Video(show.name, "", 0, 0, "", False )
    for element in data:
       # Extracting from metadata 
        if element.startswith('Episode:'):    
            video.title = data[element]['name']
            pos = data[element]['positionInSeason']
            if pos != "":
                try:
                    video.season = int(pos.split("Säsong ")[1].split(" —")[0])
                except:
                    video.season = 0
                try:
                    video.episode = int(pos.split("Avsnitt ")[1])
                except:
                    video.episode = 0
            else:
                video.season = 0
                video.episode = 0
        # Extracting video url if present
        elif element.startswith('$Episode:') and element.endswith('urls'):
            video.url = data[element]['svtplay']
            if video.url != "":
                video.url = SVT_URL + video.url
                if video.season == 0 or video.episode == 0: 
                    arr = video.url.split('-')
                    for i in range(0, len(arr) - 1):
                        if arr[i] == "sasong" and i + 1 < len(arr):
                            video.season = int(arr[i + 1])
                        elif arr[i] == "avsnitt" and i + 1 < len(arr):
                            video.episode = int(arr[i + 1])

                video_repo.insert(copy.copy(video)) # only videos not saved before get inserted

            video.url = ""
            video.season = 0
            video.episode = 0
            video.title = ""


def scrape_genre(genre):
    url = SVT_URL + "/genre/" + genre
    source = requests.get(url).text
    soup = BeautifulSoup(source, 'lxml')

    # grid = Program A-Ö
    grid = soup.find('div', class_='play_flex-grid lp_grid')
    if grid is None: 
        print("Could not find genre: " + genre)
        return

    # Below loop fetches the title and link of all presented shows
    i = 0
    for article in grid.find_all('article', class_='play_content-item play_grid__item'):
        meta = article.find('div', class_='play_content-item__meta')
        title = meta.h2.span.text
        link = meta.a['href']
        show = Show(title, SVT_URL + link)
        #file.write("\n%d: %s, %s\n\n" % (i, show.title, show.url))
        print("%d: %s, %s" % (i, show.name, show.url))
        scrape_show(show, genre)
        i = i + 1


def execute(argv):
    genres = []
    for i in range(1, len(argv)):
        if (argv[i] == "-g" or argv[i] == "-genre") and i + 1 < len(argv):
            genres.append(argv[i + 1])
        if (argv[i] == "help"):
            print("To scrape SVT-Play you need to specify which genres to extract data from by appending -g, followed by a genre, for each genre.")
            return
    if (len(genres) == 0):
        print("Error: no genres specified.")
        return 
    for genre in genres: 
        scrape_genre(genre)

