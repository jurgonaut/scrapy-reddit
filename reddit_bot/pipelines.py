# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.utils.project import get_project_settings

from reddit_bot.utils import parse_args
import os
from .items import RedditEntryItem
import csv

class CSVPipeline(object):
    def __init__(self):
        self.oCSVFile = None
        self.oCSVwriter = None

    def open_spider(self, spider):
        oSettings = get_project_settings()
        aCsvPath = parse_args(oSettings, "CSV_PATH")

        try:
            self.oCSVFile = open(aCsvPath, "a")
        except Exception as e:
            spider.logger.error(f"Couldn't open file {aCsvPath}")
            raise

        self.oCSVwriter = csv.writer(self.oCSVFile, delimiter=',', quotechar='"')

        self.oCSVFile.seek(0, os.SEEK_END)
        if self.oCSVFile.tell():
            self.oCSVFile.seek(0)
        else:
            spider.logger.error("CSV file is empty creating header")
            oItemsFields = RedditEntryItem()
            self.oCSVwriter.writerow(oItemsFields.get_fields_names())

    def close_spider(self, spider):
        self.oCSVFile.close()

    def process_item(self, item, spider):
        spider.logger.debug(f"Scraped item: {item.get_values()}")
        self.oCSVwriter.writerow(item.get_values())