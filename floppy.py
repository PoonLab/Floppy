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

# # Define path to fasta file here:
# path = "C:\Users\Galmo\Documents\PoonLab\"

seqs = {}
# fa_file = SeqIO.parse(path + "floppytest.fa", "fasta") # Open file with metadata sequences
fa_file = SeqIO.parse("floppytest.fa", "fasta") # Open file with metadata sequences

# Store sequence and ids in a dictionary
for seq_data in fa_file:
    seqs[seq_data.id] = seq_data.seq

for header, sequence in seqs.items():
    dis = header.split("_")
    ID = dis[0]

    header = ">" + ID
    seq = header + "\n" + sequence + "\n"
    print(seq)

    results = submit_sequence(seq, start_url)

    download_results(results)

    time.sleep(60)

def pondrfit(sequence):
    start_url = 'http://original.disprot.org/pondr-fit.php'
    def download_results(results):
        results = results.splitlines() # split by lines into list
        results = results[1:] # remove extra things we don't want

        # remove extra spaces
        for i in range(len(results)):
            results[i] = results[i].replace('  ', '')
            results[i] = results[i].replace('   ', ' ')
            results[i] = results[i].strip()

        # output to df
        with open(path + file_name + ".csv", 'w') as f:
            # create consistent output header line
            f.write(ID + ' ' + datetime.today().strftime('%Y-%m-%d') + ' ' + 'PONDRFIT' + '\n')
            wr = csv.writer(f)
            for val in results:
                # removing last column - don't know what that value is
                wr.writerow(val.split(' ')[:-1])

    def submit_sequence(sequence, start_url):
        # browser = webdriver.Chrome('C:\Users\Galmo\Documents\PoonLab')
        browser = webdriver.Chrome()
        browser.get(start_url) # navigate to page
        Sequence = browser.find_element_by_name('native_sequence')  # fill in form

        Sequence.send_keys(seq)
        browser.find_element_by_xpath('/html/body/table[3]/tbody/tr[3]/td/input[1]').click() # submit form
        browser.find_element_by_xpath('/html/body/center[1]/a[4]').click() # click link with disorder data
        html = browser.find_element_by_xpath('/html/body/pre').text # parse new page
        browser.close()
        return html