#!/bin/sh

url="https://www.svtplay.se/video/23536930/allt-jag-inte-minns/allt-jag-inte-minns-sasong-1-avsnitt-1"


start="00:00:41"
end="00:01:55.7"

tag="intro"

py src/main.py --dataset -annotate -tag $tag -s $start -e $end -url $url 

