from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import re
import queue


def iupred(sequence, queue):
    start_url = 'https://iupred2a.elte.hu/'
    predictors = {'long': 'iupred_long_radio',
                  'short': 'iupred_short_radio'}  # list of all the predictors we want to get data from

    def save_results(data):
        # split into list by lines
        data = data.splitlines()

        # remove header rows
        data = data[5:]
        data = data[:-4]

        for ind,i in enumerate(data):
            data[ind] = re.split('\t', i.strip('\t')) # remove spaces and only take col we want
            data[ind] = data[ind][2]


        return data


    def submit_sequence(sequence, start_url, predictor_name):
        # create instance of chrome webdriver
        # need to add chromedriver to path, or specify its location here
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--headless")  # run headless chrome
        browser = webdriver.Chrome(options=chrome_options)

        # navigate to page
        browser.get(start_url)

        # fill in sequence
        Sequence = browser.find_element_by_name('inp_seq')
        Sequence.send_keys(sequence)

        # select appropriate predictor

        predictor_id = predictors[predictor_name]
        predictor = browser.find_element_by_id(predictor_id)
        # predictor= browser.find_element_by_css_selector("input[type='radio'][value={predictor}]".format(predictor= predictor_name))
        browser.execute_script("arguments[0].click();", predictor)
        # predictor.click()

        # submit form
        browser.find_element_by_xpath('//*[@id="page-content-wrapper"]/div/div[2]/div[2]/form/div[6]/button').click()
        window_before = browser.window_handles[0]

        # wait for page to finish loading
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="plot"]')))

        # click link with disorder data amd parse
        data = browser.find_element_by_xpath('//*[@id="dropdownMenuButton"]').click()
        WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, '// *[ @ id = "page-content-wrapper"] / div / div[1] / div[1] / div / div[2] / div / a[1] / button'))) # wait for menu to open

        browser.find_element_by_xpath('// *[ @ id = "page-content-wrapper"] / div / div[1] / div[1] / div / div[2] / div / a[1] / button').click()
        window_after = browser.window_handles[1]  # get window handle of disorder data page

        browser.switch_to.window(window_after)  # switch browser to new page
        html = browser.page_source  # parse new page

        browser.close()

        return html

    iupred_total = []

    for pre in predictors:
        submitted_page = submit_sequence(sequence, start_url, pre) # run each predictor separately
        temp_results = save_results(submitted_page)
        iupred_total.append(temp_results)
        # time.sleep(60) # wait before running again

    queue.put(iupred_total)
    return iupred_total

