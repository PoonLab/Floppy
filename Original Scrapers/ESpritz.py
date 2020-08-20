#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 12:06:46 2019

@author: galmog
"""


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

start_url = 'http://protein.bio.unipd.it/espritz/'


# list mapping prediction options (for scraper) to what to put in the file name
Predictors = [['Xray','X-Ray'], ['Disprot', 'Disprot'], ['NMR', 'NMR']]

# 0 for short, 1 for long
predictor = 2

## check if sequence from cmd line is in correct format
#if seq.startswith('>') == False:
#    print(seq + ' does not seem to be a valid protein sequence')
#    sys.exit()

def download_results(results):
    data = []
    
    results = results.splitlines()
    results[0] = results[0][84:]
    results = results[:-1]
    for i in results:
        new = i[2:]
        data.append(new)
    

    # create consistent file name    
    file_name = ID + '-ESpritz-' + Predictors[predictor][0]
    path = '/home/galmog/Documents/Disorder/Disorder_Data/ESpritz/NMR/'
    
    # download as csv
    with open(path + file_name + '.csv', 'w') as f:
        # no amino acids / location, so leaving out the ID and date
        f.write('ESpritz-' + Predictors[predictor][0] + '\n')
        wr = csv.writer(f)
        for val in data:
            wr.writerow(val.split(' '))
            
            
def check_if_loaded(browser):
    """
    Function to ensure the page has finished running before extracting the results.
    """
    # waits 1 hour before giving Timeout error
    # searches for notice element in the new page to know it has changed
    WebDriverWait(browser, 7200).until(EC.presence_of_element_located((By.ID, 'notice')))


def submit_sequence(sequence, url):
    # create instance of chrome webdriver 
    # need to add chromedriver to path, or specify its location here
    browser = webdriver.Chrome('/home/galmog/chromedriver')
    
    # navigate to page
    browser.get(url)
    
    #fill in form
    Sequence = browser.find_element_by_id('sequence')
    
    Sequence.send_keys(seq)
    
    model = browser.find_element_by_name('model')
    for option in model.find_elements_by_tag_name('option'):
        if option.text == Predictors[predictor][1]:
            option.click()
            
    #submit form
    browser.find_element_by_name('Submit Query').submit()
    
    #object to store url of new loading page
    new_url = browser.current_url
    
    print(new_url)
    
    print('Starting.')
    
    # wait until page loads
    check_if_loaded(browser)
    
    print('Done loading.')
    
    # get window handle of results page
    window_before = browser.window_handles[0]
    
    print(browser.current_url)
    # get all links
    links = browser.find_elements_by_tag_name('a')
    
    # click the one we want
    disorder = links[3] 
    disorder.click()
    
    # get window handle of disorder data page
    window_after = browser.window_handles[1]
    
    # switch browser to new page
    browser.switch_to.window(window_after)
    
    # parse new page
    html = browser.page_source
    
    browser.quit()
    
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
    seq = header + "\n" + "\n" + sequence 
    print(seq)
    
    results = submit_sequence(seq, start_url)

    download_results(results)
    
    time.sleep(60)
      


