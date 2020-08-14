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

start_url = 'http://www.pondr.com/'


# list of all the predictors we want to get data from
predictors = ['VLXT', 'XL1', 'CAN', 'VL3', 'VSL2']

## check if sequence from cmd line is in correct format
#if seq.startswith('>') == False:
#    print(seq + ' does not seem to be a valid protein sequence')
#    sys.exit()
    
def download_results(data):
    
    #split into list by lines
    data = data.splitlines()
    
    #remove header row
    data = data[1:]
    
    # create consistent file name 
    file_name = ID + '-PONDR'
    
    path = '/home/galmog/Documents/Disorder/Disorder_Data/PONDR/'
    
    # download the data
    with open(path + file_name + '.csv', 'w') as f:
        f.write(ID + ' ' + datetime.today().strftime('%Y-%m-%d') + ' ' + 'PONDR-' + predictors[0] + ' ' + 'PONDR-' + predictors[1] + ' ' + 'PONDR-' + predictors[2] + ' ' + 'PONDR-' + predictors[3] + ' ' + 'PONDR-' + predictors[4] + '\n')
#        f.write(str(data))
        wr = csv.writer(f)
        for val in data:
            wr.writerow(val.split(' '))

def submit_sequence(sequence, url):
    # create instance of chrome webdriver 
    # need to add chromedriver to path, or specify its location here
    browser = webdriver.Chrome('/home/galmog/chromedriver')
    
    # navigate to page
    browser.get(url)
    
    # check all checkboxes of predictors we are interested in (all but CDF and charge-hydropathy)
    for i in predictors:
        predictor = browser.find_element_by_name(i)
        if predictor.is_selected() == False:
            predictor.click()
            
    #fill in sequence
    Sequence = browser.find_element_by_name('Sequence')
    Sequence.send_keys(seq)
    
    # click raw output
    browser.find_element_by_name('wcwraw').click()
    
    # uncheck all output forms we don't want
    checkboxes = ['graphic', 'stats', 'seq']
    for i in checkboxes:
        checkbox = browser.find_element_by_name(i) 
        if checkbox.is_selected():
            checkbox.click()
    
    #submit form
    browser.find_element_by_name('submit_result').click()
    
    # wait for page to finish loading
    WebDriverWait(browser, 3600).until(EC.presence_of_element_located((By.XPATH, '/html/body/pre[5]')))
    
    # get disorder data
    data = browser.find_element_by_xpath('/html/body/pre[6]').text
    
    browser.close()
    
    return data

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
    
    submitted_page = submit_sequence(seq, start_url)

    download_results(submitted_page)
    
    time.sleep(60)
    


