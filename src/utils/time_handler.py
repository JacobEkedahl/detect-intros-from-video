import time
import re 

# @TODO: Depreciated
def to_seconds(time_string):
    return str_to_seconds(time_string)

def str_to_seconds(time_string):
    #print("ts: %d" % timestamp(time_string))
    return float(timestamp(time_string))/1000

def seconds_to_str(seconds):
    return timestamp_to_str(seconds*1000)

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


def timestamp(time_string):
    if ',' in time_string:
        hours = int(re.findall(r'(\d+):\d+:\d+,\d+', time_string)[0])
        minutes = int(re.findall(r'\d+:(\d+):\d+,\d+', time_string)[0])
        seconds = int(re.findall(r'\d+:\d+:(\d+),\d+', time_string)[0])
        ms = re.findall(r'\d+:\d+:\d+,(\d+)', time_string)[0]
        ms = '{:<03}'.format(ms)
        milliseconds = int(ms)
       # milliseconds = int('{:<03}'.format(milliseconds))
    elif '.' in time_string: 
        hours = int(re.findall(r'(\d+):\d+:\d+.\d+', time_string)[0])
        minutes = int(re.findall(r'\d+:(\d+):\d+.\d+', time_string)[0])
        seconds = int(re.findall(r'\d+:\d+:(\d+).\d+', time_string)[0])
        ms = re.findall(r'\d+:\d+:\d+.(\d+)', time_string)[0]
        ms = '{:<03}'.format(ms)
        milliseconds = int(ms)
    else:
        hours = int(re.findall(r'(\d+):\d+:\d+', time_string)[0])
        minutes = int(re.findall(r'\d+:(\d+):\d+', time_string)[0])
        seconds = int(re.findall(r'\d+:\d+:(\d+)', time_string)[0])
        milliseconds = 0
        
    return (hours*3600 + minutes*60 + seconds) * 1000 + milliseconds
