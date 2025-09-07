class WebAppInfo:
    def __init__(self, url):
        self.url = url

    def to_dict(self):
        return {"url": self.url}