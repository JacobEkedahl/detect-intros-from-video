import sys
import json 
import time


def print_scene(scene):
    print('Scene %2d: Start %s / Frame %d, End %s / Frame %d' % (
        scene['scene'], scene['start'], scene['startFrame'], scene['end'], scene['endFrame']
    )) 


def extract_time_from_str(str):
    t0 = time.strptime(str.split('.')[0],'%H:%M:%S')
    try:
        t1 = str.split('.')[1]
        f1 = float(t1[0:3])
    except:
        f1 = 0.0
    return t0.tm_hour*3600 + t0.tm_min*60 + t0.tm_sec + f1/1000


def time_delta(t1, t2):
    return t1 - t2

def annotate_intro(filePath, startTimeStr, endTimeStr, displayAllFlag):
    introStart = extract_time_from_str(startTimeStr)
    introEnd = extract_time_from_str(endTimeStr)

    if (introEnd < introStart):
        return

    firstSceneStart = None
    lastSceneEnd = None 
    with open(filePath) as json_file:
        data = json.load(json_file)
        for scene in data['scenes']:
            sceneStart = extract_time_from_str(scene['start'])
            sceneEnd = extract_time_from_str(scene['end'])
            # scenes that intersect with the intro 
            if sceneStart >= introStart and sceneEnd <= introEnd:
                scene['intro'] = True 
                if firstSceneStart is None: 
                    firstSceneStart = sceneStart
                    lastSceneEnd = sceneEnd
                else: 
                    lastSceneEnd = sceneEnd 
                if not displayAllFlag:
                    print(scene)
            if displayAllFlag: 
                 print(scene)

        data['introAnnotation'] = {
            'introStart': startTimeStr,
            'startError': time_delta(firstSceneStart, introStart),
            'introEnd': endTimeStr,
            'EndError': time_delta(lastSceneEnd, introEnd)
        }
        with open(filePath, 'w') as outfile:
            json.dump(data, outfile)
        
        # display error margin 
        print("Start error: %f" % time_delta(firstSceneStart, introStart))
        print("End error: %f" % time_delta(lastSceneEnd, introEnd))


if len(sys.argv) -1 < 1 or  not sys.argv[1].endswith(".json"):
    print("Error: Need to specify json file.")
    exit()

startTime = ""
endTime = ""
displayAllScenes = False 

for i in range(1, len(sys.argv)):
    if (sys.argv[i] == "-s" or sys.argv[i] == "-start") and i + 1 < len(sys.argv):
        startTime = sys.argv[i + 1]
    elif (sys.argv[i] == "-e" or sys.argv[i] == "-end") and i + 1 < len(sys.argv):
        endTime = sys.argv[i + 1]
    elif (sys.argv[i] == "--all"):
        displayAllScenes = True 

if (startTime == ""):
    print("Error: start time must be provided")
    exit()

if (endTime == ""):
    print("Error: end time must be provided")
    exit()

filePath = sys.argv[1]
annotate_intro(filePath, startTime, endTime, displayAllScenes)
