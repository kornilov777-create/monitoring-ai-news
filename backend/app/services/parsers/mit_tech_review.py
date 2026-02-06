from .rss_parser import RSSParser

class MITTechReviewParser(RSSParser):
    def __init__(self):
        super().__init__(
            source_name="MIT Technology Review",
            source_url="https://www.technologyreview.com/topic/artificial-intelligence/",
            feed_url="https://www.technologyreview.com/topic/artificial-intelligence/feed"
        )
