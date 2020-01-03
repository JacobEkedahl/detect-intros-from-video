import utils.time_handler as time


class TimeInterval:
    def __init__(self, start, end):
        self.start = start
        self.end = end




# Recursively walks through all the scenes and timeIntervals, increasing scene[annotation] with one if present inside the scene
#
def __inc_count_of_occurances_of_time_intervals(annotation, scenes, i, timeIntervals, j):
    iMax = len(scenes)
    jMax = len(timeIntervals)
    while i < iMax and j < jMax:
        sceneStart = time.timestamp(scenes[i]['start'])
        sceneEnd = time.timestamp(scenes[i]['end'])
        timeStart = time.timestamp(timeIntervals[j].start)
        timeEnd = time.timestamp(timeIntervals[j].end)

        # 1) The time-interval is within the scene but exceeds it -->
        if sceneStart <= timeStart and timeStart < sceneEnd and sceneEnd < timeEnd:
            scenes[i][annotation] = scenes[i][annotation] + 1
            i = i + 1 # goto next scene

        # 2) The time-interval ends before the scene ends --> 
        elif timeEnd <= sceneEnd:
            scenes[i][annotation] = scenes[i][annotation] + 1
            j = j + 1 # goto next time interval 

        # 3) the time-interval starts before the scene and ends after it -->
        elif (timeStart < sceneStart and sceneEnd < timeEnd):
            scenes[i][annotation] = scenes[i][annotation] + 1
            i = i + 1 # goto next scene 

        # 4) None of the time-interval is within the scene --> 
        else: 
            i = i + 1 # goto next scene 
    return scenes


# Wrapper for counting time interval intersections with a given scene
#   
def count_time_interval_intersections(annotation, scenes, timeIntervals):
    for scene in scenes: 
        scene[annotation] = 0
    __inc_count_of_occurances_of_time_intervals(annotation, scenes, 0, timeIntervals, 0)


# Recursively walks through all the scenes and timeIntervals, flagging scene[annotation] as True if the time interval is present inside the scene
#
def __flag_intersection_of_time_intervals(annotation, scenes, i, timeIntervals, j):
    iMax = len(scenes)
    jMax = len(timeIntervals)
    while i < iMax and j < jMax:
        sceneStart = time.timestamp(scenes[i]['start'])
        sceneEnd = time.timestamp(scenes[i]['end'])
        timeStart = time.timestamp(timeIntervals[j].start)
        timeEnd = time.timestamp(timeIntervals[j].end)

        # 1) The time-interval is within the scene but exceeds it -->
        if sceneStart <= timeStart and timeStart < sceneEnd and sceneEnd < timeEnd:
            scenes[i][annotation] = True
            i = i + 1 # goto next scene

        # 2) The time-interval ends before the scene ends --> 
        elif timeEnd <= sceneEnd:
            scenes[i][annotation] = True 
            j = j + 1 # goto next time interval 

        # 3) the time-interval starts before the scene and ends after it -->
        elif (timeStart < sceneStart and sceneEnd < timeEnd):
            scenes[i][annotation] = True 
            i = i + 1 # goto next scene 

        # 4) None of the time-interval is within the scene --> 
        else: 
            i = i + 1 # goto next scene 
    return scenes 


# Flags true if a timestamp (in seconds) falls within a scene
def set_presence_of_timestamps(annotation, segments, listOfSeconds, override):
    if override:
        for segment in segments: 
            segment[annotation] = False 
    i = 0
    j = 0
    iMax = len(segments)
    jMax = len(listOfSeconds)
    while i < iMax and j < jMax:
        sceneStart = time.to_seconds(segments[i]['start'])
        sceneEnd = time.to_seconds(segments[i]['end'])
        if sceneStart <= listOfSeconds[j] and listOfSeconds[j] < sceneEnd:
            segments[i][annotation] = True
            j = j + 1
        else: 
            i = i + 1
    return segments 


# Wrapper for setting presence of multiple time intervals within a set of scenes. 
#   
def set_presence_of_time_interval(annotation, scenes, timeIntervals, override):
    if override: 
        for scene in scenes:
            scene[annotation] = False
    __flag_intersection_of_time_intervals(annotation, scenes, 0, timeIntervals, 0)

def set_presence_of_time_interval_improved(annotation, scenes, TimeIntervals):
    for interval in TimeIntervals:
        interval_start = time.timestamp(interval.start)
        interval_end = time.timestamp(interval.end)
        for scene in scenes:
            scene_start = time.timestamp(scene['start'])
            scene_end = time.timestamp(scene['end'])
            if scene_start >= interval_start and scene_end <= interval_end:
                scene[annotation] = True 
            else:
                scene[annotation] = False
    return scenes


# Wrapper for setting presence of a single time interval within a scene
# Such as an intro, outro, previous, etc
#   
def set_presence_of_interval(annotation, scenes, startStr, endStr):
    timeIntervals = []
    timeIntervals.append(TimeInterval(startStr, endStr))
    set_presence_of_time_interval(annotation, scenes, timeIntervals, True)
