import glob
from pprint import pprint
from summa import summarizer
from summa import keywords
from gensim import summarization
import re

files = glob.glob('./data/answers/*.txt')
i=0

def clean(text):
    clean_text = []
    text_ = []
    
    text = re.sub('https?:\/\/.*[\r\n]*', '', text, flags=re.MULTILINE)
    text = re.sub('http?:\/\/.*[\r\n]*', '', text, flags=re.MULTILINE)
    for line in text:
        if line.strip():
            text_.append(line)
    for line in text_:
        if line.strip(':**'):
            clean_text.append(line)
    return clean_text

filecount = 1
file_name = []
skipped_ans = []
for file in files:
    text = ''
    with open(file,'r') as textfile:
        text = textfile.read()

    with open(file, 'w') as textfile:
        print ("{}. Writing file: ".format(filecount), file)
        #text = summarization.summarize(text, word_count= 500)
        text = text.strip("""[

        **Short answer:** Yes, there is an API marketplace called
        [RapidAPI](http://rapidapi.com/?utm_campaign=Quora&utm_medium=link_Marketplace&utm_source=Quora),
        which combines both RapidAPI and the Mashape API Marketplace into the world’s
        largest API marketplace! ** _[disclaimer: I work for RapidAPI]_**

        

        **Long answer:** Yes, you should check out the
        [RapidAPI](http://rapidapi.com/?utm_campaign=Quora&utm_medium=link_Marketplace&utm_source=Quora).
        RapidAPI is an online API marketpl...

        ]
        """)
        for _ in "#<>**()[]":
            text = text.strip(_)
        text = re.sub(r'^https?:\/\/.*[\r\n]*', '', str(text), flags=re.MULTILINE)

        try:
            textfile.write(summarizer.summarize(text, words=200))
            #textfile.write (summarization.keywords(text, lemmatize=True, words=15, deacc=True))
        except:
            skipped_ans.append(file)
            pass
        filecount+=1
