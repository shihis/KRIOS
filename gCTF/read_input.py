# Read parameters from input file
# function to read parameters from an input text file
# usage lines with # are ignored


def read_input(inputFile):
    if not inputFile:
        print("read input funktion needs the in put file as parameter"
              "please specify an input file"
              "USAGE: read_input(inputfile) parses the in putfile and loads parameters in a dictionary")
        exit()
    #inputFile = "input.cfg"
    fileObj = open(inputFile)
    params = {}
    for line in fileObj:
        line = line.strip()
        if not line.startswith("#"):
            line = line.split("#",1)[0]
            line = line.rstrip()
            print (line)
            key_value = line.split("=")
            if len(key_value) == 2:
                params[key_value[0].strip()] = key_value[1].strip()
    fileObj.close()
    return params


print(read_input("input.dat"))