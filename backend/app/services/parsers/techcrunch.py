from .rss_parser import RSSParser

class TechCrunchParser(RSSParser):
    def __init__(self):
        super().__init__(
            source_name="TechCrunch AI",
            source_url="https://techcrunch.com/category/artificial-intelligence/",
            feed_url="https://techcrunch.com/category/artificial-intelligence/feed/"
        )
