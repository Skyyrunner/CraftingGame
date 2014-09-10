import json
from prefix import PrefixHolder
import colorama
from enum import Enum

def makeYellow(txt):
    return colorama.Fore.YELLOW + txt + colorama.Fore.RESET

def makeCyan(txt):
    return colorama.Fore.CYAN + txt + colorama.Fore.RESET 

def invert(txt):
    return colorama.Fore.BLACK + colorama.Back.YELLOW + txt + colorama.Style.RESET_ALL

class ItemType(Enum):
    undefined = 0
    material = 1
    recipe = 2
    craft = 3


# This class loads the json files into memory, and also produces materials.
class ItemMaker:
    def __init__(self):
        with open("resources/materials.json") as f:
            self.materials = json.load(f)
        with open("resources/recipes.json") as f:
            self.recipes = json.load(f)

        with open("resources/affixes.json") as f:
            self.affixes = json.load(f)
            self.affixTable = {}
            for affix in self.affixes:
                self.affixes[affix]["name"] = affix
                for material in self.affixes[affix]["attaches_to"]:
                    try:
                        self.affixTable[material].append(affix)
                    except:
                        self.affixTable[material] = []
                        self.affixTable[material].append(affix)   

        with open("resources/quality.json") as f:
            self.qualities = json.load(f)
    
    def getRecipeItem(self, name):
        item = Recipe()
        ref = self.recipes[name]
        item.name = name
        item.mainPart = ref["recipe"]["main"]
        item.neededParts = ref["recipe"]["parts_needed"]
        item.optionalParts = ref["recipe"]["parts_optional"]
        for key in ref:
            if key == "recipe":
                continue
            # If it's "x_base", store "x" in exprs. Otherwise put it in base
            strs = key.split("_")
            if strs[-1] == "base":
                basename = "_".join(strs[:-1])
                item.base[basename] = ref[key]
            else:
                item.exprs[key] = PrefixHolder(ref[key])

        return item

    # Second argument in case custom properties must be set.
    def getMaterial(self, name, properties = {}):
        item = Item()
        item.name = name
        item.flag = ItemType.material
        template = self.materials[name]
        for x in template:      
            if not type(template[x]) in [str, unicode]:      
                expr = PrefixHolder(template[x])
                item.properties[x] = expr.evaluate(item.properties)
            else:
                item.properties[x] = template[x]

        for x in properties:    
            item.properties[x] = properties[x]
        # Now, scan possible affixes.
        i = 0
        try:
            affixes = self.affixTable[name]
        except KeyError:
            return item # No possible affixes
        maxI = len(affixes)
        while i < maxI:
            # Check that the condition is fulfilled
            affix = self.affixes[affixes[i]] # self.affixes is the actual data for affixes
            # affixes[] is a list of possible affixes to apply to the item.
            expr = PrefixHolder(affix["condition"])
            if expr.evaluate(item.properties): # Condition fulfilled!
                if affix["affix_type"] == "pre":
                    item.prefixes.append(affix)
                elif affix["affix_type"] == "post":
                    item.suffixes.append(affix)
                else:
                    raise NameError(["Cannot identify affix type " + affix["affix_type"]])
            i += 1

        return item

percents = ["balance", "crit chance", "armor pen"]

MaxPropertyNameLength = 15
class Item(object):
    def __init__(self):
        self.properties = {}
        self.prefixes = []
        self.suffixes = []
        self.nickname = None
        self.flag = ItemType.undefined

    def __eq__(self, other):
        if other == None:
            return False
        a = self.properties == other.properties
        b = self.prefixes == other.prefixes
        c = self.suffixes == other.suffixes
        d = self.flag == other.flag
        return a and b and c and d

    def getPrettyStat(self, stat):
        statval = self.properties[stat]
        if type(statval) == float:
            return round(statval, 2)
        else:
            return statval

    def getName(self, ignoreNicknames = False):
        if self.nickname != None and not ignoreNicknames:
            return self.nickname + " (" + self.name + ")"
        # TODO: use a language file to obtain the proper singular/plural name
        prefixes = ""
        suffixes = ""
        for prefix in self.prefixes:
            prefixes += prefix["name"] + " "
        for suffix in self.suffixes:
            suffixes += " " + suffix["name"]
        return prefixes + self.name + suffixes

    def getProfile(self):
        out = ""
        out += " " * (max(MaxPropertyNameLength / 3 * 2 - len(self.getName()), 0)) + "< " + self.getName() + " >"
        for x in self.properties:
            out += "\n" + makeYellow(x) + " " * (MaxPropertyNameLength - len(x)) \
                    + str(self.getPrettyStat(x))

        return out

MaxStatNameLength = 12
class Recipe(Item):
    def __init__(self):
        super(Recipe, self).__init__()
        self.flag = ItemType.recipe
        self.base = {} # The base values for a given stat
        self.exprs = {} # The formula for calculating the final stat.
    
    def __eq__(self, other):
        a = super(Recipe, self).__eq__(other)
        try:
            b = self.base == other.base
        except AttributeError:
            return False # if it doesn't have that element it's not a Recipe
        return a and b

    def getName(self, ignoreNicknames = False):
        if self.nickname != None and not ignoreNicknames:
            return self.nickname + " (" + self.name + " recipe)"
        return self.name + " recipe"

    def getProfile(self):
        out = ""
        out += " " * (max(MaxPropertyNameLength / 3 * 2 - len(self.getName()), 0)) + "< " + self.getName() + " >"
        out += "\n" + invert("Required parts:") + "\n"
        out += "\t" + ",".join(self.neededParts) + "\n"
        out += invert("Optional parts:") + "\n"
        out += "\t" + ",".join(self.optionalParts) + "\n"
        out += invert("Base stats:")
        dmg_min = 0
        dmg_max = 0
        for x in self.base:
            if x in percents:
                out += "\n" + makeYellow(x) + " " * (MaxStatNameLength - len(x)) \
                   + str(int(self.base[x] * 100)) + "%"
            elif x == "min damage":
                dmg_min = self.base[x] 
            elif x == "max damage":
                dmg_max = self.base[x]
            else:
                out += "\n" + makeYellow(x) + " " * (MaxStatNameLength - len(x)) \
                   + str(self.base[x])
        out += "\n" + makeYellow("damage") + " " * (MaxStatNameLength - len("damage")) + str(dmg_min) \
                                          + "~" + str(dmg_max)

        return out

class ItemPart:
    def __init__(self):
        self.name = None
        self.material = None

class CraftedItem(Item):
    def __init__(self):
        super(CraftedItem, self).__init__()
        self.flag = ItemType.craft
        self.parts = {}


    def __eq__(self, other):
        a = super(CraftedItem, self).__eq__(other)
        return a        

    def getProfile(self):   
        out = ""
        out += " " * (max(MaxPropertyNameLength / 3 * 2 - len(self.getName()), 0)) + "< " + self.getName() + " >"
        dmg_min = 0
        dmg_max = 0
        for x in self.properties:
            if x in percents:
                out += "\n" + makeYellow(x) + " " * (MaxStatNameLength - len(x)) \
                   + str(int(self.properties[x] * 100)) + "%"
            elif x == "min damage":
                dmg_min = self.properties[x] 
            elif x == "max damage":
                dmg_max = self.properties[x]
            else:
                out += "\n" + makeYellow(x) + " " * (MaxStatNameLength - len(x)) \
                   + str(self.properties[x])
        out += "\n" + makeYellow("damage") + " " * (MaxStatNameLength - len("damage")) + str(dmg_min) \
                                          + "~" + str(dmg_max)

        return out