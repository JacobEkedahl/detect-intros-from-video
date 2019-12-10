# ------------------------------------------------------------------------- #
# Scrapes svtplay.se for all seasons and episodes belonging to the provided #
# genres.                                                                    #
#                                                                           #
# Example usage: py ScrappySvt.py serier -cwdir C:/your-output-directory    #
#                                                                           #
# Notice:                                                                   #
# 1. You can specify multiple genres.                                       #
# 2. If you don't provide any output directory it will use a default one    #   
# 3. Any genres specified after -cwdir will be ignored                      #
# ------------------------------------------------------------------------- #

from bs4 import BeautifulSoup

import lxml
import requests
import sys
import re
import json
import os

# Change to modify the default working directory
WORKING_DIR = os.getcwd()


class Video:
    def __init__(self, title, season, episode, url):
        self.title = title
        self.season = season
        self.episode = episode
        self.url = url


class Show:
    def __init__(self, title, url):
        self.title = title
        self.url = url

SVT_URL = "https://www.svtplay.se"
genre_video_count = 0

json_data = {}
json_data['videos'] = []

# Extract all seasons episodes from a given show
def scrape_show(show, genre):

    data = json.loads(re.findall(r"root\['__svtplay_apollo'\] = (\{.*?\});", requests.get(show.url).text)[0])
    video = Video("", "", "", "")
    for k in data:
        if k.startswith('Episode:'):
            # pprint(data[k])   # display meta-data as json
            video.title = data[k]['name']
            pos = data[k]['positionInSeason']
            if pos != "":
                try:
                    video.season = int(pos.split("Säsong ")[1].split(" —")[0])
                except:
                    print("Failed to read season: " + pos)
                    video.season = 0
                try:
                    video.episode = int(pos.split("Avsnitt ")[1])
                except:
                    print("Failed to read episode: " + pos)
                    video.episode = 0
            else:
                video.season = 0
                video.episode = 0
        elif k.startswith('$Episode:') and k.endswith('urls'):
            video.url = data[k]['svtplay']
            if video.url != "":
                video.url = SVT_URL + video.url
                if video.season == 0 or video.episode == 0: 
                    arr = video.url.split('-')
                    for i in range(0, len(arr) - 1):
                        if arr[i] == "sasong" and i + 1 < len(arr):
                            video.season = int(arr[i + 1])
                        elif arr[i] == "avsnitt" and i + 1 < len(arr):
                            video.episode = int(arr[i + 1])
                file.write("\'%s\' S%02d E%02d \'%s\'\n" % (video.title, video.season, video.episode, video.url))
                json_data['videos'].append({
                    'show': show.title,
                    'url': video.url,
                    's': video.season,
                    'e': video.episode,
                })
                global genre_video_count
                genre_video_count = genre_video_count + 1
            video.url = ""
            video.title = ""
            video.season = 0
            video.episode = 0

    with open(genre + '.json', 'w') as outfile:
        json.dump(json_data, outfile)


def scrape_genre(genre):
    url = SVT_URL + "/genre/" + genre
    print("Scraping: " + url)
    
    source = requests.get(url).text
    soup = BeautifulSoup(source, 'lxml')
   
   # grid = Program A-Ö
    grid = soup.find('div', class_='play_flex-grid lp_grid')

    if grid is None: 
        print("Could not find genre: " + genre)
        return

    # Below loop fetches the title and link of all presented shows
    global genre_video_count
    genre_video_count = 0
    i = 0
    for article in grid.find_all('article', class_='play_content-item play_grid__item'):
        meta = article.find('div', class_='play_content-item__meta')
        title = meta.h2.span.text
        link = meta.a['href']
        show = Show(title, SVT_URL + link)
        file.write("\n%d: %s, %s\n\n" % (i, show.title, show.url))
        print("%d: %s, %s" % (i, show.title, show.url))
        scrape_show(show, genre)
        i = i + 1

    file.write("\n" + genre + " videos = %d" % genre_video_count)
    

if len(sys.argv) - 1 < 1:
    print("No genres specified in the argument list.")
    exit()

os.chdir(WORKING_DIR)

genres = []

for i in range(1, len(sys.argv)):
    if sys.argv[i] == "-cwdir":
        if i + 1 < len(sys.argv):
            print("Changed working directory to: " + sys.argv[i + 1])
            os.chdir(sys.argv[i + 1])
        break
    else:
        genres.append(sys.argv[i])

for genre in genres: 
    file = open(genre + ".txt", "w")
    scrape_genre(genre)
    file.close()
