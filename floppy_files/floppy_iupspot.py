#!/usr/bin/env python
import os, sys

sequence = "MGGKWSKSSIVGWPAIRERMRRTPPTPPAAEGVGAVSQDLERRGAITSSNTRANNPDLAWLEAQEEDEVGFPVRPQVPLRPMTYKGAVDLSH"
id = "test"


# function to run iupred predictor
def iupred2(sequence):
    fpath = "./iupred.txt"
    cmd = "python3 ./iupred2a.py " + sequence + " long"
    os.system(cmd + " > " + fpath)
    data = ""

    with open(fpath, 'w') as file:
        data = file.read()
        file.close()
    os.remove(fpath)
    return (data)


iupred = iupred2(sequence)
print(iupred)


# function to run spot-disorder predictor
def spotdis2(sequence):
    fpath = "./spotdis.txt"
    cmd = "python ./spot-disorderG.py " + sequence
    # os.system(cmd + " > " + fpath)
    os.system(cmd)
    data = ""

    with open(fpath, 'w') as file:
        data = file.read()
        file.close()
    os.remove(fpath)
    return (data)


spotdis = spotdis2(sequence)
print(spotdis)

# if __name__ == "__main__":
#    iupred(sequence, id)
