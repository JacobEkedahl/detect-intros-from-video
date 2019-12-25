import re
import time


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

def timestamp_to_str(timestamp):
    milliseconds = timestamp%1000
    milliseconds = int(milliseconds)
    seconds = (timestamp/1000)%60
    seconds = int(seconds)
    minutes= (timestamp/(1000*60))%60
    minutes = int(minutes)
    hours= (timestamp/(1000*60*60))%24
    if milliseconds > 0:
        return "%02d:%02d:%02d.%03d" % (hours, minutes, seconds, milliseconds)
    return "%02d:%02d:%02d" % (hours, minutes, seconds)
