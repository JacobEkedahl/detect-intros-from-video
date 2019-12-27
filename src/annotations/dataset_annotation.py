
import sys
import json 
import os 
import re

import db.annotation_repo as ann_repo
from db.annotation_repo import Annotation

import utils.ui as ui 
import utils.time_handler as time_handler 


def manual_annotation(path, url, tag, start, end):

    if not time_handler.validate_timeformat(start) or not time_handler.validate_timeformat(end):
        print("Error: Invalid time format.")
        return

    if "?start=auto" in url: 
        url = url.split("?start=auto")[0]

    result = ann_repo.find_by_tag_url(url, tag)
    if len(result) > 0:
        value = result[0]
        print("Warning: %s was saved previously with %s - %s." % (value['url'], value['start'], value['end']))
        print("Do you want to override it? y/n")
        if not ui.force_query_yes_or_no():
            return len(ann_repo.find_by_tag(tag))

    ann_repo.insert(Annotation(url, tag, start, end))
    print("%s saved for %s as (%s - %s)" % (tag, url, start, end))
    return len(ann_repo.find_by_tag(tag))


start = ""
end = ""
tag = "intro"
path = "data/dataset.json"
url = ""

def execute(argv):
    doCount = False 
    for i in range(1, len(argv)):
        if (argv[i] == "-s" or argv[i] == "-start") and i + 1 < len(argv):
            start = argv[i + 1]
        elif (argv[i] == "-e" or argv[i] == "-end") and i + 1 < len(argv):
            end = argv[i + 1]
        elif (argv[i] == "-t" or argv[i] == "-tag") and i + 1 < len(argv):
            tag = argv[i + 1]
        elif (argv[i] == "-url") and i + 1 < len(argv):
            url = argv[i + 1]
        elif(argv[i] == "-count"):
            doCount = True
    
    if (url != "" and tag != "" and start != "" and end != "" and path != ""):
        count = manual_annotation(path, url, tag, start, end)
        if doCount:
            print("Total %s count: %d " % (tag, count))
    else:
        print("Error: Not enough arguments provided") 

   