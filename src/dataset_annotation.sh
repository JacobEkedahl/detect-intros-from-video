#!/bin/sh

url="https://www.svtplay.se/video/24912149/langtans-blaa-blomma/langtans-blaa-blomma-sasong-1-avsnitt-4-1?start=auto"

start="00:00:40"

end="00:01:18"

tag="intro"

py src/main.py --ann -dataset -tag $tag -s $start -e $end -url $url -count