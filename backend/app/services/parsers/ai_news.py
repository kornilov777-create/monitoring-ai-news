from .rss_parser import RSSParser

class AINewsParser(RSSParser):
    def __init__(self):
        super().__init__(
            source_name="AI News",
            source_url="https://www.artificialintelligence-news.com/",
            feed_url="https://www.artificialintelligence-news.com/feed/"
        )
