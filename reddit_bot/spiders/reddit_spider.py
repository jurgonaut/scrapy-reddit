from pprint import pprint
import scrapy
from scrapy import signals
from scrapy.utils.project import get_project_settings
from reddit_bot.items import RedditEntryItem
from datetime import datetime

import json
from pathlib import Path
import os

class RedditSpider(scrapy.Spider):
    name = "reddit"

    def __init__(self, *args, **kwargs):
        self.http_user = ""   # for reddit client id
        self.http_pass = ""   # for reddit secret
        self.reddit_user = "" # reddit username
        self.reddit_pass = "" # reddit password
        self.settings = get_project_settings()

        self.oActivities = {}       # dict of activities 
        self.oActivities_first = {} # dict of activities first encountered id.

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        """
            Connect spider_opened and spider_closed to appropriate methods.
        """

        spider = super(RedditSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        return spider

    def spider_opened(self, spider):
        """
            Check if all needed settings are set before starting and 
            Fill activities_first list.
        """

        # Check if LAST_SCRAPED_PATH exists
        if not Path(self.settings.get("LAST_SCRAPED_PATH")).is_file():
            self.logger.error("File LAST_SCRAPED_PATH doesnt exist")
            return
        
        # Try to load LAST_SCRAPED_PATH into self.oActivities as JSON
        with open(self.settings.get("LAST_SCRAPED_PATH"), "r") as oFile:
            try:
                self.oActivities = json.loads(oFile.read())
            except Exception as e:
                # If there was an error loading the activities 
                # genereate a new dict for them
                for aActivity in self.settings.get("ACTIVITIES"):
                    self.oActivities[aActivity] = {"last_id": ""}

        # Check for reddit app client id
        self.http_user = self.settings.get("REDDIT_APP_CLIENT_ID")
        if not self.http_user:
            self.logger.error(f'Error REDDIT_APP_CLIENT_ID missing from config')
            return

        # Check for reddit app secret
        self.http_pass = self.settings.get("REDDIT_APP_SECRET")
        if not self.http_pass:
            self.logger.error(f'Error REDDIT_APP_SECRET missing from config')
            return         
        
        # Check for reddit username
        if os.environ.get('REDDIT_USERNAME'):
            self.reddit_user = os.environ.get('REDDIT_USERNAME')
        elif self.settings.get("REDDIT_USERNAME"):
            self.reddit_user = self.settings.get("REDDIT_USERNAME")
        else:
            self.logger.error(f'Error REDDIT_USERNAME missing from config or env variable')
            return

        # Check for reddit password
        if os.environ.get('REDDIT_PASSWORD'):
            self.reddit_pass = os.environ.get('REDDIT_PASSWORD')
        elif self.settings.get("REDDIT_PASSWORD"):
            self.reddit_pass = self.settings.get("REDDIT_PASSWORD")
        else:
            self.logger.error(f'Error REDDIT_PASSWORD missing from config or env variable')
            return

        # When spider is opened fill the oActivities_first dict with values from oActivities
        #for aKey in self.oActivities.keys():
        #   self.oActivities_first[aKey] = ""
        for aActivity in self.settings.get("ACTIVITIES"):
            self.oActivities_first[aActivity] = ""

            # If an activity is missing form the settings specified
            # activities, create it.
            if not self.oActivities.get(aActivity):
                self.oActivities[aActivity] = {"last_id": ""}

    def spider_closed(self, spider):
        """
            Update the oActivites with the first activities and write that 
            to the LAST_SCRAPED_PATH file so that we can use that to stop
            the next time we scrape.
        """

        # When spider is closed replace last_id with the first encountered id from oActivities_first
        for aKey, aVal in self.oActivities_first.items():
            self.oActivities[aKey]["last_id"] = aVal

        # Write self.oActivities to LAST_SCRAPED_PATH as JSON
        with open(self.settings.get("LAST_SCRAPED_PATH"), 'w') as oFile:
            oFile.write(json.dumps(self.oActivities))

    def start_requests(self):
        """
            Login to reddit.
        """

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
        """
            Make requests for all activities (saved, upvoted, ...) set in ACTIVITIES.
        """

        for aKey in self.oActivities.keys():
            yield self.generate_request_activity(aKey)

    def get_activities(self, response):
        """
            Get the posts and comments in the currently searched activity.
            If we didnt find the last post from the previous run. call
            generate_request_activity until we do.
        """

        aCurrent = ""
        aKey = response.meta["key"]
        nCount = response.meta["count"]

        try:
            response_json = json.loads(response.text)
            xData = response_json["data"]["children"]
        except Exception as e:
            self.logger.error(f'Error importing json, error {e}')
            return
        
        for oData in xData:
            oData_body = oData["data"].get("body")

            # If removed continue
            if oData_body and "removed" in oData_body:
                continue

            # Get the current id
            aCurrent = oData["data"]["name"]

            # If oActivities_first is empty, fill it
            # we will save it when the spider is done
            if not self.oActivities_first[aKey]:
                self.oActivities_first[aKey] = aCurrent

            # If a current == last_id then we are done
            if aCurrent == self.oActivities[aKey]["last_id"]:
                return

            # Populate the item and yield it.
            oEntry = RedditEntryItem()
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
                oEntry["body"] = oData["data"]["body"]
            else:
                oEntry["body"] = ""

            nTime_stamp = int(oData["data"]["created"])
            oDate_created = datetime.utcfromtimestamp(nTime_stamp).strftime('%Y-%m-%d')
            oEntry["date"] = str(oDate_created)

            yield oEntry

            nCount += 1

        # Get the next batch of activities.
        yield self.generate_request_activity(aKey, aCurrent, nCount)

    def error(self, failure):
        """
            Log the error if any.
        """

        # Check for RuntimeError exception
        if failure.check(RuntimeError):
            self.crawler.engine.close_spider(self, 'Scraper stopped because error occurred.')
            return

        # If http status 404 we are done
        if int(failure.value.response.status) == 404:
            return

        self.logger.error(failure)

    def generate_request_activity(self, aKey, aAfter = None, nCount = 0):
        """
            Return a scrapy request for the next batch of post/comments
            in searched activity(key) and/or after post(aAfter).
        """

        aUrl = f'https://oauth.reddit.com/user/{self.reddit_user}/{aKey}'
        if aAfter:
            aUrl += f'?after={aAfter}'
        if nCount > 0:
            aUrl += f'&count={nCount}'

        return scrapy.Request(
            url=aUrl,
            meta={
                "last": aAfter,
                "count": nCount,
                "key": aKey
            },
            callback=self.get_activities,
            errback=self.error
        )
