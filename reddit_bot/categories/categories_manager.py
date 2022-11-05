from reddit_bot.categories import Category
import json
from pathlib import Path
import logging

class CategoriesManager():
    def __init__(self):
        self.xCategories = []

    def read_categories(self, aPath, oSettings):
        xJsonCategories = []

        oPath = Path(aPath)

        if oPath.is_file():
            try:
                logging.info("Reading categories from file")
                with open(oPath, "r") as oFile:
                    xJsonCategories = json.loads(oFile.read())
            except Exception as e:
                logging.error(f"Couldn't open file: {oPath}")
                raise
        else:
            logging.info("Generating categories object")
            for aCategory in oSettings.get("CATEGORIES"):
                xJsonCategories.append({"name": aCategory})

            logging.info("Creating categories file")
            oPath.touch(exist_ok=True)

        for oCategory in xJsonCategories:
            oNewCategory = Category()
            oNewCategory.from_json(oCategory)
            self.xCategories.append(oNewCategory)
            
    def write_categories(self, aPath):
        xJsonCategories = []
        for oCategory in self.get_all_categories():
            xJsonCategories.append(oCategory.to_dict())

        try:
            with open(aPath, 'w') as oFile:
                oFile.write(json.dumps(xJsonCategories, indent=4))
        except Exception as e:
            logging.error(f"Couldn't write to CATEGORIES_PATH is spider_closed, exception: {e}")

    def get_category(self, aKey):
        for oCategory in self.xCategories:
            if oCategory.get_name() == aKey:
                return oCategory
        raise RuntimeError(f"Category {aKey} not found")

    def get_all_categories(self):
        return self.xCategories