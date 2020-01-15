""" """
import sys
import json 
import os 
import re

import db.video_repo as video_repo
import utils.ui as ui 
import utils.time_handler as time_handler 


def manual_annotation(path, url, tag, start, end):
    if not time_handler.validate_timeformat(start) or not time_handler.validate_timeformat(end):
        print("Error: Invalid time format.")
        return 0
    if time_handler.timestamp(start) > time_handler.timestamp(end):
        print("Error: start > end.")
        return 0
    if "?start=auto" in url: 
        url = url.split("?start=auto")[0]



    start = time_handler.str_to_seconds(start)
    end = time_handler.str_to_seconds(end)

    print("start: %s and end: %s" % (start, end))

    video = video_repo.find_by_url(url)
    if video is None:
        return -1

    if tag == "intro":    
        count = len(video_repo.find_all_with_intro_annotation())
        if video_repo.INTRO_ANNOTATION_KEY in video: 
            intro = video[video_repo.INTRO_ANNOTATION_KEY]
            print("Warning: %s was saved previously with %s - %s." % (video['url'], intro['start'], intro['end']))
            print("Do you want to override it with %s %s? y/n" % (start, end))
            if not ui.force_query_yes_or_no():
                return count
            else: 
                video_repo.set_intro_annotation(url, start, end)
                return count 
        
        video_repo.set_intro_annotation(url, start, end)
        return count + 1
    else:
        print("tag %s is not managed" % tag)
        return -1
    

    
   