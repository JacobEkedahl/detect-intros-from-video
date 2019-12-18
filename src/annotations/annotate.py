
import utils.srt_to_json
import utils.time_handler as time


class TimeInterval:
    def __init__(self, start, end):
        self.start = start
        self.end = end


# Recursively walks through all the scenes and timeIntervals, increasing scene[annotation] with one if present inside the scene
#
def inc_count_of_occurances_of_time_intervals(annotation, scenes, i, timeIntervals, j):
    if i >= len(scenes) or j >= len(timeIntervals):
        return
    sceneStart = time.timestamp(scenes[i]['start'])
    sceneEnd = time.timestamp(scenes[i]['end'])
    subStart = time.timestamp(timeIntervals[j].start)
    subEnd = time.timestamp(timeIntervals[j].end)

    # Cases: 

    # 1) The subtitle is within the scene but exceeds it -->  goto next scene
    if sceneStart <= subStart and subStart < sceneEnd and sceneEnd < subEnd:
        scenes[i][annotation] = scenes[i][annotation] + 1
        inc_count_of_occurances_of_time_intervals(annotation, scenes, i + 1, timeIntervals, j)
 
    # 2) The subtitle ends before the scene ends --> goto next subtitle
    elif subEnd < sceneEnd:
        scenes[i][annotation] = scenes[i][annotation] + 1
        inc_count_of_occurances_of_time_intervals(annotation, scenes, i, timeIntervals, j + 1)

    # 3) the subtitle starts before the scene and ends after it --> goto next scene 
    elif (subStart < sceneStart and sceneEnd < subEnd):
        scenes[i][annotation] = scenes[i][annotation] + 1
        inc_count_of_occurances_of_time_intervals(annotation, scenes, i + 1, timeIntervals, j)

    # 4) None of the subtitle is within the scene --> goto next scene 
    else: 
        inc_count_of_occurances_of_time_intervals(annotation, scenes, i + 1, timeIntervals, j)


# Wrapper for counting time interval intersections with a given scene
#   
def count_time_interval_intersections(annotation, scenes, timeIntervals):
    inc_count_of_occurances_of_time_intervals(annotation, scenes, 0, timeIntervals, 0)


# Recursively walks through all the scenes and timeIntervals, flagging scene[annotation] as True if the time interval is present inside the scene
#
def flag_intersection_of_time_intervals(annotation, scenes, i, timeIntervals, j):
    if i >= len(scenes) or j >= len(timeIntervals):
        return
    sceneStart = time.timestamp(scenes[i]['start'])
    sceneEnd = time.timestamp(scenes[i]['end'])
    subStart = time.timestamp(timeIntervals[j].start)
    subEnd = time.timestamp(timeIntervals[j].end)

    # Cases: 

    # 1) The subtitle is within the scene but exceeds it -->  goto next scene
    if sceneStart <= subStart and subStart < sceneEnd and sceneEnd < subEnd:
        scenes[i][annotation] = True
        flag_intersection_of_time_intervals(annotation, scenes, i + 1, timeIntervals, j)
 
    # 2) The subtitle ends before the scene ends --> goto next subtitle
    elif subEnd < sceneEnd:
        scenes[i][annotation] = True 
        flag_intersection_of_time_intervals(annotation, scenes, i, timeIntervals, j + 1)

    # 3) the subtitle starts before the scene and ends after it --> goto next scene 
    elif (subStart < sceneStart and sceneEnd < subEnd):
        scenes[i][annotation] = True 
        flag_intersection_of_time_intervals(annotation, scenes, i + 1, timeIntervals, j)

    # 4) None of the subtitle is within the scene --> goto next scene 
    else: 
        flag_intersection_of_time_intervals(annotation, scenes, i + 1, timeIntervals, j)


# Wrapper for setting presence of multiple time intervals within a set of scenes. 
#   
def set_presence_of_time_interval(annotation, scenes, timeIntervals):
    flag_intersection_of_time_intervals(annotation, scenes, 0, timeIntervals, 0)


# Wrapper for setting presence of a single time interval within a scene
#   
def set_presence_of_interval(annotation, scenes, startStr, endStr):
    timeIntervals = []
    timeIntervals.append(TimeInterval(startStr, endStr))
    flag_intersection_of_time_intervals(annotation, scenes, 0, timeIntervals, 0)