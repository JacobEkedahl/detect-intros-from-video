#!/bin/sh

url="https://www.svtplay.se/video/24897218/world-on-fire/world-on-fire-sasong-1-avsnitt-3?start=auto"

start="00:00:31" 

end="00:01:15"

tag="intro"

py src/annotations/simple_annotation.py -tag $tag -s $start -e $end -url $url