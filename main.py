import item

try:
    from colorama import init
    from colorama import Fore
    init()
except:
    print "Could not initialize colorama";

inventory = []
stack = []



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
        print Fore.YELLOW + "--------Help text--------"
        for x in self.helptext:
            print Fore.YELLOW + x + Fore.RESET + " " * (commandMaxLength - len(x)) + self.helptext[x]

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

        print Fore.YELLOW + "Aliases for " + cmd + ":" + Fore.RESET
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
                "bag": "inventory"
                }

        helptext = {
            "inventory": "View your inventory."
        }

        functions = {
            "inventory": lambda rawinput: stack.append(InventoryViewState())
        }
        self.extendCommmands(aliases, helptext, functions)


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
            "quit": "quit",
            "exit": "quit",
            "q": "quit"
        }
        helptext = {
            "list": "List all items in bag.",
            "view [number]": "List the stats for an item at the position [number].",
            "exit": "Close the inventory window."
        }
        functions = {
            "list": self.listItems,
            "view": self.viewItem,
            "exit": lambda rawinput: states.pop()
        }
        self.listItems()
        self.extendCommmands(aliases, helptext, functions) 

    def listItems(self, rawinput = ""):        
        for i in xrange(len(inventory)):
            index = str(i)
            print Fore.YELLOW + index + Fore.RESET + " " * (IndexLength - len(index)) + inventory[i].getName()

    def viewItem(self, rawinput):
        index = int(rawinput.split(" ")[1])
        print inventory[index].getProfile()


stack.append(MainState())

ItemMaker = item.ItemMaker()
for x in xrange(10):
    inventory.append(ItemMaker.getMaterial("iron"))

while len(stack) > 0:
    input = raw_input(Fore.YELLOW + "> " + Fore.RESET)
    stack[-1].getInput(input)