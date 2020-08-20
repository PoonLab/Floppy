import sys
import requests
import re
import numpy as np
import pandas as pd
import time
import csv
from Bio import SeqIO
import joblib
import threading
import queue

from floppy_pondrfit import *
from floppy_pondr import *
from floppy_disprot import *
from floppy_cspritz import *
from floppy_espritz import *

# # Define path to fasta file here:
# path = "C:\Users\Galmo\Documents\PoonLab\"

seqs = {}
# fa_file = SeqIO.parse(path + "floppytest.fa", "fasta") # Open file with metadata sequences
fa_file = SeqIO.parse("floppytest.fa", "fasta") # Open file with metadata sequences

# Store sequence and ids in a dictionary
for seq_data in fa_file:
    seqs[seq_data.id] = seq_data.seq

for header, sequence in seqs.items(): #loop through proteins in fasta file - lim 25
    sequence_aa = sequence
    seq = ">" + header + "\n" + sequence + "\n"
    print(seq)

    """
    add iupred and spotdis
    """
    q = queue.Queue()
    if __name__ == "__main__":
        # create threads for each predictor
        pondr = threading.Thread(target=pondr, args = seq)
        pondrfit = threading.Thread(target=pondrfit, args = seq)
        disprot = threading.Thread(target=disprot, args = seq)
        cspritz = threading.Thread(target=cspritz, args = seq)
        espritz = threading.Thread(target=espritz, args = seq)

        pondr.start() # start threads
        pondrfit.start()
        disprot.start()
        cspritz.start()
        espritz.start()

        pondr.join() # wait until all threads finish running
        pondrfit.join()
        disprot.join()
        cspritz.join()
        espritz.join()

        print("Finished collecting data for {}".format(seq))

    protein = pd.DataFrame(
                [pondrfit, pondr[0], pondr[1], pondr[2], pondr[3], pondr[4], disprot[0], disprot[1], disprot[2],
                disprot[3], cspritz[0], cspritz[1], espritz[0], espritz[1], espritz[2]])

    # col_names = list(joblib.load('colnames.pkl'))[2:]
    # protein = pd.DataFrame(
    #             [spotdis, pondrfit, iupred[0]. iupred[1], pondr[0], pondr[1], pondr[2], pondr[3], pondr[4], disprot[0], disprot[1], disprot[2],
    #             disprot[3], cspritz[0], cspritz[1], espritz[0], espritz[1], espritz[2]],
    #             columns = col_names)
    #
    # # load the model from disk
    # loaded_model = joblib.load('disorder_rf.pkl')
    #
    # X = protein
    # sequence = sequence_aa

    # predictions = loaded_model.predict(X)

