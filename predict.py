import pickle
from sklearn.feature_extraction.text import TfidfVectorizer

filename = 'finalized_model.sav'
vectorizer = TfidfVectorizer(stop_words='english')

loaded_model = pickle.load(open(filename, 'rb'))

print("prediction")
X = vectorizer.transform(["How do you sell this water bottle marketing interview question?"])
predicted = loaded_model.predict(X)
print(predicted)
