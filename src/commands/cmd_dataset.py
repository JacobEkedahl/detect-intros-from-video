"""
    Commands:

    * --dataset -stats     
        Loops through all annotated data creating some basic statistics

    * --dataset -export data/dataset.json   
        Exports annotated db content to json file

    * --dataset -import data/dataset.json               
        Imports json file to db, warning will override similar urls

    * --dataset -annotate -tag $tag -s $start -e $end -url $url
        Saves a manual annotation in the database
"""

import json 
import statistics 

import db.video_repo as video_repo 
import utils.args_helper as args_helper
import annotations.dataset_annotation as dataset_annotation
import utils.time_handler as time_handler
import annotations.dataset_annotation as dataset_annotation
import db.dataset_manager as dataset_manager

def __export_dataset(path):
    dataset_manager.export_dataset(path)

def __import_dataset(path):
    dataset_manager.import_dataset(path)

def __do_present_length_varians():
    annotatedVideos = video_repo.find_all_with_intro_annotation()
    show = ""
    season = -1
    prevShow = ""
    prevSeason = -1
    lengthList = []
    for v in annotatedVideos:
        show = v['show']
        season = v['s']
        if show != prevShow:
            print()
        
        if season != prevSeason: 
            print("\n%s %02d\n" % (show, season))
            lengthList = []

        intro = v[video_repo.INTRO_ANNOTATION_KEY]
        length = time_handler.timestamp(intro['end'])/1000 - time_handler.timestamp(intro['start'])/1000
        lengthList.append(length)
        print("%s\t%f" % (v['url'], length))

        prevShow = v['show']
        prevSeason = v['s']


def __do_manual_annotation(argv):
    start = ""
    end = ""
    tag = "intro"
    path = "data/dataset.json"
    url = ""
    for i in range(1, len(argv)):
        if (argv[i] == "-s" or argv[i] == "-start") and i + 1 < len(argv):
            start = argv[i + 1]
        elif (argv[i] == "-e" or argv[i] == "-end") and i + 1 < len(argv):
            end = argv[i + 1]
        elif (argv[i] == "-t" or argv[i] == "-tag") and i + 1 < len(argv):
            tag = argv[i + 1]
        elif (argv[i] == "-url") and i + 1 < len(argv):
            url = argv[i + 1]
  
    
    if (url != "" and tag != "" and start != "" and end != "" and path != ""):
        count = dataset_annotation.manual_annotation(path, url, tag, start, end)
        print("Total %s count: %d " % (tag, count))
    else:
        print("Error: Not enough arguments provided") 


def execute(argv):   
    exportPath = args_helper.get_value_after_key(argv, "-export", "-export")
    if exportPath != "" and ".json" in exportPath:
        __export_dataset(exportPath)
        return 

    importPath = args_helper.get_value_after_key(argv, "-import", "-import")
    if importPath != "" and ".json" in importPath:
        __import_dataset(importPath)
        return 
        
    if args_helper.is_key_present(argv, "-annotate"):
        __do_manual_annotation(argv)
        return 

    if args_helper.is_key_present(argv, "-length"):
        __do_present_length_varians()
        return


