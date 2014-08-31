import json
from os import walk

files = []
for (dirpath, dirnames, filenames) in walk("raw"):
    files.extend(filenames)

for file in files:
    with open("raw/" + file) as f:
        firstline = True
        data = {}
        for line in f:            
            line = line.replace("\n", "")
            if firstline:
                headers = line.split("\t")
                firstline = False
                continue
            elements = line.split("\t")
            obj = data[elements[0]] = {}
            for x in xrange(1, len(elements)):                
                if elements[x] == "":
                    continue
                if elements[x][0] == "[" or elements[x][0] == "{":
                    obj[headers[x]] = json.loads(elements[x])
                else:
                    try:
                        obj[headers[x]] = float(elements[x])
                    except:
                        obj[headers[x]] = elements[x]
        out = open("resources/" + file + ".json", "w")
        json.dump(data, out, sort_keys=True, indent=4, separators=(',', ': '))