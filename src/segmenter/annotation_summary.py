import json 
import os 
import statistics 

import utils.file_handler as file_handler

start_errors = []
end_errors = []

def read_result(filePath, tag):
    global start_errors
    global end_errors
    line = ""
    with open(filePath) as json_file:
        data = json.load(json_file)
        if tag in data: 
            if 'start' in data[tag]:
                line = line + data[tag]['start'] + "\t"
            else:
                line = line + "--\t\t"
            if 'suggestedStart' in data[tag]:
                line = line + data[tag]['suggestedStart'] + "\t\t"
            else:
                line = line + "--\t\t"
            if 'startError' in data[tag]:
                line = line + ("%f" % data[tag]['startError']) + "\t\t"
                start_errors.append(abs(data[tag]['startError']))
            else:
                line = line + "--\t\t"
            if 'end' in data[tag]:
                line = line + data[tag]['end'] + "\t"
            else:
                line = line + "--\t\t"
            if 'suggestedEnd' in data[tag]:
                line = line + data[tag]['suggestedEnd'] + "\t\t"
            else:
                line = line + "--\t\t"
            if 'endError' in data[tag]:
                line = line + ("%f" % data[tag]['endError']) + "\t"
                end_errors.append(abs(data[tag]['endError']))
            else:
                line = line + "--\t\t"
            line = line + "" + os.path.splitext(filePath)[0]
    if line != "":
        print(line)




def execute(argv):
    path = file_handler.get_full_path_temp()
    tag = 'intro'
    for i in range(1, len(argv)):
        if (argv[i] == "-path" or argv[i] == "-p") and i + 1 < len(argv):
            path = argv[i + 1]
        elif (argv[i] == "-tag" or argv[i] == "-t") and i + 1 < len(argv):
            tag = argv[i + 1]
            
    files = file_handler.get_all_files_by_type(path, 'json')
    print("Start\t\tSceneStart\t\tStartError\t\tEnd\t\t SceneEnd\t\tEndError\tFile")
    for file in files: 
        read_result(file, tag)
    print("")
    print("Start Error avg:     %f" % statistics.mean(start_errors))
    print("Start Error median:  %f" % statistics.median(start_errors))
    print("Start Error stdev:   %f" % statistics.stdev(start_errors))
    print("End Error avg:       %f" % statistics.mean(end_errors))
    print("End Error median:    %f" % statistics.median(start_errors))
    print("End Error stdev:     %f" % statistics.stdev(start_errors))

