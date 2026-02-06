from .rss_parser import RSSParser

class VentureBeatParser(RSSParser):
    def __init__(self):
        super().__init__(
            source_name="VentureBeat AI",
            source_url="https://venturebeat.com/category/ai/",
            feed_url="https://venturebeat.com/category/ai/feed/"
        )
