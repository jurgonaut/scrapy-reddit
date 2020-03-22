# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.utils.project import get_project_settings

from .xlsx_parser.xlsx_parser import XlsxParaser
from pathlib import Path
import os
import string
from .items import RedditEntryItem

class XlsxPipeline(object):
    def __init__(self): 
        self.xlsx_parser = None

    def open_spider(self, spider):
        oSettings = get_project_settings()

        # Set the xlsx parser
        oXlsx_path = self.resolve_path(oSettings.get("XLSX_PATH"))

        self.xlsx_parser = XlsxParaser(oXlsx_path)
        self.xlsx_parser.open()

        xSheets = self.xlsx_parser.get_sheets()

        xActivities = oSettings.get("ACTIVITIES")
        for aActivity in xActivities:
            # Create the sheets if they are missing
            if not aActivity in xSheets:
                self.xlsx_parser.create_sheet(aActivity)

            # If headers are found continue
            if self.xlsx_parser.find_headers(aActivity):
                continue

            # Else create them
            xHeaders = []
            item = RedditEntryItem()
            xColumns = list(string.ascii_uppercase) # Get alphabet letters in a list eg: ["A", "B", "C", "D", ...]
            for nColumn, aKey in enumerate(item.fields):
                xHeaders.append({"header": aKey, "index": xColumns[nColumn], "start": 1})

            self.xlsx_parser.set_headers(xHeaders, aActivity)

    def close_spider(self, spider):
        self.xlsx_parser.close()

    def process_item(self, item, spider):
        xTo_insert = []
        for oItem in item.items():
            xTo_insert.append({"header": oItem[0], "data": oItem[1]})

        self.xlsx_parser.append_rows(xTo_insert, aSheet_name = item["activity"], bAppend_if_none = False)

        return item

    def resolve_path(self, aPath):
        if not aPath:
            raise RuntimeError(f"XLSX_PATH: {aPath} not defined")

        # Check if full path
        if Path(aPath).is_file():
            return Path(aPath)
        
        # Check if relative path
        oCurrent_path = Path(os.path.realpath(__file__)).parent
        if not aPath.startswith("/"):
            aPath = "/" + aPath
        
        oPath = Path(f'{oCurrent_path}{aPath}')
        if oPath.is_file():
            return oPath
        
        raise RuntimeError(f"Couldnt find {aPath}")
