# model_train.py -- tiny demo model (for hackathon prototype)
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Small synthetic dataset (demo only). Use real datasets for production!
data = [
    ("https://www.google.com", 1),
    ("https://www.wikipedia.org", 1),
    ("https://www.microsoft.com", 1),
    ("https://example.com", 1),
    ("https://www.openai.com/research", 1),
    ("https://github.com/login", 1),
    ("https://secure-login.example.com/verify", 0),
    ("http://198.51.100.23/secure-login-verify/confirm-token-аб3", 0),
    ("https://example.com/secure-payment/confirm-order?token=abc123", 0),
    ("https://exаmple.com/login", 0),
    ("https://bit.ly.fake-example.example.com/abc", 0),
    ("https://example.com/reset-password/verify-login", 0),
]

X = [u for u,_ in data]
y = [lab for _,lab in data]

vec = TfidfVectorizer(analyzer='char', ngram_range=(3,5))
Xv = vec.fit_transform(X)

clf = LogisticRegression(max_iter=1000)
clf.fit(Xv, y)

joblib.dump(clf, "model.pkl")
joblib.dump(vec, "vectorizer.pkl")
print("Saved model.pkl and vectorizer.pkl")
