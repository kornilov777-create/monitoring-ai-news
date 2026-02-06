from .rss_parser import RSSParser

class OpenAIBlogParser(RSSParser):
    def __init__(self):
        super().__init__(
            source_name="OpenAI Blog",
            source_url="https://openai.com/blog",
            feed_url="https://openai.com/blog/rss.xml"
        )
