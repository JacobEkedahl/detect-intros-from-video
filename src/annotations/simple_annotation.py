import sys
import json 
import os 

argv = sys.argv
start = ""
end = ""
tag = "intro"
path = "temp/simple_annotation.json"
url = argv[1]


def manual_annotation(path, url, tag, start, end):
    if not os.path.exists(path):
        with open(path, 'w') as outfile:
            data = { }
            json.dump(data, outfile)
    url = url.replace('?start=auto', '')
    with open(path) as json_file:
        data = json.load(json_file)

        found = None
        if not tag in data: 
            data[tag] = []
        else:
            for value in data[tag]:
                if (value['url'] == url):
                    found = value
                    print("Warning: %s was saved previously with %s - %s." % (value['url'], value['start'], value['end']))
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
        with open(path, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=False)
        print("%s saved for %s as (%s - %s)" % (tag, url, start, end))


for i in range(1, len(argv)):
    if (argv[i] == "-s" or argv[i] == "-start") and i + 1 < len(argv):
        start = argv[i + 1]
    elif (argv[i] == "-e" or argv[i] == "-end") and i + 1 < len(argv):
        end = argv[i + 1]
    elif (argv[i] == "-t" or argv[i] == "-tag") and i + 1 < len(argv):
        tag = argv[i + 1]
    elif (argv[i] == "-p" or argv[i] == "-path") and i + 1 < len(argv):
        path = argv[i + 1]

if (tag != "" and start != "" and end != "" and path != ""):
    manual_annotation(path, url, tag, start, end)
else:
    print("Error: Not enough arguments provided")