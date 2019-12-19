#!/bin/sh

srt_file="temp/subs-labb/var-tid-ar-nu.s01e01.1-freden.srt"
scene_file="temp/subs-labb/var-tid-ar-nu.s01e01.1-freden-converted.json"

py src/main.py --subs $srt_file $scene_file -print