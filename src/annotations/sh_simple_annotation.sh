#!/bin/sh

url="https://www.svtplay.se/video/23885163/vaster-om-friheten/vaster-om-friheten-sasong-1-avsnitt-5?start=auto"

start="00:03:45"

end="00:04:44"

tag="intro"
py src/annotations/simple_annotation.py -tag $tag -s $start -e $end -url $url