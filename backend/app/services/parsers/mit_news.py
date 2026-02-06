from .rss_parser import RSSParser

class MITNewsParser(RSSParser):
    def __init__(self):
        super().__init__(
            source_name="MIT News AI",
            source_url="https://news.mit.edu/topic/artificial-intelligence2",
            feed_url="https://news.mit.edu/rss/topic/artificial-intelligence2"
        )
