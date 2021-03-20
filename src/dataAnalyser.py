import decimal

import nltk
from nltk.tokenize import RegexpTokenizer, WhitespaceTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from kneed import KneeLocator

from wordcloud import WordCloud
from .filters import words
from .dataCollector import DataCollector
from . import ranges


class DataAnalyser:
    """
    Analyzes provided data with the help of `sklearn`.

    Credit: https://towardsdatascience.com/clustering-documents-with-python-97314ad6a78d
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words={"english"})
        self.stop_words = set(stopwords.words("english"))
        self.lemmatizer = WordNetLemmatizer()
        self.w_tokenizer = WhitespaceTokenizer()
        self.database = DataCollector()

    def lemmatize(self, text):
        return " ".join(
            [
                self.lemmatizer.lemmatize(i)
                for i in self.w_tokenizer.tokenize(text)
                if i.lower() not in self.stop
            ]
        )

    def tokenize(self, text):
        return nltk.word_tokenize(text)

    def vectorize(self, data):
        return self.vectorizer.fit_transform(data)

    def elbow_method(self, data, X=None):
        print(f"Determining number of clusters for {len(data)} tweets..")
        K = range(2, 12)
        X = X if X is not None else self.vectorize(data)
        Sum_of_squared_distances = [
            KMeans(n_clusters=k, max_iter=200, n_init=10).fit(X).inertia_ for k in K
        ]
        kneedle = KneeLocator(K, Sum_of_squared_distances)
        return data, kneedle.elbow, X

    def cluster(self, data, true_k=6, X=None):
        print(f"Creating {true_k} clusters..")
        model = KMeans(n_clusters=true_k, init="k-means++", max_iter=200, n_init=10)
        model.fit(X if X is not None else self.vectorize(data))
        labels = model.labels_
        tweet_cl = pd.DataFrame(list(zip(words, labels)), columns=["title", "cluster"])
        print(tweet_cl.sort_values(by=["cluster"]))
        result = {"cluster": labels, "tweet": data}
        result = pd.DataFrame(result)
        for k in range(0, true_k):
            s = result[result.cluster == k]
            wordcloud = WordCloud().generate(
                " ".join([word for word in s["tweet"].str.cat(sep=" ").lower().split()])
            )
            print(f"Cluster: {k}")
            print("Titles")
            titles = tweet_cl[tweet_cl.cluster == k]["title"]
            print(titles.to_string(index=False))
            plt.figure()
            plt.imshow(wordcloud, interpolation="bilinear")
            plt.axis("off")
            plt.show()

    def analyse(self):
        data = [
            d["text"]
            for d in self.database.get_all()[:]
            if ranges.get_weight("user", **d) > 0.6
            and ranges.get_weight("tweet", **d) >= 0
        ]
        self.cluster(*self.elbow_method(data, self.vectorize(data)))
