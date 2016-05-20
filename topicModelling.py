import mysql.connector
import re
import time
import gensim
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from gensim import corpora, models
from html.parser import HTMLParser

start_time = time.time()
stop_words = set(stopwords.words('spanish'))
stemmer = SnowballStemmer('spanish')
texts = []

class HTMLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, data):
        self.fed.append(data)
    def get_data(self):
        return ''.join(self.fed)

def getPosts():
    """ To fetch posts from database """
    connection = mysql.connector.connect(user='sql', password='', host='localhost', database='posts')
    cursor = connection.cursor()
    cursor.execute("""
        SELECT   id, LOWER(post_content_filtered)
        FROM     wp_posts 
        WHERE    post_status = 'publish'
        AND      post_type = 'normal'
        ORDER BY Id DESC LIMIT 1
        """)
    posts = cursor.fetchall()
    cursor.close()
    return posts

def filterPostContent(data):
    """ To remove tags,multispaces and store simple string of data """
    stripTags = HTMLStripper()
    stripTags.feed(data)
    data = stripTags.get_data()
    data = re.sub('[^\s0-9A-Za-zÀ-ÿ]', ' ', data)
    data = data.split()
    stopped_data = [i for i in data if not i in stop_words]
    stemmed_data = [stemmer.stem(i) for i in stopped_data]
    return stemmed_data

if __name__ == '__main__':
    posts = getPosts()

    for post in posts:
        postContent = filterPostContent(post[1])
        texts.append(postContent)

    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics = 4, id2word = dictionary, passes=20)
    print(ldamodel.print_topics(num_topics = 4, num_words = 3))
    for i in range(0, ldamodel.num_topics-1):
     	print(ldamodel.print_topic(i))
    print(ldamodel.print_topics())
    print("TIME taken")
    print(time.time() - start_time)