import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud
from .filters import words


class dataAnalyser:
    """
    Analyzes provided data with the help of `sklearn`.

    Credit: https://towardsdatascience.com/clustering-documents-with-python-97314ad6a78d
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words={'english'})

    def elbow_method(self, X):
        Sum_of_squared_distances = []
        K = range(2,10)
        for k in K:
            km = KMeans(n_clusters=k, max_iter=200, n_init=10)
            km = km.fit(X)
            Sum_of_squared_distances.append(km.inertia_)
        plt.plot(K, Sum_of_squared_distances, 'bx-')
        plt.xlabel('k')
        plt.ylabel('Sum_of_squared_distances')
        plt.title('Elbow Method For Optimal k')
        plt.show()
        return K, Sum_of_squared_distances

    def vectorize(self, data):
        return self.vectorizer.fit_transform(data)

    def cluster(self, X, data):
        true_k = 6
        model = KMeans(n_clusters=true_k, init='k-means++', max_iter=200, n_init=10)
        model.fit(X)
        labels = model.labels_
        wiki_cl = pd.DataFrame(list(zip(words,labels)),columns=['title','cluster'])
        print(wiki_cl.sort_values(by=['cluster']))
        result = {'cluster':labels,'wiki':data}
        result = pd.DataFrame(result)
        for k in range(0,true_k):
            s = result[result.cluster==k]
            text = s['wiki'].str.cat(sep=' ')
            text = text.lower()
            text = ' '.join([word for word in text.split()])
            wordcloud = WordCloud(max_font_size=50, max_words=100, background_color="white").generate(text)
            print('Cluster: {}'.format(k))
            print('Titles')
            titles = wiki_cl[wiki_cl.cluster==k]['title']
            print(titles.to_string(index=False))
            plt.figure()
            plt.imshow(wordcloud, interpolation="bilinear")
            plt.axis("off")
            plt.show()

    def analyse(self, data):
        self.elbow_method(self.vectorize(data))
        self.cluster(self.vectorize(data), data)
