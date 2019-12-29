import json 
import statistics 

import utils.args_helper as args_helper
import segmenter.scenedetector as scenedetector
import db.annotation_repo as ann_repo 
import db.video_repo as video_repo
import utils.time_handler as time_handler

SCENDTECT_COMP_STATS_FILE = "data/stats_scendetect.json"

#TODO: make it optional to segment all or only segment unsegmented videos
def __segment_all_scendetect(forced):
    scenedetector.segment_all_videos()


def __segment_scendetect(video_file):
    scenedetector.segment_video(video_file)


# Compares the scenes with the annotated intro to determine the margin of error between when scene breaks and intro sequence 
def __get_compare_scenes_to_intro(url, scenes, startStr, endStr):
    introStart = time_handler.timestamp(startStr)
    introEnd = time_handler.timestamp(endStr)
    firstScene = None 
    lastScene = None 
    found = False 
    print(url)
    print(startStr)
    print(endStr)
    for scene in scenes: 
        print(scene)
        sceneStart = time_handler.timestamp(scene['start'])
        sceneEnd = time_handler.timestamp(scene['end'])
        if sceneStart <= introStart and introStart <= sceneEnd:
            firstScene = scene 
            s1_start = sceneStart 
            s1_end = sceneEnd
            s1_start_diff = abs(s1_start - introStart) 
            s1_end_diff = abs(s1_end - introStart) 
        if sceneStart <= introEnd and introEnd <= sceneEnd:
            lastScene = scene 
            s2_start = sceneStart
            s2_end = sceneEnd
            s2_start_diff = abs(s2_start - introEnd) 
            s2_end_diff = abs(s2_end - introEnd) 
            found = True 
            break  

    if not found:
        return None

    if (s1_start_diff <= s1_end_diff):
        suggestedStartStr = firstScene['start']
        startError = -s1_start_diff/1000
    else:
        suggestedStartStr = firstScene['end']
        startError = s1_end_diff/1000
    if (s2_start_diff <= s2_end_diff):
        suggestedEndStr = lastScene['start']
        endError = -s2_start_diff/1000
    else:
        suggestedEndStr = lastScene['end']
        endError = s2_end_diff/1000
    return {
        'url': url,
        'introStart': startStr,
        'suggestedStart': suggestedStartStr,
        'startError': startError,
        'introEnd': endStr,
        'suggestedEnd': suggestedEndStr,
        'endError': endError,
    }

def __create_scendetect_intro_stats():
    intros = ann_repo.find_by_tag("intro")
    urls = []
    for intro in intros:
        urls.append(intro['url'])
    videos = video_repo.find_by_urls(urls)
    hasScenesCount = 0
    data = []
    for video in videos:
        if "scenes" in video:
            hasScenesCount = hasScenesCount + 1
            for intro in intros: 
                if intro['url'] == video['url']:
                    result = __get_compare_scenes_to_intro(intro['url'], video['scenes'], intro['start'], intro['end'])
                    if result: 
                        data.append(result)

    with open(SCENDTECT_COMP_STATS_FILE, 'w') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=False)

    print("Processed from annotated set: %d/%d\nSegment the remainder to improve the coverage." % (hasScenesCount, len(videos)))


def __display_scendetect_stats(startFilter, endFilter):
    includeEntry = True 
    if startFilter != "":
        startFilterValue = float(startFilter.split(" ")[1])
        startFilter = startFilter.split(" ")[0]
    if endFilter != "":
        endFilterValue = float(endFilter.split(" ")[1])
        endFilter = endFilter.split(" ")[0]
    startErrors = []
    endErrors = []
    matchingEntries = 0
    s = "Start\t\tSceneStart\tStartError\tEnd\t\t SceneEnd\tEndError\turl\n"
    with open(SCENDTECT_COMP_STATS_FILE) as json_file:
        entries = json.load(json_file)
        for entry in entries:          
            startError = abs(entry['startError'])
            endError = abs(entry['endError'])
            if startFilter != "":
                includeEntry = False 
                if startFilter == "lt" and startError < startFilterValue:
                    includeEntry = True 
                if startFilter == "gt" and startError > startFilterValue:
                    includeEntry = True 
            if endFilter != "":
                includeEntry = False 
                if endFilter == "lt" and endError < endFilterValue:
                    includeEntry = True 
                if endFilter == "gt" and endError > endFilterValue:
                    includeEntry = True 


            if includeEntry:
                s = s + entry['introStart'] + "\t" + entry['suggestedStart'] + "\t" + ("%f" % entry['startError']) + "\t" + entry['introEnd'] + "\t" + entry['suggestedEnd'] + "\t" + ("%f" % entry['endError']) + "\t" + entry['url'] + "\n"   
                startErrors.append(startError)
                endErrors.append(endError)
                matchingEntries = matchingEntries + 1

    print(s)
    print("Entries: %d/%d\n" % (matchingEntries, len(entries)))
    if startFilter != "":
        print("Start filter: %s %d" % (startFilter, startFilterValue)) 
    if endFilter != "":
        print("End filter %s %d" % (endFilter, endFilterValue))
    if len(startErrors) > 0:
        print("Start Error avg:     %f" % statistics.mean(startErrors))
        print("Start Error median:  %f" % statistics.median(startErrors))
        print("Start Error stdev:   %f" % statistics.stdev(startErrors))
    if len(endErrors) > 0:
        print("End Error avg:       %f" % statistics.mean(endErrors))
        print("End Error median:    %f" % statistics.median(endErrors))
        print("End Error stdev:     %f" % statistics.stdev(endErrors)) 


def execute(argv):
    if args_helper.is_key_present(argv, "-all"):
        if args_helper.is_key_present(argv, "-force"):
            __segment_all_scendetect(True)
        else: 
            __segment_all_scendetect(False)
        return
    file = args_helper.get_value_after_key(argv, "-input", "-i")
    if file != "" and ".mp4" in file: 
        __segment_scendetect(file)
        return 
    if args_helper.is_key_present(argv, "-stats"):
        __create_scendetect_intro_stats()
        
        startFilter = ""
        index = args_helper.get_key_index_first(argv, ["-sf", "-startfilter"])
        if index != -1 and index + 2 < len(argv):
            if (argv[index + 1] == "lt"):
                try:
                    f = float(argv[index + 2])
                    startFilter = "lt " + ("%f" % f)
                except:
                    print("Error: less than filter must contain a float or integer")
            elif (argv[index + 1] == "gt"):
                try:
                    f = float(argv[index + 2])
                    startFilter = "gt " + ("%f" % f)
                except:
                    print("Error: greater than filter must contain a float or integer")
        
        endFilter = ""
        index = args_helper.get_key_index_first(argv, ["-ef", "-endfilter"])
        if index != -1 and index + 2 < len(argv):
            if (argv[index + 1] == "lt"):
                try:
                    f = float(argv[index + 2])
                    endFilter = "lt " + ("%f" % f)
                except:
                    print("Error: less than filter must contain a float or integer")
            elif (argv[index + 1] == "gt"):
                try:
                    f = float(argv[index + 2])
                    endFilter = "gt " + ("%f" % f)
                except:
                    print("Error: greater than filter must contain a float or integer")
        __display_scendetect_stats(startFilter, endFilter)
        return 


