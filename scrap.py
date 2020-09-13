import pandas as pd
from urllib.request import urlopen, Request
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from pprint import pprint
import re
import csv

#chromedriver = "/usr/local/bin/chromedriver"
#os.environ["webdriver.chrome.driver"] = chromedriver
#browser = webdriver.Chrome(executable_path=chromedriver)
'''
firefox_profile = webdriver.FirefoxProfile()
firefox_profile.set_preference('permissions.default.image', 2)
firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

browser = webdriver.Firefox(firefox_profile=firefox_profile)
session_url = browser.command_executor._url      
session_id = browser.session_id 
'''
prefix = {"y":1e-24, "z":1e-21, "a":1e-18, "f":1e-15, "p": 1e-12,
          "n":1e-9, "u":1e-6, "µ":1e-6, "m":1e-3, "c":1e-2, "d":0.1,
          "h":100, "k":1000, "M":1e6, "G":1e9, "T":1e12, "P":1e15,
          "E":1e18, "Z":1e21, "Y":1e14}

def meter(s):
    try:
        # multiply with meter-prefix value
        if len(s) >= 2:
            return float(s[:-1])*prefix[s[-1]]
    except KeyError:
        # no or unknown meter-prefix
        return float(s)

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

def scrap_page( filename = './csv/hr_unfitered.csv'):
    '''
    Scraps the webpage and picks the questions under the given topic
    Outpus a CSV file with 
    [question_id, question_link, question, no_ans, no_follows]
    '''
    '''
    browser = create_driver_session(session_id, session_url)
    browser.session_id = session_id
    browser.get(url)
    html = browser.page_source'''

    html = open('./top.html')
    soup = BeautifulSoup(html, 'lxml')

    # Print out the text
    sections = soup.findAll("div", {"class": "feed_content"})
    with open(filename,'a', encoding='utf8') as file:
        #pprint (len(sections))
        for section in sections:
            #pprint (section)
            questions = section.find("div", { "class": "pass_color_to_child_links"})
            answer = section.findAll("a", {"class" : "answer_count_prominent"})
            follow = section.findAll("span", {"class": "ui_button_count_inner"}  )
            #print (questions)

            #question_div = questions.find("div",{"class": "pass_color_to_child_links"})
            question_div = questions.findChildren("div")    
            question_id = question_div[0]["id"]
            question_link = question_div[0].find("a", {"class": "question_link"})
            question = question_div[0].find("span", {"class": "ui_qtext_rendered_qtext"})
            
            no_answers = re.findall('\d+',answer[0].get_text())
            no_follows = meter(follow[0].get_text())
            
            try:
                a = int(no_answers[0])
            except:
                a = 0
            
            try:
                no_follows = int(no_follows)
            except:
                no_follows = 0
            
            '''
            print ('###############################################################')
            pprint (str(question_id))
            pprint (question_link['href'])
            pprint (question.text)
            if len(no_answers) >=10:
                pprint (int(no_answers))
            else:
                pprint (0)
            pprint (no_follows)
            '''
            csv_row = [question_id.strip(),question_link['href'],question.text,a,no_follows]
            writer = csv.writer(file)
            writer.writerow(csv_row)

def fetch_topic_url(topic = 'HR-Interview-Questions', top_question = True):

    '''
    Input : Topic name - to parse from Quora site
    Output: Url_link - Returns topic page
            url_top_link - returns top questions page in topic
    '''
    html_prefix = 'https://www.quora.com/topic/'

    if top_question is True:
        question = '/top_questions'
    else:
        question = '/all_questions'

    url_top_link = str(html_prefix+topic+question)
    url_link = str(html_prefix+topic)
    return url_link, url_top_link

def fetch_related_topics(url_link):
    related_topic = []
    url_prefix = 'https://www.quora.com'
    browser.get(url_link)
    html = browser.page_source
    soup = BeautifulSoup(html, 'lxml') 
    topics = soup.find_all('a', {'class':'HoverMenu RelatedTopicsListItem'}, href = True)
    for link in topics:
        related_topic.append(str(url_prefix + link['href']))
    return related_topic
    
if __name__ == '__main__':
    #url_link, url_top_link = fetch_topic_url()

    #related_topic = fetch_related_topics(url_link)
    #print(url_top_link)

    scrap_page()
    #browser.quit()