import item as itempy
import objects

try:
    from colorama import init
    from colorama import Fore, Back, Style
    init()
except:
    print "Could not initialize colorama";

inventory = []
knownRecipes = []
stack = []

def makeYellow(txt):
    return Fore.YELLOW + txt + Fore.RESET

def invert(txt):
    return Fore.BLACK + Back.YELLOW + txt + Style.RESET_ALL

commandMaxLength = 20

class BaseState(object):
    def __init__(self):
        self.aliases = {
            "help":"help",
            "h":"help",
            "alias": "alias",
            "aliases": "alias"
            }   
        self.helptext = {
            "help": "View this.",
            "help": ("[cmd]", "View help for a command."),
            "alias": ("[cmd]", "List all alternative commands for 'cmd'")
            }
        self.functions = {
            "help": self.doHelp,
            "alias": self.listAliases            
            }

    # Used to combine commands added by child classes to the base class's commands
    def extendCommands(self, aliases, helptext, functions):
        self.aliases = dict(self.aliases.items() + aliases.items())
        self.helptext = dict(self.helptext.items() + helptext.items())
        self.functions = dict(self.functions.items() + functions.items())

    def context(self): # If you want to put something in front of the >
        return ""

    def doHelp(self, rawinput):
        try:    
            if len(rawinput.split(" ")) != 1:
                cmd = rawinput.split(" ")[1]
                text = self.helptext[self.aliases[cmd]]
                if type(text) == tuple:
                    print makeYellow(cmd + " " + text[0]) + "    " + text[1]
                else:
                    print makeYellow(cmd) + "    " + text
                return
        except KeyError:
            print "Help text for command '" + makeYellow(cmd) + "' not found."
            return

        print makeYellow("--------Help text--------")
        for x in self.helptext:
            text = self.helptext[self.aliases[x]]
            if type(text) == tuple:
                spaces = " " * (commandMaxLength - len(x + " " + text[0]))
                print makeYellow(x + " " + text[0]) + spaces + text[1]
            else:
                spaces = " " * (commandMaxLength - len(x))
                print makeYellow(x) + spaces + text

    def listAliases(self, rawinput):
        try:
            cmd = rawinput.split(" ")[1]     
            # First, check if the command exists
            if not cmd in self.aliases:
                raise NameError
            # Next, get the base command.
            basecmd = self.aliases[cmd]

            # Find all aliases.
            values = self.aliases.values()
            foundAliases = []
            for x in xrange(len(values)):
                if values[x] == basecmd:
                    foundAliases.append(self.aliases.keys()[x])              

        except IndexError:
            print "Usage:" + makeYellow(" alias [verb/command]")
            return
        except NameError:
            print "That command doesn't exist!"
            return

        print makeYellow("Aliases for " + cmd + ":")
        print ", ".join(foundAliases)

    def getInput(self):   
        rawinput = raw_input(Fore.YELLOW + self.context() + "> " + Fore.RESET)
        print " "       
        if len(rawinput) > 0:
            try:
                a = self.aliases[rawinput.split(" ")[0]]
            except:
                print "Unknown command."
                return
            self.functions[a](rawinput)
            print " "

class MainState(BaseState):
    def __init__(self):
        super(MainState, self).__init__()
        aliases =  { 
                "inventory": "inventory",
                "i": "inventory",
                "bag": "inventory",
                "forge": "forge",
                "make": "forge",
                "create": "forge",
                "f": "forge"
                }

        helptext = {
            "inventory": "View your inventory.",
            "forge": "Interact with the forge in the room."
        }

        functions = {
            "inventory": lambda rawinput: stack.append(InventoryViewState()),
            "forge": lambda rawinput: stack.append(ForgeState(self.forge))
        }
        self.extendCommands(aliases, helptext, functions)
        self.forge = objects.Forge() # forge in the current room.

