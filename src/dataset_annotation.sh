#!/bin/sh

url="https://www.svtplay.se/video/12524164/hotell-halcyon/hotell-halcyon-sasong-1-avsnitt-4?start=auto"

start="00:01:51"

end="00:02:24"

tag="intro"

py src/main.py --ann -dataset -tag $tag -s $start -e $end -url $url -count