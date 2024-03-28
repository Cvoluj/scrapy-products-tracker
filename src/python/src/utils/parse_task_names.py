import furl


class ParseTaskName():

    def __init__(self) -> None:
        ...
        
    def parse_name(self, url):
        return url.host.split('.')[1]
