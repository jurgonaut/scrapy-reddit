import scrapy
from scrapy import signals
from scrapy.utils.project import get_project_settings
from reddit_bot.items import RedditEntryItem
from datetime import datetime
from reddit_bot.categories import Category
from reddit_bot.categories import CategoriesManager
from reddit_bot.utils import parse_args

import json
from pathlib import Path

class RedditSpider(scrapy.Spider):
    name = "reddit"

    def __init__(self, *args, **kwargs):
        self.http_user = ""
        self.http_pass = ""
        self.reddit_user = ""
        self.reddit_pass = ""
        self.categories_path = ""
        self.settings = get_project_settings()

        self.xCategories = CategoriesManager()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(RedditSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        return spider

    def spider_opened(self, spider):
        self.http_user = parse_args(self.settings, "REDDIT_APP_CLIENT_ID")
        self.http_pass = parse_args(self.settings, "REDDIT_APP_SECRET")
        self.reddit_user = parse_args(self.settings, "REDDIT_USERNAME")
        self.reddit_pass = parse_args(self.settings, "REDDIT_PASSWORD")
        self.categories_path = parse_args(self.settings, "CATEGORIES_PATH")

        self.xCategories.read_categories(self.categories_path, self.settings.get("CATEGORIES"))

    def spider_closed(self, spider):
        self.xCategories.write_categories(self.categories_path)

    def start_requests(self):
        yield scrapy.FormRequest(
            url="https://www.reddit.com/api/v1/access_token",
            formdata={
                "grant_type": "password",
                "username": self.reddit_user,
                "password": self.reddit_pass
            },
            callback=self.after_login,
            errback=self.error
        )

    def after_login(self, response):
        for oCategory in self.xCategories.get_all_categories():
            aFirst = oCategory.get_first_id() if oCategory.get_first_id() else None
            aLast = oCategory.get_last_id() if oCategory.get_last_id() else None
            
            # If no activities, then we have the first run ever, get only the oldest posts
            if not aFirst and not aLast:
                yield self.generate_request_activity(oCategory.get_name(), self.get_activities_old, aLast, None)
            else:
                yield self.generate_request_activity(oCategory.get_name(), self.get_activities_new, None, aFirst)
                yield self.generate_request_activity(oCategory.get_name(), self.get_activities_old, aLast, None)

    def get_activities_new(self, response):
        aKey = response.meta["key"]
        self.logger.info(f"Getting new activities before {response.meta['last']}, from category {aKey}")

        xEntries = self.parse_response(response, aKey)
        if not xEntries:
            self.logger.info("Done, got all new activities")
            return
        
        aFirst = ""
        for oEntry in xEntries:
            if not aFirst:
                aFirst = oEntry["id"]
            
            yield oEntry

        oCategory = self.xCategories.get_category(aKey)
        oCategory.update_first_id(aFirst)

        yield self.generate_request_activity(aKey, self.get_activities_new, None, aFirst)

    def get_activities_old(self, response):
        aKey = response.meta["key"]
        self.logger.info(f"Getting old activities after {response.meta['last']}, from category {aKey}")

        xEntries = self.parse_response(response, aKey)
        if not xEntries:
            self.logger.info("Done, got all old activities")
            return

        for oEntry in xEntries:
            yield oEntry

        aLast = xEntries[-1]["id"]

        oCategory = self.xCategories.get_category(aKey)
        oCategory.update_last_id(aLast)

        # If first id is empty, we are doing a first run, so just 
        # save the most recent id as first for subsequent runs.
        if not oCategory.get_first_id():
            oCategory.update_first_id(xEntries[0]["id"])

        yield self.generate_request_activity(aKey, self.get_activities_old, aLast, None)

    def parse_response(self, oResponse, aKey):
        try:
            response_json = json.loads(oResponse.text)
            xData = response_json["data"]["children"]
        except Exception as e:
            self.logger.error(f'Error importing json, error {e}')
            return
        
        xEntries = []

        for oData in xData:
            oData_body = oData["data"].get("body")

            # If removed continue
            if oData_body and "removed" in oData_body:
                continue

            # Populate the item and yield it.
            oEntry = RedditEntryItem()
            oEntry["id"] = oData["data"]["name"]
            oEntry["activity"] = aKey
            oEntry["url"] = oData["data"]["permalink"]
            oEntry["subreddit"] = oData["data"]["subreddit"]

            if oData["data"].get("title"):
                oEntry["title"] = oData["data"]["title"]
            elif oData["data"].get("link_title"):
                oEntry["title"] = oData["data"]["link_title"]
            else:
                oEntry["title"] = ""

            if oData["data"].get("body"):
                oEntry["body"] = oData["data"]["body"].replace("\n", " ")
            else:
                oEntry["body"] = ""

            nTime_stamp = int(oData["data"]["created"])
            oDate_created = datetime.utcfromtimestamp(nTime_stamp).strftime('%Y-%m-%d')
            oEntry["date"] = str(oDate_created)

            xEntries.append(oEntry)
        
        return xEntries

    def error(self, failure):
        self.logger.error(failure)

        if failure.check(RuntimeError):
            self.crawler.engine.close_spider(self, 'Scraper stopped because error occurred.')
            return

    def generate_request_activity(self, aKey, fCallback, aAfter = None, aBefore = None):
        aUrl = f'https://oauth.reddit.com/user/{self.reddit_user}/{aKey}?limit=100'

        aLastParsed = ""
        if aAfter:
            aUrl += f'&after={aAfter}'
            aLastParsed = aAfter
        elif aBefore:
            aUrl += f'&before={aBefore}'
            aLastParsed = aBefore

        return scrapy.Request(
            url=aUrl,
            meta={
                "last": aLastParsed,
                "key": aKey
            },
            callback=fCallback,
            errback=self.error
        )

    def writer_response_to_file(self, oResponse, aPath):
        try:
            with open(aPath, 'w') as oFile:
                oFile.write(oResponse.text)
        except OSError as e:
            self.logger.error(f"Couldn't write to {aPath}, error: {e}")
            raise