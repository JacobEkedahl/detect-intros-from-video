#!/bin/sh

url="https://www.svtplay.se/video/20373262/en-engelsk-skandal/en-engelsk-skandal-sasong-1-avsnitt-3?start=auto"

start="00:02:33"

end="00:03:09"

tag="intro"

py src/annotations/simple_annotation.py -tag $tag -s $start -e $end -url $url -count