IndexLength = 4 
class InventoryViewState(BaseState):
    def __init__(self):
        super(InventoryViewState, self).__init__()
        aliases = {
            "list": "list",
            "bag": "list",
            "ls": "list",
            "inventory": "list",
            "i": "list",
            "view": "view",
            "v": "view",
            "look": "view",
            "quit": "quit",
            "exit": "quit",
            "e": "quit",
            "q": "quit",
            "name": "name",
            "nickname": "name",
            "n": "name",
            "unname": "unname",
            "unnickname": "unname",
            "un": "unname"
        }
        helptext = {
            "list": "List all items in bag.",
            "view [number]": "List the stats for an item at the position [number].",
            "exit": "Close the inventory window.",
            "name [item #] [name]": "Nickname an item.",
            "unname [item #]": "Remove the nickname from an item."
        }
        functions = {
            "list": self.listItems,
            "view": self.viewItem,
            "quit": self.exit,
            "name": self.nameItem,
            "unname": self.unnameItem
        }        
        self.listItems()
        self.extendCommands(aliases, helptext, functions) 

    def context(self):
        return "bag"

    def exit(self, rawinput):
        print "You close your bag."
        stack.pop()

    def listItems(self, rawinput = ""):     
        print "In your bag are..."   
        print makeYellow("#   name")
        for i in xrange(len(inventory)):
            index = str(i)
            print makeYellow(index) + " " * (IndexLength - len(index)) + inventory[i].getName()

    def viewItem(self, rawinput):
        index = int(rawinput.split(" ")[1])
        print inventory[index].getProfile()

    def nameItem(self, rawinput):
        args = rawinput.split(" ")
        try:
            itemNum = int(args[1])
            newName = " ".join(args[2:])
        except:
            print "Usage is " + makeYellow("name [item #] [new name]") + "."
            return

        try:
            item = inventory[itemNum]
        except:
            print "Invalid item number input: " + Fore.RED + str(itemNum) + Fore.RESET
            return

        item.nickname = newName
        print "Named " + makeYellow(item.getName(True)) + " as " + makeYellow(item.getName())

    def unnameItem(self, rawinput):
        args = rawinput.split(" ")
        try:
            itemNum = int(args[1])
        except:
            print "Usage is " + makeYellow("unname [item #]") + "."
            return

        try:
            item = inventory[itemNum]
        except:
            print "Invalid item number input: " + Fore.RED + str(itemNum) + Fore.RESET
            return

        oldName = item.nickname
        item.nickname = None
        print "Removed nickname from " + makeYellow(oldName) + "."

class ForgeState(BaseState):
    def __init__(self, forge):
        super(ForgeState, self).__init__()
        alias = {
            "i": "inventory",
            "inventory": "inventory",
            "bag": "inventory",
            "add": "add",
            "a": "add",
            "craft": "craft",
            "make": "craft",
            "c": "craft",
            "m": "craft",
            "create": "craft",
            "list": "view",
            "view": "view",
            "l":"view",
            "v": "view",
            "quit": "quit",
            "q": "quit",
            "exit": "quit",
            "leave": "quit"
        }
        helptext = {
            "inventory": "View your inventory.",
            "add": ("[item #]", "Add a recipe to the forge."),
            "craft": ("[recipe #]", "Create an item from a recipe stored in the forge."),
            'view': ('["recipes"|"items"]', "View recipes or your inventory."),
            "quit": "Exit the forge menu."
        }
        functions = {
            "inventory": lambda rawinput: stack.append(InventoryViewState()),
            "view": self.view,
            "quit": lambda rawinput: stack.pop(),
            "craft": self.prepareCraft
        }
        self.forge = forge
        self.extendCommands(alias, helptext, functions)

    def context(self):
        return "forge"

    def prepareCraft(self, rawinput):
        try:
            recipeNum = int(rawinput.split(" ")[1])
        except:
            print "Usage:" + makeYellow(" craft [recipe #]")
            return
        try:
            item = inventory[recipeNum]
            if item.flag == itempy.ItemType.recipe:
                print "Using recipe for " + item.name + "."
                stack.append(CraftState(self.forge, item))
            else:
                print "Item number " + makeYellow(str(recipeNum)) + " is a " + item.getName() + ", not a recipe."
        except IndexError:
            print "Item number " + makeYellow(str(recipeNum)) + " does not exist."



    def view(self, rawinput):
        args = rawinput.split(" ")
        recipe = ["recipes", "recipe", "r"]
        items = ["items", "item", "i"]
        if args[1] in items:
            stack.append(InventoryViewState())
        elif args[1] in recipe:
            if len(self.forge.recipes) == 0:
                print "There are no recipes loaded into the forge."
            else:
                print "Inside the forge is ..."
                print makeYellow("#   name")
            for x in xrange(len(self.forge.recipes)):
                index = str(x)
                print makeYellow(index) + " " * (4 - len(index)) + self.forge.recipes[x].getName()

