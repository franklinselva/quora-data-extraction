import csv
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from pprint import pprint
from html2text import html2text
from time import sleep
import os

question_id = []
question_link = []
question  = []
answer_count = []
answers = []
skipped_ans = []

#chromedriver = "/usr/local/bin/chromedriver"
#os.environ["webdriver.chrome.driver"] = chromedriver
#browser = webdriver.Chrome(executable_path=chromedriver)

firefox_profile = webdriver.FirefoxProfile()
firefox_profile.set_preference('permissions.default.image', 2)
firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

browser = webdriver.Firefox(firefox_profile=firefox_profile)
session_url = browser.command_executor._url      
session_id = browser.session_id 

def create_driver_session(session_id, executor_url):
    from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver

    # Save the original function, so we can revert our patch
    org_command_execute = RemoteWebDriver.execute

    def new_command_execute(self, command, params=None):
        if command == "newSession":
            # Mock the response
            return {'success': 0, 'value': None, 'sessionId': session_id}
        else:
            return org_command_execute(self, command, params)

    # Patch the function before creating the driver object
    RemoteWebDriver.execute = new_command_execute

    new_driver = webdriver.Remote(command_executor=executor_url, desired_capabilities={})
    new_driver.session_id = session_id

    # Replace the patched function with original function
    RemoteWebDriver.execute = org_command_execute

    return new_driver

def load_csv(filename = './csv/QuoraData_filtered.csv'):
    if (os.path.isfile(filename)):
        first_line = True
        with open(filename) as file:
            reader = csv.reader(file)
            for row in reader:
                if first_line:
                    first_line = False
                    continue
                question_id.append(row[0])
                question_link.append(row[1])
                question.append(row[2])
                answer_count.append(row[3])
        return question_id, question_link, question
    else:
        print ('Specified filepath not found')


def fetch_ans (question_links, n=25):
    '''
    Input: question links in lists
    output: answers as list of lists
    '''

    path = "./data/answers"
    for i in range(0,len(question_id)-1):
        num = i+1
        directory ='{}/{}.txt'.format(path, question_id[i])
        if os.path.isfile(directory): continue
        browser = create_driver_session(session_id, session_url)
        browser.session_id = session_id
        url = question_links[i]
        browser.get(url)
        elm = browser.find_element_by_tag_name('html')
        elm.send_keys(Keys.END)
        
        html = ''
        while True:
                html = browser.page_source
                if html is None or os.path.isfile(directory):
                    print ("Skipping question id {} ".format(question_id[i]))
                    skipped_ans.append(question_id)
                    break
                soup = BeautifulSoup(html, 'lxml')
                user = soup.find_all('a', {'class': 'user'})
                ans_part = soup.find_all('div', {'class': 'ui_qtext_truncated_text'})
                ans_part = ans_part + soup.find_all('div', {'class': 'ui_qtext_expanded'})
                #pprint (ans_part)
                #print (int(answer_count[i]))
                try:
                    browser.findElement(By.linkText("(more)")).click()
                except:
                    pass
                if len(ans_part) >= int(answer_count[i]):#len(user)>=n or 
                    elm.send_keys(Keys.HOME)
                    print ("Writing Question no. {} for id {} to path {}".format(num, question_id[i], directory))
                    with open(directory, 'a') as file:
                        for j in range(0,len(ans_part)-1):
                                #if ans_part[j].find_all('p'):
                                ans = ans_part[j].findChildren('span', {'class': 'ui_qtext_rendered_qtext'})
                                #ans = ans_part[j]
                                file.write(html2text(str(ans)))
                                file.write ('\n##########\n')

                    break
                else:
                    elm.send_keys(Keys.END)
                    try:
                        view_more = '//*[@id="__w2_wDKb73t42_more"]/div'
                        load = browser.find_element_by_xpath(view_more)
                        load.click()
                        browser.findElement(By.linkText("View more")).click()                        
                    except:
                        pass
    if len(skipped_ans):    print ("Skipped questions", skipped_ans)
    else: print ("Successfully completed writing")
    print ('Skipped Questions : ', skipped_ans)

def fetch_html (question_links, n=25):
    '''
    Input: question links in lists
    output: saves webpages in html format
    '''

    path = "./data/html_ans"
    num = 0
    for i in range(0,len(question_links)-1):  
        browser = create_driver_session(session_id, session_url)
        browser.session_id = session_id
        url = question_links[i]
        browser.get(url)
        elm = browser.find_element_by_tag_name('html')
        elm.send_keys(Keys.END)
        num+=1
        directory ='{}/{}.html'.format(path, question_id[i])
        html = ''
        with open (directory, 'w+') as file:
            while True:
                html = browser.page_source
                if html is None or os.path.isfile(directory):
                    print ("Skipping question id {} ".format(question_id[i]))
                    skipped_ans.append(question_id)
                    break
                soup = BeautifulSoup(html)
                user = soup.find_all('a', {'class': 'user'})
                if len(user) >= int(answer_count[i]):#len(user)>=n or 
                    elm.send_keys(Keys.HOME)
                    print ("Writing HTML no. {} for id {} to path {}".format(num, question_id[i], directory))
                    file.write(browser.page_source)
                    break
                else:
                    elm.send_keys(Keys.END)
                    try:
                        view_more = '//*[@id="__w2_wDKb73t42_more"]/div'
                        load = browser.find_element_by_xpath(view_more)
                        load.click()
                        browser.findElement(By.linkText("View more")).click()
                    except:
                        pass
                    
    if len(skipped_ans):    print ("Skipped questions", skipped_ans)
    else: print ("Successfully completed writing")

if __name__ == '__main__':
    ids, link, question = load_csv(filename='./csv/hr_filtered.csv')
    fetch_ans(question_links=link,n=3)
    browser.quit()