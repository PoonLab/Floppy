# -*- coding: utf-8 -*-
import sys
import requests
import re
import time
import csv
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime 
from Bio import SeqIO
import math

"""
Need to download Selenium package and a driver interface with browser of choice.
See: https://selenium-python.readthedocs.io/installation.html 
"""

#protein disorder software url
start_url = 'http://www.dabi.temple.edu/disprot/predictor.php'

predictor_name = 'vl3'

# dict to map predictor names to their xpath
predictors = {'vl2': '/html/body/table/tbody/tr[4]/td/form/table/tbody/tr[8]/td[2]/input[1]', 'vl3': '/html/body/table/tbody/tr[4]/td/form/table/tbody/tr[8]/td[2]/input[2]', 'vl3h':'/html/body/table/tbody/tr[4]/td/form/table/tbody/tr[8]/td[2]/input[3]', 'vl3e':'/html/body/table/tbody/tr[4]/td/form/table/tbody/tr[8]/td[2]/input[4]', 'vslb':'/html/body/table/tbody/tr[4]/td/form/table/tbody/tr[8]/td[2]/input[5]', 'vslp':'/html/body/table/tbody/tr[4]/td/form/table/tbody/tr[8]/td[2]/input[6]'}

## check if sequence from cmd line is in correct format
#if seq.startswith('>') == False:
#    print(seq + ' does not seem to be a valid protein sequence')
#    sys.exit()

def download_results(html):
    
    # split by lines into list
    html = html.splitlines()
    
    # remove extra things we don't want
    extra = math.ceil(Length / 60) + 5
    html = html[extra:]
    
    # remove extra spaces and store in new list
    results = []
    for i in html:
        new = i.strip()
        new = new.replace('  ', ' ')
        results.append(new)

    # create consistent file name    
    file_name = ID + '-Disprot-' + predictor_name
    path = '/home/galmog/Documents/Disorder/Disorder_Data/Disprot/vl3/'
    
    # output to csv
    with open(path + file_name + '.csv', 'w') as f:
        # create consistent output header line
        f.write(ID + ',' + datetime.today().strftime('%Y-%m-%d') + ',' + 'Disprot-' + predictor_name  + '\n')
        wr = csv.writer(f)
        for val in results:
#            wr.writerow(val.split(' ')[:-1]) 
            wr.writerow(val.split(' ')[:-1])
        
def submit_sequence(sequence, url):
    # create instance of chrome webdriver
    # need to add firefoxdriver to path, or specify its location here
    browser = webdriver.Chrome(executable_path='/home/galmog/chromedriver')

    # navigate to page
    browser.get(url)

    # fill in form
    Sequence = browser.find_element_by_name("sequence")
    Sequence.send_keys(seq)
    
    # select appropriate predictor 
    predictor_xpath = predictors[predictor_name]
    predictor = browser.find_element_by_xpath(predictor_xpath)
    predictor.click()
    
    # submit form
    browser.find_element_by_xpath("//input[@value='Submit']").submit()

    # wait for page to finish loading
    WebDriverWait(browser, 3600).until(EC.presence_of_element_located((By.XPATH, '/html/body/table/tbody/tr[4]/td/blockquote/pre')))
    
    # click link with disorder data
    # parse
    html = browser.find_element_by_xpath("/html/body/table/tbody/tr[4]/td/blockquote/pre").text
    
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

    seq = sequence + "\n"
    print(seq)
    Length = len(seq)
    submitted_page = submit_sequence(seq, start_url)

    download_results(submitted_page)
    
    time.sleep(30)


