from .rss_parser import RSSParser

class TheVergeParser(RSSParser):
    def __init__(self):
        super().__init__(
            source_name="The Verge AI",
            source_url="https://www.theverge.com/ai-artificial-intelligence",
            feed_url="https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"
        )
