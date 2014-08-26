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

class BaseState:
    def __init__(self):
        self.aliases = {
            "help":"help",
            "h":"help",
            "alias": "alias",
            "aliases": "alias"
            }   
        self.helptext = {
            "inventory": "View your inventory.",
            "help": "View this.",
            "alias [cmd]": "List all alternative commands for 'cmd'"
            }

    def doHelp(rawinput):
        print Fore.YELLOW + "--------Help text--------"
        for x in self.helptext:
            print Fore.YELLOW + x + Fore.RESET + " " * (commandMaxLength - len(x)) + self.helptext[x]

    def listAliases(rawinput):
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
            print "Usage: alias[es] [verb/command]"
            return
        except NameError:
            print "That command doesn't exist!"
            return

        print Fore.YELLOW + "Aliases for " + cmd + ":" + Fore.RESET
        print ", ".join(foundAliases)
        
    def getInput(self, rawinput):
        print rawinput

class MainState(BaseState):
    def getInput(self, rawinput):
        if len(rawinput) > 0:
            try:
                a = aliases[rawinput.split(" ")[0]]
            except:
                print "Unknown command."
                return
            functions[a](rawinput)

functions = {
    "help": doHelp,
    "alias": listAliases
}

stack.append(MainState())

while len(stack) > 0:
    input = raw_input(Fore.YELLOW + "> " + Fore.RESET)
    stack[-1].getInput(input)