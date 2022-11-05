import os
import unittest
from scrapy.http import Response, Request, TextResponse
from reddit_bot.spiders.reddit_spider import RedditSpider

class TestRedditBot(unittest.TestCase):
    def test_generate_request(self):
        oReddit_spider = generate_spider()

        oRequest = generate_request(oReddit_spider, "upvoted", None, None)
        self.assertIn("https://oauth.reddit.com/user/test_user/upvoted", oRequest.url, "Incorrect username in url")
        self.assertNotIn("&after", oRequest.url, "After shouldn't be present when aAfter parameter is not supplied")
        self.assertNotIn("&before", oRequest.url, "Before shouldn't be present when aBefore parameter is not supplied")

        oRequest = generate_request(oReddit_spider, "upvoted", "after", "before")
        self.assertIn("&after=after", oRequest.url, "Only after should be present when both aAfter and aBefore parameters are supplied")
        self.assertNotIn("&before=before", oRequest.url, "Only after should be present when both aAfter and aBefore parameters are supplied")
        self.assertEqual(oRequest.meta["last"], "after", "Last meta key should be equal to aAfter parameters when both aAfter and aBefore parameters are supplied")

        oRequest = generate_request(oReddit_spider, "upvoted", "after", None)
        self.assertIn("&after=after", oRequest.url, "After should be present in url when aAfter parameter is supplied")
        self.assertEqual(oRequest.meta["last"], "after", "Last meta key should be equal to aAfter parameters when aAfter parameters is supplied")

        oRequest = generate_request(oReddit_spider, "upvoted", None, "before")
        self.assertIn("&before=before", oRequest.url, "Before should be present in url when aBefore parameter is supplied")
        self.assertEqual(oRequest.meta["last"], "before", "Last meta key should be equal to aBefore parameters when aBefore parameters is supplied")

        self.assertEqual(oRequest.meta["key"], "upvoted", "The key meta should be equal to the aKey parameter")
        self.assertEqual(oRequest.callback, oReddit_spider.get_activities_old, "The callback should be equal to fCallback parameter")

    def test_parse_response(self):
        oReddit_spider = generate_spider()
        oRequest = generate_request(oReddit_spider, "upvoted", None, None)
        oResponse = generate_response_from_file("./reddit_bot/sample_data/reddit-api-response.json", oRequest)

        xResults = oReddit_spider.parse_response(oResponse, "upvoted")
        self.assertEqual(len(xResults), 2)
        self.assertEqual(xResults[0]["activity"], "upvoted")
        self.assertEqual(xResults[0]["id"], "t3_yas5rk")
        self.assertEqual(xResults[1]["activity"], "upvoted")
        self.assertEqual(xResults[1]["id"], "t3_yb7ygx")

    def test_get_activities(self):
        oReddit_spider = generate_spider()
        oRequest = generate_request(oReddit_spider, "upvoted", None, "t3_yb7ygx")
        oResponse = generate_response_from_file("./reddit_bot/sample_data/reddit-api-response.json", oRequest)

        xResults = oReddit_spider.get_activities_old(oResponse)
        nI = 0
        while xResults:
            oResult = next(xResults)
            if nI == 0:
                self.assertEqual(oResult["activity"], "upvoted")
                self.assertEqual(oResult["id"], "t3_yas5rk")
            elif nI == 1:
                self.assertEqual(oResult["activity"], "upvoted")
                self.assertEqual(oResult["id"], "t3_yb7ygx")
            elif nI == 2:
                self.assertIn("&after=t3_yb7ygx", oResult.url)
                self.assertEqual(oRequest.meta["key"], "upvoted")
                self.assertEqual(oRequest.meta["last"], "t3_yb7ygx")
                break
            nI += 1

        # Todo: test when there are no new activities

def generate_spider():
    os.environ["REDDIT_APP_CLIENT_ID"] = "1234"
    os.environ["REDDIT_APP_SECRET"] = "5678"
    os.environ["REDDIT_USERNAME"] = "test_user"
    os.environ["REDDIT_PASSWORD"] = "test_pass"
    os.environ["CATEGORIES_PATH"] = "./reddit_bot/sample_data/categories.json"

    oReddit_spider = RedditSpider()
    oReddit_spider.spider_opened(oReddit_spider)
    return oReddit_spider

def generate_request(oSpider, aKey, aAfter = None, aBefore = None):
    return oSpider.generate_request_activity(aKey, oSpider.get_activities_old, aAfter, aBefore)

def generate_response_from_file(aPath, oRequest):
    aResponseBody = ""
    try:
        with open(aPath, 'r') as oFile:
            aResponseBody = oFile.read()
    except OSError as e:
        print(f"Couldn't read from {aPath}, error: {e}")

    return TextResponse(
        url = "https://oauth.reddit.com/user/user/key?limit=2",
        body = str.encode(aResponseBody),
        request = oRequest
    )

if __name__ == "__main__":
    unittest.main()