#!/bin/sh

url=""
start="00:00:00" 
end="00:00:00"
tag="intro"

py src/annotations/simple_annotation.py -tag $tag -s $start -e $end -url $url