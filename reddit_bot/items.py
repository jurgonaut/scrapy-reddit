# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class RedditEntryItem(scrapy.Item):
    id = scrapy.Field()
    activity = scrapy.Field()
    date = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    body = scrapy.Field()
    subreddit = scrapy.Field()

    def get_fields_names(self):
        return ["id", "activity", "date", "url", "title", "body", "subreddit"]

    def get_values(self):
        return [self.get("id"), self.get("activity"), self.get("date"), self.get("url"), self.get("title"), self.get("body"), self.get("subreddit")]