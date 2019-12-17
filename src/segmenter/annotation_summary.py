# 
# Creates a summary of the result gathered from annotated data. Allows for filtering
# annotations by start and end errors.                                                     

# Example usage 1:                                                                 
#   py annotation_summary.py --result -tag 'intro'                                                                 
#         
#   Reviews the result for all intro annotations inside temp/
                                                         
# Example usage 2:                                                                 
#   py annotation_summary.py --result -tag 'intro' -path temp/videos                                                                 
#         
#   Reviews the result for all intro annotations inside temp/videos or any other directory of your choice

# Example usage 3:                                                                 
#   py annotation_summary.py --result -tag 'intro' -filter lt 1                                                             
#         
#   Same as before but filters for errors less than 1. Filters are: lt (less than) and gt (greater than)

import json 
import os 
import statistics 

import utils.file_handler as file_handler

start_errors = []
end_errors = []

def read_result(filePath, tag, filter):
    global start_errors
    global end_errors
    line = ""
    startError = None
    endError = None 
    passedFilter = True
    if filter != "":
        filterValue = float(filter.split(" ")[1])
        filter = filter.split(" ")[0]
        passedFilter = False
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
                startError = abs(data[tag]['startError'])
                if filter != "":
                    if filter == "lt" and startError < filterValue:
                        passedFilter = True
                    if filter == "gt" and startError > filterValue:
                        passedFilter = True
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
                endError = abs(data[tag]['endError'])
                if filter != "":
                    if filter == "lt" and endError < filterValue:
                        passedFilter = True
                    if filter == "gt" and endError > filterValue:
                        passedFilter = True
            else:
                line = line + "--\t\t"
            line = line + "" + os.path.splitext(filePath)[0]
    if line != "" and passedFilter:
        if startError is not None:
            start_errors.append(startError)
        if endError is not None:
            end_errors.append(endError)
        print(line)


def execute(argv):
    path = file_handler.get_full_path_temp()
    tag = 'intro'
    filter = ""
    for i in range(1, len(argv)):
        if (argv[i] == "-path" or argv[i] == "-p") and i + 1 < len(argv):
            path = argv[i + 1]
        elif (argv[i] == "-tag" or argv[i] == "-t") and i + 1 < len(argv):
            tag = argv[i + 1]
        elif (argv[i] == "-filter" or argv[i] == "-f"):
            if i + 2 < len(argv):
                if (argv[i + 1] == "lt"):
                    try:
                        f = float(argv[i + 2])
                        filter = "lt " + ("%f" % f)
                    except:
                        print("Error: less than filter must contain a float or integer")
                        return
                elif (argv[i + 1] == "gt"):
                    try:
                        f = float(argv[i + 2])
                        filter = "gt " + ("%f" % f)
                    except:
                        print("Error: greater than filter must contain a float or integer")
                        return
                else:
                    print("Error: Invalid filter specified.")
                    return
            else: 
                print("Error: Not enough arguments provided for filter.")
                return

    files = file_handler.get_all_files_by_type(path, 'json')
    print("Start\t\tSceneStart\t\tStartError\t\tEnd\t\t SceneEnd\t\tEndError\tFile")
    for file in files: 
        read_result(file, tag, filter)
    print("")
    print("Start Error avg:     %f" % statistics.mean(start_errors))
    print("Start Error median:  %f" % statistics.median(start_errors))
    print("Start Error stdev:   %f" % statistics.stdev(start_errors))
    print("End Error avg:       %f" % statistics.mean(end_errors))
    print("End Error median:    %f" % statistics.median(start_errors))
    print("End Error stdev:     %f" % statistics.stdev(start_errors))

