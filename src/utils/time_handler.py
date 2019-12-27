import time
import re 

def timestamp(time_string):
    if ',' in time_string:
        hours = int(re.findall(r'(\d+):\d+:\d+,\d+', time_string)[0])
        minutes = int(re.findall(r'\d+:(\d+):\d+,\d+', time_string)[0])
        seconds = int(re.findall(r'\d+:\d+:(\d+),\d+', time_string)[0])
        milliseconds = int(re.findall(r'\d+:\d+:\d+,(\d+)', time_string)[0])
    elif '.' in time_string: 
        hours = int(re.findall(r'(\d+):\d+:\d+.\d+', time_string)[0])
        minutes = int(re.findall(r'\d+:(\d+):\d+.\d+', time_string)[0])
        seconds = int(re.findall(r'\d+:\d+:(\d+).\d+', time_string)[0])
        milliseconds = int(re.findall(r'\d+:\d+:\d+.(\d+)', time_string)[0])
    else:
        hours = int(re.findall(r'(\d+):\d+:\d+', time_string)[0])
        minutes = int(re.findall(r'\d+:(\d+):\d+', time_string)[0])
        seconds = int(re.findall(r'\d+:\d+:(\d+)', time_string)[0])
        milliseconds = 0
    return (hours*3600 + minutes*60 + seconds) * 1000 + milliseconds


def validate_timeformat(t):
    try: 
        if not (t[0].isdigit() and t[1].isdigit() and t[2] == ':' and t[3].isdigit() and t[4].isdigit() and t[5] == ':' and t[6].isdigit() and t[7].isdigit()):
            return False 
        if len(t) == 8:
            return True
        if ',' in t:
            t = t.split(',')[1]
            for c in t: 
                if not c.isdigit():
                    return False
        elif '.' in t: 
            t = t.split('.')[1]
            for c in t: 
                if not c.isdigit():
                    return False
        return True 
    except: 
        return False


def timestamp_to_str(timestamp):
    milliseconds = timestamp%1000
    milliseconds = int(milliseconds)
    seconds = (timestamp/1000)%60
    seconds = int(seconds)
    minutes = (timestamp/(1000*60))%60
    minutes = int(minutes)
    hours= (timestamp/(1000*60*60))%24
    if milliseconds > 0:
        return "%02d:%02d:%02d.%03d" % (hours, minutes, seconds, milliseconds)
    return "%02d:%02d:%02d" % (hours, minutes, seconds)

