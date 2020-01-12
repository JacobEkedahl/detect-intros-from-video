
import subprocess

import imageio_ffmpeg as ffmpeg


def extract():
    output = "gui/temp/current.ogg"
    command = [ffmpeg._utils.get_ffmpeg_exe(), "-hide_banner", "-loglevel", "panic", "-i", "gui/temp/current-converted.mp4", "-vn", "-acodec", "libvorbis", "-y", output]
    subprocess.call(command) 
