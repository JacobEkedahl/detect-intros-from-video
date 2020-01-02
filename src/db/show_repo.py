""" 

    Holds information related to shows.

    API: 


    *   insert(srcs_show)
    *   find_by_url(url)
    *   find_by_name(name)
    *   find_by_dir(dirname)
    *   find_all()
    *   drop_collection()

"""

import pymongo
import json
import os 

class Show: 

    """ Holds information related to shows """

    def __init__(self, name, url):
        self.name = name
        arr = url.split("/")
        self.dirname = arr[len(arr) - 1]
        self.url = url 


secret = None
with open(".secret.json") as json_file:
    secret = json.load(json_file)
dbName = secret['dbname']
url = secret['url']
mongoClient = pymongo.MongoClient(url)
db = mongoClient[dbName]
showCollection = db["shows"]

def insert(srcs_show):
    if not isinstance(srcs_show, Show):
        raise TypeError('Inappropriate type: {}, Expected: {}.'.format(type(srcs_show), type(Show)))
    if find_by_url(srcs_show.url) is not None: 
        return None
    x = showCollection.insert_one(srcs_show.__dict__)
    return x.inserted_id

def find_by_url(url):
    return showCollection.find_one({"url": url})

def find_by_name(name):
    return showCollection.find_one({"name": name})

def find_by_dir(dirname):
    return showCollection.find_one({"dir": dirname})

def find_all():
    return list(showCollection.find())

def drop_collection():
    showCollection.drop()