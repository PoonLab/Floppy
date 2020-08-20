from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def pondr(sequence):
    start_url = 'http://www.pondr.com/'
    predictors = ['VLXT', 'XL1', 'CAN', 'VL3', 'VSL2'] # list of all the predictors we want to get data from

    def save_results(data):
        # split into list by lines
        data = data.splitlines()

        # remove header row
        data = data[1:]
        for ind, aa in enumerate(data): # save data
            data[ind] = aa.split(' ')[2:]  # split string and only take wanted value

        return data


    def submit_sequence(sequence, url):
        # create instance of chrome webdriver
        # need to add chromedriver to path, or specify its location here
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--headless")  # run headless chrome
        browser = webdriver.Chrome(options=chrome_options)

        # navigate to page
        browser.get(url)

        # check all checkboxes of predictors we are interested in (all but CDF and charge-hydropathy)
        for i in predictors:
            predictor = browser.find_element_by_name(i)
            if predictor.is_selected() == False:
                predictor.click()

        # fill in sequence
        Sequence = browser.find_element_by_name('Sequence')
        Sequence.send_keys(sequence)

        # click raw output
        browser.find_element_by_name('wcwraw').click()

        # uncheck all output forms we don't want
        checkboxes = ['graphic', 'stats', 'seq']
        for i in checkboxes:
            checkbox = browser.find_element_by_name(i)
            if checkbox.is_selected():
                checkbox.click()

        # submit form
        browser.find_element_by_name('submit_result').click()

        # wait for page to finish loading
        WebDriverWait(browser, 3600).until(EC.presence_of_element_located((By.XPATH, '/html/body/pre[5]')))

        # get disorder data
        data = browser.find_element_by_xpath('/html/body/pre[6]').text

        browser.close()

        return data

    results = submit_sequence(sequence, start_url)

    predictions = save_results(results)

    return predictions