class CraftState(BaseState):
    def __init__(self, forge, recipe):
        super(CraftState, self).__init__()
        alias = {
            "quit": "quit",
            "q": "quit",
            "exit": "quit",
            "leave": "quit",
            "view": "view",
            "inventory": "inventory",
            "bag": "inventory",
            "i": "inventory",
            "add": "add",
            "a": "add",
            "q": "quit",
            "remove": "remove",
            "r": "remove",
            "craft": "craft",
            "c": "craft"
        }
        helptext = {
            "quit": "Exit the crafting menu.",
            "view": "View the components of the recipe and ingredients added.",
            "inventory": "Open inventory.",
            "add": ("[item #] to [part letter]", "Add an item from your inventory to the ingredients. Type " + makeYellow("add help") + " for more info." ),
            "remove": ("[part letter]", "Removes an item from a part."),
            "craft": "Creates an item from the ingredients."
        }
        functions = {
            "quit": lambda rawinput: stack.pop(),
            "view": self.printRecipe,
            "inventory": lambda rawinput: stack.append(InventoryViewState()),
            "add": self.addItem,
            "remove": self.removeItem,
            "craft": self.craft
        }
        self.extendCommands(alias, helptext, functions)
        self.recipe = recipe
        # Separate the recipe into portions.
        self.neededParts = {}
        self.optionalParts = {}
        self.itemsAdded = [] # To prevent duplicate items
        # Single length arrays, to allow passing by reference
        for part in recipe.neededParts: 
            self.neededParts[part] = [None]
        for part in recipe.optionalParts:
            self.optionalParts[part] = [None]
        self.forge = forge

        self.printRecipe()

    def context(self):
        return "crafting"   

    def getPartIngredients(self, letter): # converts a letter (A~) to a part list, eg Hilt or Blade.
        number = ord(letter.upper()) - 65
        if number < len(self.neededParts):
            key = self.neededParts.keys()[number]
            return self.neededParts[key]
        else:
            key = self.neededParts.keys()[number - len(letterID)]
            return self.optionalParts[key]

    def printParts(self, parts, counter = 0):
        for part in parts:
            print makeYellow("(" + str(unichr(65 + counter)) + ") " + part) + ":" + " " * (partNameLen - len(part))
            if len(parts[part]) == 0:
                print "\tNone."
            for x in parts[part]:
                if x == None:
                    print "\tnothing"
                else:
                    print makeYellow("\t") + x.getName()
            counter+=1
        return counter


    def printRecipe(self, rawinput = ""):
        print invert("Required parts")
        counter = self.printParts(self.neededParts)
        print invert("Optional parts")
        self.printParts(self.optionalParts, counter)


    def addItem(self, rawinput):
        if rawinput.split(" ")[1] == "help":
            print "Adds the specified item(s) to the recipe to be used as ingredients for a part."
            print makeYellow("add [item #] to [part letter]")
            print "For example, if #5 of your inventory is an iron, and the #1 part of the recipe is the Hilt, type"
            print makeYellow("add 5 to A")
            return
        strs = rawinput.split("to")
        if len(strs) < 2:
            print "Incorrect usage, try " + makeYellow("add [item #] to [recipe part letter]")
            return
        items = strs[0].strip().split(" ")[1:]
        i_str = items[0]
        itemID = int(i_str)
        if itemID in self.itemsAdded:
            print "The item #" + i_str + "(" + inventory[itemID].getName() + ") is already added."
        elif len(inventory) <= itemID:
            print "The item #" + i_str + " does not exist."
        else:
            letterID = strs[1].strip().split(" ")[0]
            old = self.getPartIngredients(letterID)[0]
            if old != None:
                self.removeItem("remove " + letterID)            
            self.getPartIngredients(letterID)[0] = inventory[itemID]
            self.itemsAdded.append(itemID)
            # If there already is an item in that slot
            print "Added " + inventory[itemID].getName() + " to the forge."

    def findPositionOfElement(self, searchList, element):
        return [x for x in range(len(searchList)) if searchList[x] == element]

    def removeItem(self, rawinput):
        strs = rawinput.split(" ")
        letterID = strs[1].strip().split(" ")[0]    
        if len(strs) < 2:
            print "Incorrect usage, try " + makeYellow("remove [recipe part letter]")
            return
        letterID = strs[1].upper()

        # must find real item ID.
        lookingFor = self.getPartIngredients(letterID)[0]    
        realID = self.findPositionOfElement(inventory, lookingFor)
        if len(realID) > 1:
            raise IndexError("More than one item that is identical to given ID.")
        else:
            realID = realID[0]

        if realID in self.itemsAdded:
            self.getPartIngredients(letterID)[0] = None
            self.itemsAdded.remove(realID)            
            print "Removed " + inventory[realID].getName() + " from the forge."
        else:
            print "An item does not exist in " + makeYellow(letterID) + "."

    def allIngredients(self):
        result = []
        for i in self.itemsAdded:
            result.append(inventory[i])
        return result

    def craft(self, rawinput):
        # Check that all required ingredients have at least 1.
        canDo = True
        for p in self.neededParts:
            if len(self.neededParts) > 0:
                continue
            else:
                canDo = False
                print "You haven't provided at least 1 ingredient for " + p + "."
        if not canDo:
            return

        item = itempy.CraftedItem()   
        item.name = self.recipe.name     
        item.properties["weight"] = 0.0
        item.properties["value"] = self.recipe.base["value"]

        ingredients = self.allIngredients()

        for i in ingredients:
            item.properties["weight"] += i.properties["weight"]
            item.properties["value"] += i.properties["value"]
        item.properties["weight"] = round(item.properties["weight"], 2)
        item.properties["value"] = round(item.properties["value"])

        item.mainPart = self.recipe.mainPart
        
        variables = dict(self.neededParts[self.recipe.mainPart][0].properties, **item.properties)
        # Each stat is calculated by "base + expressions"
        for name in self.recipe.exprs: 
            stat = self.recipe.base[name] + self.recipe.exprs[name].evaluate(variables)
            if name in itempy.percents:
                item.properties[name] = round(stat, 4)    
            else:
                item.properties[name] = round(stat, 2)

        for i in ingredients:
            inventory.remove(i)

        inventory.append(item)

        print "Created:"
        print inventory[-1].getProfile()

partNameLen = 15   

stack.append(MainState())

ItemMaker = itempy.ItemMaker()
for x in xrange(9):
    inventory.append(ItemMaker.getMaterial("iron"))
for x in xrange(3):
    inventory.append(ItemMaker.getMaterial("feathers"))
inventory.append(ItemMaker.getRecipeItem("dagger"))

while len(stack) > 0:
    stack[-1].getInput()