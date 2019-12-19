#!/bin/sh

scene_file="temp/al-pitcher-pa-paus.json"

start="00:00:31" 

end="00:01:15"

tag="intro"

# There are more optional arguments

py src/main.py --ann -tag $tag -s $start -e $end -print 

