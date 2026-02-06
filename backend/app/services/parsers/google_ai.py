from .rss_parser import RSSParser

class GoogleAIParser(RSSParser):
    def __init__(self):
        super().__init__(
            source_name="Google AI Blog",
            source_url="https://blog.research.google/",
            feed_url="https://blog.research.google/feeds/posts/default"
        )
