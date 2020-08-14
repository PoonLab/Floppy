# -*- coding: utf-8 -*-
import sys
import requests
import re 
import time 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime 
import csv
from Bio import SeqIO

"""
Need to download Selenium package and a driver interface with browser of choice.
See: https://selenium-python.readthedocs.io/installation.html 
"""


start_url = 'http://original.disprot.org/pondr-fit.php'

"""
* will only work if have '>' then sequence on a NEW LINE
"""
#
## check if sequence from cmd line is in correct format
#if seq.startswith('>') == False:
#    print(seq + ' does not seem to be a valid protein sequence')
#    sys.exit()

    # can use a regular expression to ensure FASTA description line is in correct format ?
    
def download_results(results):
    
    # split by lines into list
    results = results.splitlines()
    
    # remove extra things we don't want
    results = results[1:]
    
    # remove extra spaces
    for i in range(len(results)):
        results[i] = results[i].replace('  ', '')
        results[i] = results[i].replace('   ', ' ')
        results[i] = results[i].strip()

    # create consistent file name    
    file_name = ID + '-PONDRFIT'
    path = '/home/galmog/Documents/Disorder/Disorder_Data/PONDRFIT/'
    
    # output to csv
    with open(path + file_name + ".csv", 'w') as f:
        # create consistent output header line
        f.write(ID + ' ' + datetime.today().strftime('%Y-%m-%d') + ' ' + 'PONDRFIT' + '\n')
        wr = csv.writer(f)
        for val in results:
            # removing last column - don't know what that value is
            wr.writerow(val.split(' ')[:-1])   
            
def submit_sequence(sequence, url):
    # create instance of chrome webdriver 
    # need to add chromedriver to path, or specify its location here
    browser = webdriver.Chrome('/home/galmog/chromedriver')
    
    # navigate to page
    browser.get(url)
    
    #fill in form
    Sequence = browser.find_element_by_name('native_sequence')
    
    Sequence.send_keys(seq)
    
    #submit form
    
    browser.find_element_by_xpath('/html/body/table[3]/tbody/tr[3]/td/input[1]').click()

    # click link with disorder data
    browser.find_element_by_xpath('/html/body/center[1]/a[4]').click()

    
    # parse new page
    html = browser.find_element_by_xpath('/html/body/pre').text
        
    browser.close()
    return html
        
# Define path to data file
path = '/home/galmog/Documents/Disorder/'
# Define dictionary
seqs = {}

# Open file with metadata sequences
fa_file = SeqIO.parse(path + "disprot_virus.fa", "fasta")

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
    
