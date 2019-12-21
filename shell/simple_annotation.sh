#!/bin/sh

url="https://www.svtplay.se/video/23578398/hamnd-och-karlek/hamnd-och-karlek-sasong-1-avsnitt-5?start=auto"

start="00:00:00"

end="00:00:22"

tag="intro"

py src/annotations/simple_annotation.py -tag $tag -s $start -e $end -url $url -count