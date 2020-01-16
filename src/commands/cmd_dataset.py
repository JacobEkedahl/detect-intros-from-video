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

SHOW = "show"
SEASON = "s"


def __export_dataset(path):
    dataset_manager.export_dataset(path)

def __import_dataset(path):
    dataset_manager.import_dataset(path)

def __do_present_start_varians():
    videos = video_repo.find_all_with_intro_annotation()
    dictVideos = {}
    for video in videos: 
        show = video[SHOW]
        season = video[SEASON]
        if not show in dictVideos:
            dictVideos[show] = {}
        if not season in dictVideos[show]:
            dictVideos[show][season] = []
        dictVideos[show][season].append(video)

    # Iterate through all ordered videos 
    startList = []
    showCount = 0
    for show in dictVideos:
        showCount = showCount + 1
        print("\n%s" % show)
        for season in dictVideos[show]:
            startListSeason = []
            print("\n%02d\n" % season)
            for video in dictVideos[show][season]:
                intro = video[video_repo.INTRO_ANNOTATION_KEY]
                if intro['start'] == intro['end']:
                    print("%s\t%s" % (video['url'], "none"))
                    continue 
                start = intro['start']
                startList.append(start)
                startListSeason.append(start)
                print("%s\t%f" % (video['url'], start))

            if len(startListSeason) > 1:    
                print("Start avg:     %f" % statistics.mean(startListSeason))
                print("Start median:   %f" % statistics.median(startListSeason))
                print("Start stdev:   %f" % statistics.stdev(startListSeason))
    print("Show count: %d" % showCount)
    print("Video count: %d" % len(videos))


def __do_present_length_varians():
    videos = video_repo.find_all_with_intro_annotation()
    dictVideos = {}
    for video in videos: 
        show = video[SHOW]
        season = video[SEASON]
        if not show in dictVideos:
            dictVideos[show] = {}
        if not season in dictVideos[show]:
            dictVideos[show][season] = []
        dictVideos[show][season].append(video)

    # Iterate through all ordered videos 
    lengthList = []
    for show in dictVideos:
        print("\n%s" % show)
        for season in dictVideos[show]:
            print("%02d\n" % season)
            lengthSeason = []
            for video in dictVideos[show][season]:
                intro = video[video_repo.INTRO_ANNOTATION_KEY]
                if intro['start'] == intro['end']:
                    continue 
                length = intro['end'] - intro['start']
                lengthList.append(length)
                lengthSeason.append(length)
                print("%s\t%f" % (video['url'], length))
            if len(lengthSeason) > 1:    
                print("Length avg:     %f" % statistics.mean(lengthSeason))
                print("Length median:  %f" % statistics.median(lengthSeason))
                print("Length stdev:   %f" % statistics.stdev(lengthSeason))


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

    if args_helper.is_key_present(argv, "-start"):
        __do_present_start_varians()
        return