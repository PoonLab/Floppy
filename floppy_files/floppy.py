import sys
import requests
import re
import numpy as np
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import csv
from Bio import SeqIO

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

for header, sequence in seqs.items():
    sequence_aa = sequence
    seq = ">" + header + "\n" + sequence + "\n"
    print(seq)

"""
add iupred and spotdis
"""
pondr = pondr(seq)
pondrfit = pondrfit(seq)
disprot = disprot(seq)
cspritz = cspritz(seq)
espritz = espritz(seq)

protein = pd.DataFrame()

# load the model from disk
loaded_model = joblib.load('disorder_rf.pkl')

X = protein
sequence = sequence_aa

predictions = loaded_model.predict(X)
