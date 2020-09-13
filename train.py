import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cluster import KMeans
from nltk.corpus import stopwords 
from nltk.stem.wordnet import WordNetLemmatizer
import string
import re
import numpy as np
from collections import Counter
import pickle

stop = set(stopwords.words('english'))
exclude = set(string.punctuation) 
lemma = WordNetLemmatizer()

# Cleaning the text sentences so that punctuation marks, stop words & digits are removed  
def clean(doc):
    stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
    punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
    normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
    processed = re.sub(r"\d+","",normalized)
    y = processed.split()
    return y


#Data preprocessing
question_id = []
question = []
data = []
cleaned = []
transform_cleaned = []

with open('./csv/QuoraData_filtered.csv') as file:
    reader = csv.reader(file)
    for row in reader:
        question_id.append(row[0])
        question.append(row[2])
        #data.append()

for i in range(0,len(question)):
    line = question[i].strip()
    cleaned = clean(line)
    cleaned = ' '.join(cleaned)
    #data.append(cleaned)
    transform_cleaned.append(cleaned)
    data.append([question_id[i], cleaned])

stopwords = stopwords.words('english')
newStopWords = ['aadhaar','ok', 'lottery', 'pune', 'samsung', 'hyundai', 'isro', 'kolkatta', \
    'deloitte', 'infotech', 'cisco', 'wipro', 'upsc', 'ongc', 'google', 'amazon', 'barclays', \
        'flipkart', 'ibm', 'bookmyshow', 'zoho', 'microsoft', 'bangalore', 'linkedin', 'icici', \
            'makemytrip', 'bengaluru', 'walmart', 'cognizant', 'indigo', 'drdo', 'appbank', 'facebook', \
                'mumbai', 'etc']
stopwords.extend(newStopWords)


vectorizer = TfidfVectorizer(min_df=2, max_df=0.5 ,ngram_range=(1,3), stop_words=stopwords)
X = vectorizer.fit_transform(transform_cleaned)

true_k = 2
model = KMeans(n_clusters=true_k, init='k-means++', max_iter=100, n_init=10, verbose=0)
model.fit(X)

filename = 'finalized_model.sav'
pickle.dump(model, open(filename, 'wb'))

order_centroids = model.cluster_centers_.argsort()[:, ::-1]
terms = vectorizer.get_feature_names()


for i in range(true_k):
    print("Cluster %d:" % i)
    for ind in order_centroids[i, :]:
        print("%s" % terms[ind])


print("Creating the file with added category")

#Resetting
question_id = []
question = []
data = []
cleaned = []
transform_cleaned = []

with open('./csv/QuoraData_filtered.csv') as file:
    reader = csv.reader(file)
    for row in reader:
        question_id.append(row[0])
        question.append(row[2])
        #data.append()

for i in range(0,len(question)):
    line = question[i].strip()
    cleaned = clean(line)
    cleaned = ' '.join(cleaned)
    #data.append(cleaned)
    transform_cleaned.append(cleaned)
    data.append([question_id[i], cleaned])

with open('./csv/QuoraData_categorized.csv','a') as file:
    for i in range(0,len(question)-1):
        X = vectorizer.transform([question[i]])
        predicted = model.predict(X)
        category = ''
        if predicted:
            category = 'experience'
        else:
            category = 'interview'
        writer = csv.writer(file)
        writer.writerow([question_id[i],question[i],category])
