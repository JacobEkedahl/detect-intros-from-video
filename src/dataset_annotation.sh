#!/bin/sh

url="https://www.svtplay.se/video/24876742/unga-kvinnor/unga-kvinnor-sasong-1-avsnitt-2"


start="00:01:14"
end="00:01:44"

tag="intro"

py src/main.py --dataset -annotate -tag $tag -s $start -e $end -url $url -count

