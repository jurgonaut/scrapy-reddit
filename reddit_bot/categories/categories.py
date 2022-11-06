class Category():
    """
        This object represents the data for a category and it's used 
        by the spider to determine where it left off scrapying.
    """

    def __init__(self):
        self.aName = ""
        self.aFirstId = ""
        self.aLastId = ""

    def get_name(self):
        return self.aName

    def set_name(self, aName):
        self.aName = aName

    def get_last_id(self):
        return self.aLastId

    def get_first_id(self):
        return self.aFirstId

    def update_last_id(self, aId):
        self.aLastId = aId

    def update_first_id(self, aId):
        self.aFirstId = aId

    def to_dict(self):
        return {
            "name": self.aName,
            "status": {
                "first_id": self.aFirstId,
                "last_id": self.aLastId
            }
        }
    
    def from_json(self, oJson):
        self.aName = oJson["name"]
        if oJson.get("status"):
            self.update_first_id(oJson["status"]["first_id"])
            self.update_last_id(oJson["status"]["last_id"])

    def __repr__(self):
        return f"Category name: {self.aName}, first id: {self.aFirstId}, last id: {self.aLastId}"

    def __str__(self):
        return f"Category name: {self.aName}, first id: {self.aFirstId}, last id: {self.aLastId}"