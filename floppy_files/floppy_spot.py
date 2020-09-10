import os, sys

sequence = "MGGKWSKSSIVGWPAIRERMRRTPPTPPAAEGVGAVSQDLERRGAITSSNTRANNPDLAWLEAQEEDEVGFPVRPQVPLRPMTYKGAVDLSH"
id = "test"

# function to run spot-disorder predictor
def spotdis2(sequence):
    fpath = "./spotdis.txt"
    cmd = "python ./spot-disorderG.py " + sequence
    # os.system(cmd + " > " + fpath)
    os.system(cmd)
    data = ""

    with open(fpath, 'r') as file:
        data = file.read()
        file.close()
    os.remove(fpath)
    return (data)


spotdis = spotdis2(sequence)

print(spotdis)