# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import pprint
import json
from scrapy.exceptions import IgnoreRequest

class CookieMiddleware(object):
    def __init__(self):
        self.cookies = {}
        self.headers = {}

    def process_request(self, request, spider):
        if self.cookies:
            request.cookies = self.cookies

        if self.headers:
            request.headers.update(self.headers)

        return None

    def process_response(self, request, response, spider):
        # Get cookies
        xResponse_cookies_raw = []
        for key, value in response.headers.items():
            if key == b'Set-Cookie':
                xResponse_cookies_raw = value

        for aCookie in xResponse_cookies_raw:
            aCookie = str(aCookie, 'utf-8')
            aKey_val = aCookie.split(";")[0]
            aKey = aKey_val.split("=")[0]
            aVal = aKey_val.split("=")[1]
            self.cookies[aKey] = aVal

        # Get auth header
        if response.url == "https://www.reddit.com/api/v1/access_token":
            response_json = json.loads(response.text)
            if not response_json.get("access_token"):
                spider.logger.error(f"Couldnt get access token, response: {response.text}")
                raise RuntimeError()
            self.headers["Authorization"] = 'bearer ' + response_json['access_token']

        spider.logger.debug(f'Cookies: {self.cookies}')
        spider.logger.debug(f'Headers: {self.headers}')

        return response
