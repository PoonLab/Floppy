import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def cspritz(sequence):
    start_url = 'http://protein.bio.unipd.it/cspritz/'
    # list mapping prediction options (for scraper) to what to put in the file name
    predictors_t = [['Short', 'X-Ray (short)'], ['long', 'Disprot (long)']]

    def save_results(results):
        data = []
        results = results.splitlines()
        results[0] = results[0][84:]
        results = results[:-1]
        for i in results:
            new = i[2:]
            data.append(new)

        for ind, aa in enumerate(data):
            data[ind] = aa.split(' ')  # split string and only take wanted value
        return data

    def check_if_loaded(browser):
        """
        Function to ensure the page has finished running before extracting the results.
        """
        # waits 1 hour before giving Timeout error
        # searches for notice element in the new page to know it has changed
        WebDriverWait(browser, 3600).until(EC.presence_of_element_located((By.ID, 'notice')))

    def submit_sequence(sequence, url, predictor):
        # create instance of chrome webdriver
        # need to add chromedriver to path, or specify its location here
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--headless")  # run headless chrome
        browser = webdriver.Chrome(options=chrome_options)

        browser.get(url)
        # fill in form
        Sequence = browser.find_element_by_id('sequence')
        Sequence.send_keys(sequence)
        model = browser.find_element_by_name('model')
        for option in model.find_elements_by_tag_name('option'):
            if option.text == predictors_t[predictor][1]:
                option.click()
        # submit form
        browser.find_element_by_name('Submit Query').submit()
        # object to store url of new loading page
        new_url = browser.current_url
        # print(new_url)
        # print('Starting.')
        check_if_loaded(browser) # wait until page loads
        # print('Done loading.')
        window_before = browser.window_handles[0] # get window handle of results page

        # print(browser.current_url)
        links = browser.find_elements_by_tag_name('a') # get all links
        disorder = links[6]
        disorder.click()
        window_after = browser.window_handles[1] # get window handle of disorder data page
        browser.switch_to.window(window_after) # switch browser to new page
        html = browser.page_source # parse new page
        browser.quit()
        return html

    predictors=[0,1]
    cspritz_total = []
    # 0 for short, 1 for long
    for pre in predictors:
        results = submit_sequence(sequence, start_url, pre) # run each predictor separately
        temp_results = save_results(results)
        cspritz_total.append(temp_results)
        # time.sleep(60) # wait before running again

    return cspritz_total