import time


def H_M_S_to_seconds(str):
    t0 = time.strptime(str.split('.')[0],'%H:%M:%S')
    try:
        t1 = str.split('.')[1]
        f1 = float(t1[0:3])
    except:
        f1 = 0.0
    return t0.tm_hour*3600 + t0.tm_min*60 + t0.tm_sec + f1/1000


def seconds_to_H_M_S(seconds):
    return time.strftime('%H:%M:%S', time.gmtime(seconds))