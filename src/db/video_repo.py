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
    *   get_shows()
    *   get_show_seasons(show):


    *   find_by_presence_of_key(key)
    *   find_all_with_intro_prediction()
    *   find_all_with_intro_annotation():

    *   save_after_download(url, mp4_fullpath)
    *   set_downloaded_flag(url, flag)
    *   change_fullpath(file, fullpath)
    *   set_data_by_file(file, key, data):
    *   set_data_by_url(url, key, data):

    *   set_intro_prediction(url, start, end)
    *   set_intro_annotation(url, start, end)
    
    *   delete_by_file(videoFileName):
    *   delete_by_url(url):
    *   delete_show(show)

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


INTRO_ANNOTATION_KEY    = 'intro_ann'
INTRO_PREDICTION_KEY    = 'intro_pre'
PREINTRO_ANNOTATION_KEY = 'prei_ann'
PREVIOUS_ANNOTATION_KEY = 'prev_ann'
URL_KEY                 = 'url'
SHOW_KEY                = 'show'
TITLE_KEY               = 'title'
SEASON_KEY              = 's'
EPISODE_KEY             = 'e'
DOWNLOADED_KEY          = 'dl'

secret = None
with open(".secret.json") as json_file:
    secret = json.load(json_file)
dbName = secret['dbname']
url = secret['url']
mongoClient = pymongo.MongoClient(url)
db = mongoClient[dbName]
videoCollection = db["videos"]


def insert(video):
    if not isinstance(video, Video):
        raise TypeError('Inappropriate type: {}, Expected: {}.'.format(type(video), type(Video)))
    if find_by_url(video.url) is not None: 
        return None
    return videoCollection.insert_one({
        SHOW_KEY: video.show,
        TITLE_KEY: video.title, 
        SEASON_KEY: video.season, 
        EPISODE_KEY: video.episode, 
        URL_KEY: video.url, 
        DOWNLOADED_KEY: video.downloaded
    }).inserted_id

def find_all():
    return list(videoCollection.find())

def find_all_not_dl():
    return list(videoCollection.find({DOWNLOADED_KEY: False}))

def find_all_dl():
     return list(videoCollection.find({DOWNLOADED_KEY: True}))

def find_by_url(url):
    return videoCollection.find_one({ URL_KEY: url})

def find_by_urls(urls):
    return list(videoCollection.find({ URL_KEY: {
         "$in": urls 
         }
    }))

def find_by_file(filename):
    return videoCollection.find_one({"file": filename})

def find_by_show(show):
    return list(videoCollection.find({SHOW_KEY: show}))

def find_by_show_not_dl(show):
    return list( videoCollection.find({
        "$and": [
            {SHOW_KEY: show}, 
            {DOWNLOADED_KEY: False}
        ]
    }))

def find_by_show_and_season(show, season):
    return list( videoCollection.find({
        "$and": [
            {SHOW_KEY: show}, 
            {SEASON_KEY: season}
        ]
    }))
    
def find_by_show_and_season_not_dl(show, season):
    return list( videoCollection.find({
        '$and': [
            {SHOW_KEY: show}, 
            {SEASON_KEY: season},
            {DOWNLOADED_KEY: False}
        ]
    }))

def find_by_show_season_episode(show, season, episode):
    return list( videoCollection.find({
    '$and': [
        {SHOW_KEY: show}, 
        {SEASON_KEY: season},
        {EPISODE_KEY: episode}
    ]
}))

def find_by_presence_of_key(key):
    return list(videoCollection.find({key: {
            "$exists": True 
        }
    }))

def find_all_with_intro_prediction():
    return find_by_presence_of_key(INTRO_PREDICTION_KEY)

def find_all_with_intro_annotation():
    return find_by_presence_of_key(INTRO_ANNOTATION_KEY)



# TODO: Remove? 
def save_after_download(url, mp4_fullpath):
    return videoCollection.update_one({ URL_KEY: url }, 
    {
        "$set": {
             DOWNLOADED_KEY: True, 
             "file": os.path.basename(mp4_fullpath),
             "fullpath": mp4_fullpath
        }
    }, upsert = False).matched_count

# TODO: Remove? 
def change_fullpath(file, fullpath):
    return videoCollection.update_one({ "file": file }, 
    {
        "$set": {
             "fullpath": fullpath
        }
    }, upsert = False).matched_count

# TODO: Remove ? 
def set_downloaded_flag(url, flag):
    return set_data_by_url(url, DOWNLOADED_KEY, flag)

def set_data_by_file(videoFileName, key, data):
    return videoCollection.update_one({ "file": videoFileName }, 
    {
        "$set": { key: data }
    }, upsert = False).matched_count

def set_data_by_url(url, key, data):
    return videoCollection.update_one({ URL_KEY: url }, 
    {
        "$set": { key: data }
    }, upsert = False).matched_count

def unset_data_by_url(url, key):
     return videoCollection.update_one({ URL_KEY: url }, 
    {
        "$unset": key 
    }, upsert = False).matched_count

def set_intro_prediction(url, start, end):
    return set_data_by_url(url, INTRO_PREDICTION_KEY, { "start": start, "end": end } )

def set_intro_annotation(url, start, end):
    return set_data_by_url(url, INTRO_ANNOTATION_KEY, { "start": start, "end": end } )

def get_shows():
    return list(videoCollection.distinct(SHOW_KEY))

def get_show_seasons(show):
    return list(videoCollection.distinct(SEASON_KEY, {SHOW_KEY: show})) 

def delete_by_file(videoFileName):
    return videoCollection.delete_one({"file": videoFileName}).deleted_count

def delete_by_url(url):
    return videoCollection.delete_one({URL_KEY: url}).deleted_count

def delete_by_show(show):
    return videoCollection.delete_many({SHOW_KEY: show}).deleted_count

