import json
import os
import sys as s
from pathlib import Path

NO_RESULT = ""

# Given a root directory it finds all json files and extract all intros annotated
# Stores this data inside intro.json under output directory 
def extract_intros(path, output):
    files = []
    types = ["*.json"] 

    for ext in types:
        for file in Path(path).rglob(ext):
            fileWithNoDir = os.path.basename(file)
            print(str(fileWithNoDir))
            filePath = str(file)
            with open(filePath) as json_file:
                data = json.load(json_file)
                if "intro" in data:
                    intro = data["intro"]
                    files.append({"url": fileWithNoDir, "start": intro["start"], "end": intro["end"]})
                else:
                    files.append({"url": fileWithNoDir, "start": NO_RESULT, "end": NO_RESULT})

    with open(os.path.join(output, 'intros' + '.json') , 'w') as outfile:
        json.dump(files, outfile)

if __name__ == "__main__":
    extract_intros(s.argv[1], s.argv[2])
