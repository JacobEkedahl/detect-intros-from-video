class Video:
    """ Class containing video information """

    def __init__(self, show="", title="", season=0, episode=0, url="", downloaded=False):
        self.show = show
        self.title = title
        self.season = season
        self.episode = episode 
        self.url = url
        self.downloaded = downloaded
        
    def __repr__(self):
        return "Video('{}', '{}', {}, {}, '{}', {})".format(self.show, self.title, self.season, self.episode, self.url, self.downloaded)

    def setDwonloaded(self, flag):
        self.downloaded = flag

    def hasDownloaded(self):
        return self.downloaded 

    @property
    def filename(self):
        return '{}.s{:02}e{:02}'.format(self.show, self.season, self.episode)


def generate_file_name(show, title, season, episode):
    return Video(show, title, season, episode).filename
