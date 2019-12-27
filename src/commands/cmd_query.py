import json 

import db.video_repo as video_repo 
import utils.args_helper as args_helper

import annotations.dataset_annotation as dataset_annotation
from db.annotation_repo import Annotation
import db.annotation_repo as ann_repo

import utils.time_handler as time_handler


def __query_videos(argv):

    season = args_helper.get_value_after_key(argv, "-season", "-season")
    show = args_helper.get_value_after_key(argv, "-show", "-show")
    videos = []
    if show != "":
        if season != "":
            videos = video_repo.find_by_show_and_season(show, int(season))
        else:
            videos = video_repo.find_by_show(show)
    else:
        videos = video_repo.find_all()
    for v in videos: 
        if v['downloaded']:
            print("%s s%02de%02d %s %s" % (v['show'], v['season'], v['episode'], v['downloaded'], v['fullpath']))
        else:
            print("%s s%02de%02d %s " % (v['show'], v['season'], v['episode'], v['downloaded']))

def __export_dataset(path):

    tags = ["intro", "pre-intro", "previous"]
    output = { "intro": [], "pre-intro": [], "previous": []}
    for show in ann_repo.get_shows():
        for season in ann_repo.get_show_seasons(show):
            for tag in tags: 
                for element in ann_repo.find_by_tag_show_season(tag, show, season):
                    output[tag].append({
                        "start": element['start'],
                        "end": element['end'],
                        "url": element['url']
                    })
    with open(path, 'w') as outfile:
        json.dump(output, outfile, indent=4, sort_keys=True)

def __import_dataset(path):
    
    tags = ["intro", "pre-intro", "previous"]
    with open(path) as json_file:
        data = json.load(json_file)
        for tag in tags: 
            print("\n%s\n" % tag)
            for element in data[tag]:
                ann_repo.insert(Annotation(element['url'], tag, element['start'], element['end']))

def __query_dataset(argv):
    
    exportPath = args_helper.get_value_after_key(argv, "-export", "-export")
    if exportPath != "" and ".json" in exportPath:
        __export_dataset(exportPath)
        return 

    importPath = args_helper.get_value_after_key(argv, "-import", "-import")
    if importPath != "" and ".json" in importPath:
        __import_dataset(importPath)
        return 

     
        
    # supports old method by first inserting all intros that have yet been inserted into ann_repo
    intros = dataset_annotation.get_dataset("intro")
    for intro in intros:
        ann_repo.insert(Annotation(intro['url'], "intro", intro['start'], intro['end']))
        

    shows = ann_repo.get_shows()
    i = 0
    print("\n\nFirst batch")
    while i < len(shows)*70/100:
        print(shows[i])
        i = i + 1
    print("\n\nSecond batch")
    while i < len(shows):
        print(shows[i])
        i = i + 1

    #for show in ann_repo.get_shows():
    # print(show)
    #  for season in ann_repo.get_show_seasons(show):
    ##     print(season)
    #     for intro in ann_repo.find_by_tag_show_season("intro", show, season):
    #         print(intro)

        

def execute_command(argv):   
    if args_helper.is_key_present(argv, "-videos"):
        __query_videos(argv)
    if args_helper.is_key_present(argv, "-dataset"):
        __query_dataset(argv)
    else: 
        print("Error: invalid query.")    





