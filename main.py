import item
import objects

try:
    from colorama import init
    from colorama import Fore
    init()
except:
    print "Could not initialize colorama";

inventory = []
knownRecipes = []
stack = []

def makeYellow(txt):
    return Fore.YELLOW + txt + Fore.RESET

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
            "help [cmd]": "View help for a command.",
            "alias [cmd]": "List all alternative commands for 'cmd'"
            }
        self.functions = {
            "help": self.doHelp,
            "alias": self.listAliases            
            }

    # Used to combine commands added by child classes to the base class's commands
    def extendCommmands(self, aliases, helptext, functions):
        self.aliases = dict(self.aliases.items() + aliases.items())
        self.helptext = dict(self.helptext.items() + helptext.items())
        self.functions = dict(self.functions.items() + functions.items())



    def doHelp(self, rawinput):
        if len(rawinput.split(" ")) != 1:
            cmd = rawinput.split(" ")[1]
            print makeYellow(cmd) + "    " + self.helptext[self.aliases[cmd]]
            return
        print makeYellow("--------Help text--------")
        for x in self.helptext:
            print makeYellow(x) + " " * (commandMaxLength - len(x)) + self.helptext[x]

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
            print "Usage: alias [verb/command]"
            return
        except NameError:
            print "That command doesn't exist!"
            return

        print makeYellow("Aliases for " + cmd + ":")
        print ", ".join(foundAliases)

    def getInput(self, rawinput):
        if len(rawinput) > 0:
            try:
                a = self.aliases[rawinput.split(" ")[0]]
            except:
                print "Unknown command."
                return
            self.functions[a](rawinput)

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
        self.extendCommmands(aliases, helptext, functions)
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
            "quit": lambda rawinput: stack.pop(),
            "name": self.nameItem,
            "unname": self.unnameItem
        }        
        self.listItems()
        self.extendCommmands(aliases, helptext, functions) 

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

        }
        helptext = {

        }
        functions = {

        }
        self.extendCommands(alias, helptext, functions)

stack.append(MainState())

ItemMaker = item.ItemMaker()
for x in xrange(9):
    inventory.append(ItemMaker.getMaterial("iron"))
for x in xrange(3):
    inventory.append(ItemMaker.getMaterial("feathers"))

while len(stack) > 0:
    input = raw_input(Fore.YELLOW + "> " + Fore.RESET)
    stack[-1].getInput(input)