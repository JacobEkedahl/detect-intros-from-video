# Source: https://github.com/pgrabovets/srt-to-json

import re
import json

def parse_srt(srt_string):
    srt_list = []
    for line in srt_string.split('\n\n'):
        if line != '':
            index = int(re.match(r'\d+', line).group())
            pos = re.search(r'\d+:\d+:\d+,\d+ --> \d+:\d+:\d+,\d+', line).end() + 1
            content = line[pos:]
            start_time_string = re.findall(r'(\d+:\d+:\d+,\d+) --> \d+:\d+:\d+,\d+', line)[0]
            end_time_string = re.findall(r'\d+:\d+:\d+,\d+ --> (\d+:\d+:\d+,\d+)', line)[0]
            srt_list.append( {
                'index': index, 
                'content': content,
                'start': start_time_string,
                'end': end_time_string
            } )
    return srt_list

