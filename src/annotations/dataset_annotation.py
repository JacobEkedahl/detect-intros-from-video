
import sys
import json 
import os 
import re

import db.video_repo as video_repo

def get_dataset(annotation):
    with open(path) as json_file:
        data = json.load(json_file)
        return data[annotation]
    return None

def __validate_time_input(t):
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


def query_yes_or_no(): 
    yes = {'yes','y', 'ye', ''}
    no = {'no','n'}

    choice = input().lower()
    if choice in yes:
        return True
    elif choice in no:
        return False
    else:
        sys.stdout.write("Please respond with 'yes' or 'no'")
        return query_yes_or_no()



def manual_annotation(path, url, tag, start, end):

    if not __validate_time_input(start) or not __validate_time_input(end):
        print("Error: Invalid time format.")
        return

    if not os.path.exists(path):
        with open(path, 'w') as outfile:
            data = { }
            json.dump(data, outfile)
    
    if "?start=auto" in url: 
        url = url.split("?start=auto")[0]

    with open(path) as json_file:
        data = json.load(json_file)
        found = None
        if not tag in data: 
            data[tag] = []
        else:
            for value in data[tag]:
                if (value['url'] == url):
                    print("Warning: %s was saved previously with %s - %s." % (value['url'], value['start'], value['end']))
                    print("Do you want to override it? y/n")
                    response = query_yes_or_no()
                    if not response: 
                        return
                    found = value
                    found['url'] = url 
                    found['start'] = start 
                    found['end'] = end
                    break
        if found is None: 
            data[tag].append( {
                'url': url,
                'start': start,
                'end': end
            })

        video_repo.insert_dataset_sequence(url, tag, start, end)
        with open(path, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True)
        print("%s saved for %s as (%s - %s)" % (tag, url, start, end))

start = ""
end = ""
tag = "intro"
path = "data/dataset.json"
url = ""

def execute(argv):
    doCount = False 
    for i in range(1, len(argv)):
        if (argv[i] == "-s" or argv[i] == "-start") and i + 1 < len(argv):
            start = argv[i + 1]
        elif (argv[i] == "-e" or argv[i] == "-end") and i + 1 < len(argv):
            end = argv[i + 1]
        elif (argv[i] == "-t" or argv[i] == "-tag") and i + 1 < len(argv):
            tag = argv[i + 1]
        elif (argv[i] == "-url") and i + 1 < len(argv):
            url = argv[i + 1]
        elif(argv[i] == "-count"):
            doCount = True

    if (url != "" and tag != "" and start != "" and end != "" and path != ""):
        manual_annotation(path, url, tag, start, end)
    else:
        print("Error: Not enough arguments provided") 

    if doCount:
        count = 0
        with open(path) as json_file:
            data = json.load(json_file)
            for value in data[tag]:
                count = count + 1
        print("Total %s count: %d" % (tag, count))