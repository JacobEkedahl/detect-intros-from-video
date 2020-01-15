#!/bin/sh

url="https://www.svtplay.se/video/20332466/andra-aket/andra-aket-sasong-1-avsnitt-6?start=auto"


start="00:01:02"
end="00:01:16"

tag="intro"

py src/main.py --dataset -annotate -tag $tag -s $start -e $end -url $url 

