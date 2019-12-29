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
    *   find_by_show(targetShow)
    *   find_by_show_not_dl(targetShow)
    *   find_by_show_and_season(targetShow, season)
    *   find_by_show_and_season_not_dl(targetShow, season)
    *   save_after_download(url, mp4_fullpath)
    *   set_downloaded_flag(url, flag)
    *   change_fullpath(file, fullpath)
    *   set_scenes(videoFileName, scenes):
    *   get_shows()
    *   get_show_seasons(targetShow):
    *   delete_by_file(videoFileName):
    *   delete_by_url(url):
    *   delete_show(targetShow)
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

def find_by_show(targetShow):
    return list(videoCollection.find({"show": targetShow}))

def find_by_show_not_dl(targetShow):
    return list( videoCollection.find({
        "$and": [
            {"show": targetShow}, 
            {"downloaded": False}
        ]
    }))

def find_by_show_and_season(targetShow, season):
    return list( videoCollection.find({
        "$and": [
            {"show": targetShow}, 
            {"season": season}
        ]
    }))
    
def find_by_show_and_season_not_dl(targetShow, season):
    return list( videoCollection.find({
        '$and': [
            {'show': targetShow}, 
            {"season": season},
            {"downloaded": False}
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
    return videoCollection.update_one({ "url": url }, 
    {
        "$set": { "downloaded": flag}
    }, upsert = False).matched_count

def set_scenes(videoFileName, scenes):
    return videoCollection.update_one({ "file": videoFileName }, 
    {
        "$set": { "scenes": scenes}
    }, upsert = False).matched_count

def set_prediction(url, tag, start, end):
    return videoCollection.update_one({ "url": url }, 
    {
        "$set": { 
           tag: {
               "start": start,
               "end": end
           }
        }
    }, upsert = False).matched_count

def get_shows():
    return list(videoCollection.distinct("show"))

def get_show_seasons(targetShow):
    return list(videoCollection.distinct("season", {"show": targetShow})) 

def delete_by_file(videoFileName):
    return videoCollection.delete_one({"file": videoFileName}).deleted_count

def delete_by_url(url):
    return videoCollection.delete_one({"url": url}).deleted_count

def delete_show(targetShow):
    return videoCollection.delete_many({"show": targetShow}).deleted_count

