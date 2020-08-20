import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from Bio import SeqIO
import math
from threading import Thread

def disprot(sequence):
    start_url = 'http://www.dabi.temple.edu/disprot/predictor.php'
    predictor_names = ['vl2', 'vl3','vl3h','vslb']
    seq_len= len(sequence)
    # dict to map predictor names to their xpath
    predictors = {'vl2': '/html/body/table/tbody/tr[4]/td/form/table/tbody/tr[8]/td[2]/input[1]',
                  'vl3': '/html/body/table/tbody/tr[4]/td/form/table/tbody/tr[8]/td[2]/input[2]',
                  'vl3h': '/html/body/table/tbody/tr[4]/td/form/table/tbody/tr[8]/td[2]/input[3]',
                  'vl3e': '/html/body/table/tbody/tr[4]/td/form/table/tbody/tr[8]/td[2]/input[4]',
                  'vslb': '/html/body/table/tbody/tr[4]/td/form/table/tbody/tr[8]/td[2]/input[5]',
                  'vslp': '/html/body/table/tbody/tr[4]/td/form/table/tbody/tr[8]/td[2]/input[6]'}

    def save_results(html):
        html = html.splitlines() # split by lines into list
        # remove extra things we don't want
        extra = math.ceil(seq_len / 60) + 5
        html = html[extra:]
        # remove extra spaces and store in new list
        results = []
        for i in html:
            new = i.strip()
            new = new.replace('  ', ' ')
            results.append(new)

        for ind, aa in enumerate(results):  # save data
            results[ind] = aa.split(' ')[-1]  # split string and only take wanted value

        return results


    def submit_sequence(sequence, url, predictor_name):
        # create instance of chrome webdriver
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--headless") # run headless chrome
        browser = webdriver.Chrome(options = chrome_options)

        # navigate to page
        browser.get(url)

        # fill in form
        Sequence = browser.find_element_by_name("sequence")
        Sequence.send_keys(sequence)

        # select appropriate predictor
        predictor_xpath = predictors[predictor_name]
        predictor = browser.find_element_by_xpath(predictor_xpath)
        predictor.click()

        # submit form
        browser.find_element_by_xpath("//input[@value='Submit']").submit()

        # wait for page to finish loading
        WebDriverWait(browser, 3600).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/table/tbody/tr[4]/td/blockquote/pre')))
        # click link with disorder data amd parse
        html = browser.find_element_by_xpath("/html/body/table/tbody/tr[4]/td/blockquote/pre").text
        browser.close()
        return html

    disprot_total = []

    for pre in predictor_names:
        submitted_page = submit_sequence(sequence, start_url, pre) # run each disprot predictor separately
        temp_results = save_results(submitted_page)
        disprot_total.append(temp_results)
        # time.sleep(60) # wait before running again

    return disprot_total
