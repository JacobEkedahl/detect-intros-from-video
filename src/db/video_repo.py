""" 
    video_repo.py is a database interface to all videos managed by the program.

    API: 

    *   insert(video)
    *   find_all()
    *   find_all_not_dl(): 
    *   find_all_dl()
    *   find_by_url(url)
    *   find_by_urls(urls)
    *   find_by_file(videoFileName)
    *   find_by_show(show)
    *   find_by_show_not_dl(show)
    *   find_by_show_and_season(show, season)
    *   find_by_show_and_season_not_dl(show, season)
    *   find_by_show_season_episode(show, season, episode)
    *   save_after_download(url, mp4_fullpath)
    *   set_downloaded_flag(url, flag)
    *   change_fullpath(file, fullpath)
    *   set_data_by_file(file, key, data):
    *   set_data_by_url(url, key, data):
    *   get_shows()
    *   get_show_seasons(show):
    *   delete_by_file(videoFileName):
    *   delete_by_url(url):
    *   delete_show(show)
    *   set_prediction(url, tag, start, end)
"""

import pymongo
import json
import os 

from pathlib import Path

class Video:
    """ Class containing video information """

    def __init__(self, show="", title="", season=0, episode=0, url="", downloaded=False):
        self.show = show
        self.title = title
        self.season = season
        self.episode = episode 
        self.url = url
        self.downloaded = downloaded
        
    def __repr__(self):
        return "Video('{}', '{}', {}, {}, '{}', {})".format(self.show, self.title, self.season, self.episode, self.url, self.downloaded)

    def setDwonloaded(self, flag):
        self.downloaded = flag

    def hasDownloaded(self):
        return self.downloaded 

    @property
    def filename(self):
        return '{}.s{:02}e{:02}'.format(self.show, self.season, self.episode)


def generate_file_name(show, title, season, episode):
    return Video(show, title, season, episode).filename


secret = None
with open(".secret.json") as json_file:
    secret = json.load(json_file)
    
dbName = secret['dbname']
url = secret['url']
mongoClient = pymongo.MongoClient(url)
db = mongoClient[dbName]
videoCollection = db["videos"]


# API

def insert(srcs_video):
    if not isinstance(srcs_video, Video):
        raise TypeError('Inappropriate type: {}, Expected: {}.'.format(type(srcs_video), type(Video)))
    if find_by_url(srcs_video.url) is not None: 
        return None
    x = videoCollection.insert_one(srcs_video.__dict__)
    return x.inserted_id

def find_all():
    return list(videoCollection.find())

def find_all_not_dl():
    return list(videoCollection.find({"downloaded": False}))

def find_all_dl():
     return list(videoCollection.find({"downloaded": True}))

def find_by_url(url):
    return videoCollection.find_one({"url": url})

def find_by_urls(urls):
    return list(videoCollection.find({ "url": {
         "$in": urls 
         }
    }))

def find_by_file(filename):
    return videoCollection.find_one({"file": filename})

def find_by_show(show):
    return list(videoCollection.find({"show": show}))

def find_by_show_not_dl(show):
    return list( videoCollection.find({
        "$and": [
            {"show": show}, 
            {"downloaded": False}
        ]
    }))

def find_by_show_and_season(show, season):
    return list( videoCollection.find({
        "$and": [
            {"show": show}, 
            {"season": season}
        ]
    }))
    
def find_by_show_and_season_not_dl(show, season):
    return list( videoCollection.find({
        '$and': [
            {'show': show}, 
            {"season": season},
            {"downloaded": False}
        ]
    }))

def find_by_show_season_episode(show, season, episode):
    return list( videoCollection.find({
    '$and': [
        {'show': show}, 
        {"season": season},
        {"episode": episode}
    ]
}))


def save_after_download(url, mp4_fullpath):
    return videoCollection.update_one({ "url": url }, 
    {
        "$set": {
             "downloaded": True, 
             "file": os.path.basename(mp4_fullpath),
             "fullpath": mp4_fullpath
        }
    }, upsert = False).matched_count

def change_fullpath(file, fullpath):
    return videoCollection.update_one({ "file": file }, 
    {
        "$set": {
             "fullpath": fullpath
        }
    }, upsert = False).matched_count

def set_downloaded_flag(url, flag):
    return set_data_by_url(url, "downloaded", flag)

def set_data_by_file(videoFileName, key, data):
    return videoCollection.update_one({ "file": videoFileName }, 
    {
        "$set": { key: data }
    }, upsert = False).matched_count


def set_data_by_url(url, key, data):
    return videoCollection.update_one({ "url": url }, 
    {
        "$set": { key: data }
    }, upsert = False).matched_count

def set_prediction(url, tag, start, end):
    return set_data_by_url(url, tag, {
            "start": start,
            "end": end
        }
    )

def get_shows():
    return list(videoCollection.distinct("show"))

def get_show_seasons(show):
    return list(videoCollection.distinct("season", {"show": show})) 

def delete_by_file(videoFileName):
    return videoCollection.delete_one({"file": videoFileName}).deleted_count

def delete_by_url(url):
    return videoCollection.delete_one({"url": url}).deleted_count

def delete_show(show):
    return videoCollection.delete_many({"show": show}).deleted_count

