import os


def get_full_path_temp():
    return os.path.join(str(os.getcwd()), "temp")

def get_full_path_folder(folder_name):
    return os.path.join(get_full_path_temp(), folder_name)

def get_all_urls_from_file(file_name):
    text_file_path = os.path.join(get_full_path_temp(), file_name)
    return [line.rstrip('\n') for line in open(text_file_path)]

def get_all_full_path_mkv(folder_name):
    return "hi"
