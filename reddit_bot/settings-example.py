# -*- coding: utf-8 -*-

#
# NOTE: The spiders is meant to be called from outside top "reddit_bot" folder.
#

from logging import DEBUG


BOT_NAME = 'reddit_bot'

SPIDER_MODULES = ['reddit_bot.spiders']
NEWSPIDER_MODULE = 'reddit_bot.spiders'

USER_AGENT = 'reddit scrapper by jurgonaut'

CONCURRENT_REQUESTS = 1
DOWNLOAD_DELAY = 1
CONCURRENT_REQUESTS_PER_DOMAIN = 1
CONCURRENT_REQUESTS_PER_IP = 1

DUPEFILTER_CLASS = "scrapy.dupefilters.BaseDupeFilter"

ITEM_PIPELINES = {
   'reddit_bot.pipelines.CSVPipeline': 100
}

DOWNLOADER_MIDDLEWARES = {
   'reddit_bot.middlewares.CookieMiddleware': 725
}

LOG_LEVEL = "DEBUG"

# A list of categories you wish to scrape
CATEGORIES = [
   "upvoted",
   #"saved",
   #"hidden",
   #"downvoated"
]

# Path to the last_scrapped.json file.
CATEGORIES_PATH = "categories.json"

# Reddit credentials
REDDIT_USERNAME = ""  # this can be set as a env variable
REDDIT_PASSWORD = "" # this can be set as a env variable

# Reddit app credentials
REDDIT_APP_CLIENT_ID = "" # this can be set as a env variable
REDDIT_APP_SECRET = "" # this can be set as a env variable

# Path to the where the posts and comments are stored.
CSV_PATH = "reddit_activities.csv"