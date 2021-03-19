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

from wordcloud import WordCloud
from .filters import words
from .dataCollector import DataCollector


class DataAnalyser:
    """
    Analyzes provided data with the help of `sklearn`.

    Credit: https://towardsdatascience.com/clustering-documents-with-python-97314ad6a78d
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words={"english"})
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.w_tokenizer = WhitespaceTokenizer()
        self.database = DataCollector()

        self.follow_ranges = {
            range(1): 0,
            range(1, 50): 0.5,
            range(50, 5000): 1.0,
            range(5000, 10000): 1.5,
            range(10000, 100000): 2.0,
            range(100000, 200000): 2.5,
        }

        self.age_ranges = {
            range(1): 0,
            range(1, 182): 0.5,
            range(182, 365): 1.0,
            range(365, 547): 1.5,
        }

        self.quote_ranges = {
            range(1): 0,
            range(1, 50): 0.5,
            range(50, 500): 1.0,
            range(500, 1000): 1.5,
        }

        self.reply_ranges = {
            range(1): 0,
            range(1, 5): 0.5,
            range(5, 15): 1.0,
            range(15, 30): 1.5,
        }

        self.retweet_ranges = {
            range(1): 0,
            range(1, 50): 0.5,
            range(50, 500): 1.0,
            range(500, 1000): 1.5,
            range(1000, 10000): 2.0,
            range(10000, 20000): 2.5,
        }

        self.favorite_ranges = {
            range(1): 0,
            range(1, 5): 0.5,
            range(5, 15): 1.0,
            range(15, 30): 1.5,
        }

    def elbow_method(self, X):
        Sum_of_squared_distances = []
        K = range(2, 10)
        for k in K:
            km = KMeans(n_clusters=k, max_iter=200, n_init=10)
            km = km.fit(X)
            Sum_of_squared_distances.append(km.inertia_)
        plt.plot(K, Sum_of_squared_distances, "bx-")
        plt.xlabel("k")
        plt.ylabel("Sum_of_squared_distances")
        plt.title("Elbow Method For Optimal k")
        plt.show()
        return K, Sum_of_squared_distances

    def vectorize(self, data):
        return self.vectorizer.fit_transform(data)

    def lemmatize(self, text):
        return " ".join([
            self.lemmatizer.lemmatize(i)
            for i in self.w_tokenizer.tokenize(text)
            if i.lower() not in self.stop
        ])

    def get_weight(self, weight_type, **kwargs):
        return (sum((
            (1.0 if kwargs.get("description") else 0),
            (1.0 if kwargs.get("verified") else 0),
            (
                (sum(self.follow_ranges[k] for k in self.follow_ranges if kwargs.get("followers") in k) / 3)
                if kwargs.get("followers") in range(200000)# and not print(kwargs.get("followers"))
                else 1.0
            ),
            (
                (sum(self.age_ranges[k] for k in self.age_ranges if kwargs.get("account_age") in k) / 3)
                if kwargs.get("account_age") in range(547)# and not print(kwargs.get("account_age"))
                else 1.0
            ),
            (
                (0.5 if not kwargs["defaults"][0] else 0) + (0.5 if not kwargs["defaults"][1] else 0)
                if kwargs.get("defaults") and len(kwargs.get("defaults")) == 2# and not print(kwargs.get("defaults"))
                else 0
            ),
        )) / 5) if weight_type == 'user' else (sum((
            (
                (sum(self.quote_ranges[k] for k in self.quote_ranges if kwargs.get("quotes") in k) / 2)
                if kwargs.get("quotes") in range(1000)
                else 1.0
            ),
            (
                (sum(self.reply_ranges[k] for k in self.reply_ranges if kwargs.get("replies") in k) / 2)
                if kwargs.get("replies") in range(30)
                else 1.0
            ),
            (
                (sum(self.retweet_ranges[k] for k in self.retweet_ranges if kwargs.get("retweets") in k) / 3)
                if kwargs.get("retweets") in range(20000)
                else 1.0
            ),
            (
                (sum(self.favorite_ranges[k] for k in self.favorite_ranges if kwargs.get("favorites") in k) / 2)
                if kwargs.get("favorites") in range(30)
                else 1.0
            ),
        )) / 4)

    def cluster(self, X, data):
        true_k = 6
        model = KMeans(n_clusters=true_k, init="k-means++", max_iter=200, n_init=10)
        model.fit(X)
        labels = model.labels_
        tweet_cl = pd.DataFrame(list(zip(words, labels)), columns=["title", "cluster"])
        print(tweet_cl.sort_values(by=["cluster"]))
        result = {"cluster": labels, "tweet": data}
        result = pd.DataFrame(result)
        for k in range(0, true_k):
            s = result[result.cluster == k]
            text = s["tweet"].str.cat(sep=" ")
            text = text.lower()
            text = " ".join([word for word in text.split()])
            wordcloud = WordCloud(
                max_font_size=50, max_words=100, background_color="white"
            ).generate(text)
            print("Cluster: {}".format(k))
            print("Titles")
            titles = tweet_cl[tweet_cl.cluster == k]["title"]
            print(titles.to_string(index=False))
            plt.figure()
            plt.imshow(wordcloud, interpolation="bilinear")
            plt.axis("off")
            plt.show()

    def tokenize(self, text):
        return nltk.word_tokenize(text)

    def analyse(self):
        data = [d for d in self.database.get_all() if self.get_weight("user", **d) > 0.6 and self.get_weight("tweet", **d) >= 0]
        self.elbow_method(self.vectorize(data))
        self.cluster(self.vectorize(data), data)
