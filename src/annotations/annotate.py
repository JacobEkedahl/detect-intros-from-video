import utils.time_handler as time


class TimeInterval:
    def __init__(self, start, end):
        self.start = start
        self.end = end

# Recursively walks through all the scenes and timeIntervals, flagging scene[annotation] as True if the time interval is present inside the scene
# Precondition: TimeInterval start and end must be in seconds (float/int)
def __flag_intersection_of_time_intervals(annotation, scenes, i, timeIntervals, j):
    iMax = len(scenes)
    jMax = len(timeIntervals)
    while i < iMax and j < jMax:
        sceneStart = time.timestamp(scenes[i]['start'])
        sceneEnd = time.timestamp(scenes[i]['end'])
        timeStart =timeIntervals[j].start
        timeEnd = timeIntervals[j].end

        # scene_start >= interval_start and scene_end <= interval_end:

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
        sceneStart = time.str_to_seconds(segments[i]['start'])
        sceneEnd = time.str_to_seconds(segments[i]['end'])
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

def set_presence_of_interval(annotation, scenes, startInSeconds, endInSeconds, override):
    if annotation is None or annotation == "":
        raise ValueError("annotation")
    if endInSeconds < startInSeconds:
        raise ValueError("end < start")
    for scene in scenes: 
        scene_start = time.str_to_seconds(scene['start'])   
        scene_end = time.str_to_seconds(scene['end'])
        if scene_start >= startInSeconds and scene_end <= endInSeconds:
            scene[annotation] = True 
        elif override:
            scene[annotation] = False
    
