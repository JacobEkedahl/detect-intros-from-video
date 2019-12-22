import os
import subprocess

import imageio_ffmpeg as ffmpeg


def convert_audio_to_spec(audio_file):
    pre, ext = os.path.splitext(audio_file)
    output = pre + ".jpg"
    command = [ffmpeg._utils.get_ffmpeg_exe.__call__(), "-i", audio_file, "-lavfi", "showspectrumpic=s=100x100:mode=separate:legend=disabled", "-y", output]
    subprocess.call(command, shell=True) 
