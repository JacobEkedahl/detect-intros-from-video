#!/bin/sh

url="https://www.svtplay.se/video/15047632/rederiet/rederiet-sasong-1-stoppa-pressarna?start=auto"

start="00:00:00"

end="00:00:58"

tag="intro"

py src/main.py --dataset -annotate -tag $tag -s $start -e $end -url $url -count