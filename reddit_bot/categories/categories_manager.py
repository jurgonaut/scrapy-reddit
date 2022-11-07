from reddit_bot.categories import Category
import json
from pathlib import Path
import logging

class CategoriesManager():
    def __init__(self):
        self.xCategories = []

    def read_categories(self, aPath, xSettingsCategories):
        xJsonCategories = []

        oPath = Path(aPath)
        xJsonCategories = []

        if oPath.is_file():
            try:
                logging.info("Reading categories from file")
                with open(oPath, "r") as oFile:
                    xJsonCategories = json.loads(oFile.read())
            except Exception as e:
                logging.error(f"Couldn't open file: {oPath}")
                raise

        # Check if the categories in the JSON file are present and if so get the values 
        # for first_id and last_id
        for aCategory in xSettingsCategories:
            oNewCategory = Category()
            oNewCategory.set_name(aCategory)

            for oJsonCategory in xJsonCategories:
                if aCategory == oJsonCategory["name"] and oJsonCategory["status"]:
                    aJsonCategoryFirstId = oJsonCategory["status"].get("first_id")
                    oNewCategory.update_first_id(aJsonCategoryFirstId)

                    aJsonCategoryLastId = oJsonCategory["status"].get("last_id")
                    oNewCategory.update_last_id(aJsonCategoryLastId)
                    break
            
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
        for oCategory in self.get_all_categories():
            if oCategory.get_name() == aKey:
                return oCategory
        return None

    def get_all_categories(self):
        return self.xCategories