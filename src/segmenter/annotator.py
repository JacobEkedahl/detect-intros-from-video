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

# Contains the first and last scenes within for a given annotation interval 
class AnnotationInterval:
    def __init__(self, firstScene, lastScene):
        self.firstScene = firstScene
        self.lastScene = lastScene


def annotate_strict_scenes(annotation, data, annotationStart, annotationEnd, displayAllFlag):
    annotationInterval = AnnotationInterval(None, None)
    for scene in data['scenes']:
        sceneStart = time.H_M_S_to_seconds(scene['start'])
        sceneEnd = time.H_M_S_to_seconds(scene['end'])
        if annotation not in scene: 
            scene[annotation] = False 
        if (sceneStart >= annotationStart and sceneEnd <= annotationEnd) or (sceneStart < annotationStart and annotationEnd <= sceneEnd):
            scene[annotation] = True 
            if annotationInterval.firstScene is None: 
                annotationInterval.firstScene = scene 
                annotationInterval.lastScene = scene 
            else:
                 annotationInterval.lastScene = scene
            if not displayAllFlag:
                print(scene)
        if displayAllFlag: 
            print(scene)
    return annotationInterval

def annotate_loose_scenes(annotation, data, annotationStart, annotationEnd, displayAllFlag):
    annotationInterval = AnnotationInterval(None, None)
    for scene in data['scenes']:
        sceneStart = time.H_M_S_to_seconds(scene['start'])
        sceneEnd = time.H_M_S_to_seconds(scene['end'])
        if annotation not in scene: 
            scene[annotation] = False 
        if (
            sceneStart <= annotationStart and annotationStart < sceneEnd) or ( 
            sceneStart <= annotationEnd and annotationEnd < sceneEnd) or (      
            annotationStart < sceneStart and sceneEnd < annotationEnd         
        ):
            scene[annotation] = True 
            if annotationInterval.firstScene is None: 
                annotationInterval.firstScene = scene 
                annotationInterval.lastScene = scene 
            else:
                 annotationInterval.lastScene = scene
            if not displayAllFlag:
                print(scene)
        if displayAllFlag: 
            print(scene)
    return annotationInterval
    

def annotate_segments_loose(annotation, filePath, startTimeStr, endTimeStr, displayAllFlag):
    annotationStart = time.H_M_S_to_seconds(startTimeStr)
    annotationEnd = time.H_M_S_to_seconds(endTimeStr)
    if (annotationEnd < annotationStart):
        return
    annotationInterval = None
    with open(filePath) as json_file:
        data = json.load(json_file)
        annotationInterval = annotate_loose_scenes(annotation, data, annotationStart, annotationEnd, displayAllFlag)
        firstScene = annotationInterval.firstScene
        lastScene = annotationInterval.lastScene
        if firstScene is None: 
            print("Error: failed to find any intersecting scenes.")
            print("Input: %s to %s" % (startTimeStr, endTimeStr))
            data[annotation] = {
                'start': startTimeStr,
                'end': endTimeStr,
                'success': False
            }
        else: 
            s1_start = time.H_M_S_to_seconds(firstScene['start'])
            s1_end = time.H_M_S_to_seconds(firstScene['end'])
            s1_start_diff = abs(s1_start - annotationStart) 
            s1_end_diff = abs(s1_end - annotationStart) 
            if (s1_start_diff <= s1_end_diff):
                suggestedStartStr = firstScene['start']
                startError = -s1_start_diff
            else:
                suggestedStartStr = firstScene['end']
                startError = s1_end_diff

            s2_start = time.H_M_S_to_seconds(lastScene['start'])
            s2_end = time.H_M_S_to_seconds(lastScene['end'])
            s2_start_diff = abs(s2_start - annotationEnd) 
            s2_end_diff = abs(s2_end - annotationEnd) 
            if (s2_start_diff <= s2_end_diff):
                suggestedEndStr = lastScene['start']
                endError = -s2_start_diff
            else:
                suggestedEndStr = lastScene['end']
                endError = s2_end_diff
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



        with open(filePath, 'w') as outfile:
            json.dump(data, outfile)
 

 # This is legacy annotation boundary, can still be accessed with -strict argument
 # If the new implementation is proven to be better this will be phased out.
def annotate_segments_strict(annotation, filePath, startTimeStr, endTimeStr, displayAllFlag):
    annotationStart = time.H_M_S_to_seconds(startTimeStr)
    annotationEnd = time.H_M_S_to_seconds(endTimeStr)
    if (annotationEnd < annotationStart):
        return
    annotationInterval = None
    with open(filePath) as json_file:
        data = json.load(json_file)
        annotationInterval = annotate_strict_scenes(annotation, data, annotationStart, annotationEnd, displayAllFlag)
        firstScene = annotationInterval.firstScene
        lastScene = annotationInterval.lastScene
        if firstScene is None: 
            print("Error: failed to find any true intersecting scenes.")
            print("Input: %s to %s" % (startTimeStr, endTimeStr))
            data[annotation] = {
                'start': startTimeStr,
                'end': endTimeStr,
                'success': False
            }
        else: 
            data[annotation] = {
                'start': startTimeStr,
                'suggestedStart': firstScene['start'],
                'startError': time.H_M_S_to_seconds(firstScene['start']) - annotationStart,
                'end': endTimeStr,
                'suggestedEnd': lastScene['end'],
                'endError': time.H_M_S_to_seconds(lastScene['end']) - annotationEnd,
                'success': True
            }
            print("Input: %s to %s" % (startTimeStr, endTimeStr))
            print("Suggested: %s to %s" % (firstScene['start'], lastScene['end']))
            print("StartError: %f" % (time.H_M_S_to_seconds(firstScene['start']) - annotationStart))
            print("EndError: %f" % (time.H_M_S_to_seconds(lastScene['end']) - annotationEnd))
        with open(filePath, 'w') as outfile:
            json.dump(data, outfile)
   

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
        json.dump(data, outfile)


def print_all_scenes(filePath):
    with open(filePath) as json_file:
        data = json.load(json_file)
        for scene in data['scenes']:
            print(scene)


def execute(argv):
    if len(argv) - 1 <= 1:
        print("Error: No arguments provided.")
        return
    if not argv[2].endswith(".json"):
        print("Error: Need to specify json file.")
        return

    startTime = ""
    endTime = ""
    annotationTag = ""
    displayAllScenes = False 
    deleteAnnotation = False
    strictAnnotationBounds = False
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
        elif (argv[i] == "-strict"):
            strictAnnotationBounds = True
        elif (argv[i] == "-force"):
            overridePrevAnnotation = True

    filePath = argv[2]
    if not os.path.isfile(filePath):
        print("Error: invalid file path provided (%s)" % filePath)
        return

    if (startTime == "" and endTime == "" and displayAllScenes and annotationTag == ""): 
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

    if strictAnnotationBounds:
        annotate_segments_strict(annotationTag.lower(), filePath, startTime, endTime, displayAllScenes)
    else:
        annotate_segments_loose(annotationTag.lower(), filePath, startTime, endTime, displayAllScenes)