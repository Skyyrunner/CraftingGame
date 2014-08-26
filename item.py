import json
from prefix import PrefixHolder
import colorama

# This class loads the json files into memory, and also produces materials.
class ItemMaker:
    def __init__(self):
        with open("resources/materials.json") as f:
            self.materials = json.load(f)
        with open("resources/recipes.json") as f:
            self.recipes = json.load(f)

    def getMaterial(self, name):
        item = Item()
        item.name = name
        template = self.materials[name]
        for x in template:      
            if not type(template[x]) in [str, unicode]:      
                expr = PrefixHolder(template[x])
                item.properties[x] = expr.evaluate(item.properties)
            else:
                item.properties[x] = template[x]
        return item

MaxPropertyNameLength = 15
class Item:
    def __init__(self):
        self.properties = {}

    def getPrettyStat(self, stat):
        statval = self.properties[stat]
        if type(statval) == float:
            return round(statval, 2)
        else:
            return statval

    def getName(self):
        # TODO: use a language file to obtain the proper singular/plural name
        return self.name

    def getProfile(self):
        out = ""
        out += " " * (max(MaxPropertyNameLength / 3 * 2 - len(self.getName()), 0)) + "< " + self.getName() + " >"
        for x in self.properties:
            out += "\n" + colorama.Fore.YELLOW + x + " " * (MaxPropertyNameLength - len(x)) \
                    + colorama.Fore.RESET + str(self.getPrettyStat(x))

        return out

