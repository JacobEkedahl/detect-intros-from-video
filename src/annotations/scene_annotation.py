# 
# Allows for scene annotation based on scenes within a given interval.                                                       
#   
                                                                       
# Example usage 1:                                                                 
#   py annotator.py --ann al-pitcher-pa-paus.json -s 00:00:00 -e 00:00:15 -t intro                                                                  
#         
#   Set 'intro' = true for scenes between start and end     
                                                         
# Example usage 3:                                                              
#   py annotator.py --ann al-pitcher-pa-paus.json -s 00:00:00 -e 00:00:15 -t intro -print                                                            
#   
#   Same as before but will also print out all scenes

# Example usage 3:                                                                 
#   py annotator.py --ann al-pitcher-pa-paus.json -s 00:00:00 -e 00:00:15 -t intro -force
#   
#   Same as before but will now override any previous annotations 
                                                                         
# Example usage 4:                                                                  
#   py annotator.py --ann al-pitcher-pa-paus.json -print      
# 
#   Debug command for simply printing all scenes
                                                                                                                                       
# Example usage 5:                                                                
#   py annotator.py --ann al-pitcher-pa-paus.json -delete -tag intro                    
#    
#   Deletes the tag from all scenes and any associated metadata
                                                                       
import os
import json 

import utils.time_handler as time
from .annotate import set_presence_of_interval
from .annotate import TimeInterval


# Annotates all scenes that intersect with the start and end time

def annotate_segments_loose(annotation, filePath, startTimeStr, endTimeStr, displayScenes):
    annotationStart = time.timestamp(startTimeStr)
    annotationEnd = time.timestamp(endTimeStr)
    if (annotationEnd < annotationStart):
        return
    with open(filePath) as json_file:
        data = json.load(json_file)

        for scene in data['scenes']:
            scene[annotation] = False 

        # Annotate
        set_presence_of_interval(annotation, data['scenes'], startTimeStr, endTimeStr)

        # Metadata
        firstScene = None
        lastScene = None
        for scene in data['scenes']:
            if (displayScenes):
                print(scene)
            if (scene[annotation] == True):
                if firstScene is None: 
                    firstScene = scene
                    lastScene = scene 
                else:
                    lastScene = scene

        if firstScene is None: 
            print("Error: failed to find any intersecting scenes.")
            print("Input: %s to %s" % (startTimeStr, endTimeStr))
            data[annotation] = {
                'start': startTimeStr,
                'end': endTimeStr,
                'success': False
            }
        else: 
            s1_start = time.timestamp(firstScene['start'])
            s1_end = time.timestamp(firstScene['end'])
            s1_start_diff = abs(s1_start - annotationStart) 
            s1_end_diff = abs(s1_end - annotationStart) 
            if (s1_start_diff <= s1_end_diff):
                suggestedStartStr = firstScene['start']
                startError = -s1_start_diff/1000
            else:
                suggestedStartStr = firstScene['end']
                startError = s1_end_diff/1000

            s2_start = time.timestamp(lastScene['start'])
            s2_end = time.timestamp(lastScene['end'])
            s2_start_diff = abs(s2_start - annotationEnd) 
            s2_end_diff = abs(s2_end - annotationEnd) 
            if (s2_start_diff <= s2_end_diff):
                suggestedEndStr = lastScene['start']
                endError = -s2_start_diff/1000
            else:
                suggestedEndStr = lastScene['end']
                endError = s2_end_diff/1000
            data[annotation] = {
                'start': startTimeStr,
                'suggestedStart': suggestedStartStr,
                'startError': startError,
                'end': endTimeStr,
                'suggestedEnd': suggestedEndStr,
                'endError': endError,
                'success': True
            }
            print("Input: %s to %s" % (startTimeStr, endTimeStr))
            print("Suggested: %s to %s" % (suggestedStartStr, suggestedEndStr))
            print("StartError: %f" % (startError))
            print("EndError: %f" % (endError))

        # Save
        with open(filePath, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=False)


def annotate_previous_segments(filePath, startTimeStr, endTimeStr, displayAllFlag):
    return annotate_segments_loose("previous", filePath, startTimeStr, endTimeStr, True)


def annotate_title_segments(filePath, startTimeStr, endTimeStr, displayAllFlag):
    return annotate_segments_loose("title", filePath, startTimeStr, endTimeStr, True)


def annotate_intro_segments(filePath, startTimeStr, endTimeStr, displayAllFlag):
    return annotate_segments_loose("intro", filePath, startTimeStr, endTimeStr, True)


def delete_annotation(annotation, filePath):
    with open(filePath) as json_file:
        data = json.load(json_file)
        for scene in data['scenes']:
            if annotation in scene: 
                scene.pop(annotation)
        if annotation in data: 
            data.pop(annotation)
    with open(filePath, 'w') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=False)


def print_all_scenes(filePath):
    with open(filePath) as json_file:
        data = json.load(json_file)
        for scene in data['scenes']:
            print(scene)


def save_url(filePath, url):
    with open(filePath) as json_file:
        data = json.load(json_file)
        if 'url' in data:
            print("Warning: Overwriting previously saved url: %s with %s" % (url, data['url']))
        data['url'] = url
        with open(filePath, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=False)

def execute(argv):
    if len(argv) - 1 <= 1:
        print("Error: No arguments provided.")
        return
    if not argv[2].endswith(".json"):
        print("Error: Need to specify json file.")
        return

    url = ""
    startTime = ""
    endTime = ""
    annotationTag = ""
    displayAllScenes = False 
    deleteAnnotation = False
    overridePrevAnnotation = False

    for i in range(1, len(argv)):
        if (argv[i] == "-s" or argv[i] == "-start") and i + 1 < len(argv):
            startTime = argv[i + 1]
        elif (argv[i] == "-e" or argv[i] == "-end") and i + 1 < len(argv):
            endTime = argv[i + 1]
        elif (argv[i] == "-print"):
            displayAllScenes = True 
        elif (argv[i] == "-tag" or argv[i] == "-t") and i + 1 < len(argv):
            annotationTag = argv[i + 1]
        elif (argv[i] == "-delete"):
            deleteAnnotation = True
        elif (argv[i] == "-force"):
            overridePrevAnnotation = True
        elif (argv[i] == "-url") and i + 1 < len(argv):
            url = argv[i + 1] 



    filePath = argv[2]
    if not os.path.isfile(filePath):
        print("Error: invalid file path provided (%s)" % filePath)
        return
    
    if (url != ""):
        save_url(filePath, url)
        if startTime == "" and endTime == "" and annotationTag == "" and not displayAllScenes:
            return

    if (displayAllScenes and startTime == "" and endTime == "" and annotationTag == ""): 
        print_all_scenes(filePath)
        return 

    if (annotationTag == ""):
        print("Error: tag must be provided (-t or -tag)")
        return

    if deleteAnnotation: 
        delete_annotation(annotationTag, filePath)
        return

    if (startTime == ""):
        print("Error: start time must be provided (-s or -start)")
        return
    if (endTime == ""):
        print("Error: end time must be provided (-e or -end)")
        return

    if overridePrevAnnotation:
         delete_annotation(annotationTag, filePath)

    annotate_segments_loose(annotationTag.lower(), filePath, startTime, endTime, displayAllScenes)    
    