"""
    *   insert(srcs_annotation)

    *   find_by_tag(tag)
    *   find_by_tag_show(tag, show)
    *   find_by_tag_show_season(tag, show, season)
    *   get_shows()
    *   get_show_seasons(show)
    *   delete_by_url(url)
    *   drop_collection()
    *   get_prediction_comparison(url, tag)
    
"""
import pymongo
import json 
import db.video_repo as video_repo

class Annotation:
    """ Class containing annotation data """
    def __init__(self, url, tag, start, end):
        self.url = url
        self.tag = tag 
        self.start = start 
        self.end = end

secret = None
with open(".secret.json") as json_file:
    secret = json.load(json_file)    
dbName = secret['dbname']
url = secret['url']
mongoClient = pymongo.MongoClient(url)
db = mongoClient[dbName]
annotationCollection = db["annotations"]


def insert(srcs_annotation):
    if not isinstance(srcs_annotation, Annotation):
        raise TypeError('Inappropriate type: {}, Expected: {}.'.format(type(srcs_annotation), type(Annotation)))
    video = video_repo.find_by_url(srcs_annotation.url)
    if video is None: 
        print("Error: %s video does not exists inside the video repository. This is likely because the web scraper failed to find it." % srcs_annotation.url)
        return 
    if len(find_by_tag_url(srcs_annotation.url, srcs_annotation.tag)) > 0:
        print("Warning: updating: %s %s" % (srcs_annotation.url, srcs_annotation.tag))
        # Update 
        annotationCollection.update_one(
        {
            "$and": [
                {"url": srcs_annotation.url}, 
                {"tag": srcs_annotation.tag}
            ]
        }, 
        {
            "$set": {
                "start": srcs_annotation.start,
                "end": srcs_annotation.end
            }
        }, upsert = False)
        return 
    srcs_annotation.season = video['season']
    srcs_annotation.episode = video['episode']
    srcs_annotation.show = video['show']
    x = annotationCollection.insert_one(srcs_annotation.__dict__)
    return x.inserted_id

def find_by_tag(tag):
    return list(annotationCollection.find({"tag": tag}))

def find_by_tag_url(url, tag):
    return list(annotationCollection.find({
        '$and': [
            {'url': url}, 
            {"tag": tag}
        ]
    }))


def find_by_tag_show(tag, show):
    return list(annotationCollection.find({
        '$and': [
            {'tag': tag}, 
            {"show": show}
        ]
    }))

def find_by_tag_show_season(tag, show, season):
    return list(annotationCollection.find({
        '$and': [
            {'tag': tag}, 
            {"show": show},
            {"season": season}
        ]
    }))

def get_shows():
    return list(annotationCollection.distinct("show"))

def get_show_seasons(targetShow):
    return list(annotationCollection.distinct("season", {"show": targetShow})) 

def delete_by_url(url):
    return annotationCollection.delete_many({"url": url}).deleted_count

def drop_collection():
    annotationCollection.drop()

def get_prediction_comparison(url, tag):
    video = video_repo.find_by_url(url)
    if video is None: 
        print("Error: %s video does not exists inside the video repository. This is likely because the web scraper failed to find it." % url)
        return 
    if not tag in video: 
        return None 
    ann = find_by_tag_url(url, tag)[0]
    if ann is None:
          return None
    return {
        'predicted':  video[tag],
        'actual': { 
            'start': ann['start'], 'end': ann['end'] 
        } 
    }