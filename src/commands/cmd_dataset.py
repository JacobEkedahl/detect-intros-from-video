import json 
import statistics 

import db.video_repo as video_repo 
import utils.args_helper as args_helper
import annotations.dataset_annotation as dataset_annotation
from db.annotation_repo import Annotation
import db.annotation_repo as ann_repo
import utils.time_handler as time_handler
import annotations.dataset_annotation as dataset_annotation


def __export_dataset(path):
    print("exported to %s " % path)
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
    print("imported from %s " % path)
    tags = ["intro", "pre-intro", "previous"]
    with open(path) as json_file:
        data = json.load(json_file)
        for tag in tags: 
            print("\n%s\n" % tag)
            for element in data[tag]:
                ann_repo.insert(Annotation(element['url'], tag, element['start'], element['end']))
                print(element)


# TODO: not sure what statistics are relevant here tbh, you may wish to expand on this
def __create_intro_stats(): 
    shows = ann_repo.get_shows()
    for show in shows: 
        seasons = ann_repo.get_show_seasons(show)
        for season in seasons: 
            startList = []
            endList = []
            lengthList = []
            intros = ann_repo.find_by_tag_show_season("intro", show, season)
            for intro in intros:
                start = time_handler.timestamp(intro['start'])/1000
                end = time_handler.timestamp(intro['end'])/1000
                startList.append(start)
                endList.append(end)
                lengthList.append(end - start)

            if len(intros):
                print("\n%s %02d" % (show, season))
                startAvg = statistics.mean(startList)
                startMedian = statistics.median(startList) 
                startStdev = statistics.stdev(startList)
                lenAvg = statistics.mean(lengthList)
                lenMedian = statistics.median(lengthList) 
                lenStdev = statistics.stdev(lengthList)
                print("avg\tmedian\tstdev")
                print("start: %f %f %f " % (startAvg, startMedian, startStdev))
                print("length: %f %f %f %s" % (lenAvg, lenMedian, lenStdev, lengthList))
           

def __do_manual_annotation(argv):
    start = ""
    end = ""
    tag = "intro"
    path = "data/dataset.json"
    url = ""
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
        count = dataset_annotation.manual_annotation(path, url, tag, start, end)
        if doCount:
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

    if args_helper.is_key_present(argv, "-stats"):
        __create_intro_stats()
        return 
        
    if args_helper.is_key_present(argv, "-annotate"):
        __do_manual_annotation(argv)
        return 
    show = args_helper.get_value_after_key(argv, "-show", "-show")
    annotations = []
    if show != "":
        annotations = ann_repo.find_by_tag_show("intro", show)
    else:
        annotations = ann_repo.find_by_tag("intro")
    for a in annotations: 
        print("%s s%02de%02d" % (a['show'], a['season'], a['episode']))


