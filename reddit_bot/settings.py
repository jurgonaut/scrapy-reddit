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
   'reddit_bot.pipelines.XlsxPipeline': 100
}

DOWNLOADER_MIDDLEWARES = {
   'reddit_bot.middlewares.CookieMiddleware': 725
}

LOG_LEVEL = "DEBUG"

# A list of activities you wish to scrape
ACTIVITIES = [
   "upvoted",
   "saved",
   #"hidden",
   #"downvoated"
]

# Full path to the last_scrapped.json file.
LAST_SCRAPED_PATH = "/home/jurij/Projects/Projects-old/reddit_scrapper/reddit_bot/last_scrapped.json"
# Reddit credentials
REDDIT_USERNAME = ""  # this can be set as a env variable, eg: export REDDIT_USERNAME="..." on Linux
REDDIT_PASSWORD = "" # this can be set as a env variable, eg: export REDDIT_PASSWORD="..." on Linux

# Reddit app credentials
REDDIT_APP_CLIENT_ID = ""
REDDIT_APP_SECRET = ""

# Full or relative path to the where the posts and comments are stored.
XLSX_PATH = "reddit_activities.xlsx"