# Jalankan secara terpisah!!


from textblob import TextBlob
import matplotlib.pyplot as plt
import pandas as pd
import tweepy
import re

# Text Cleansing Function
def my_preprocessor(mytext):
    #Convert to lower case
    mytext = mytext.lower()
    #Convert www.* or https?://* to URL
    mytext = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','URL',mytext) 
    #Convert @username to AT_USER
    mytext = re.sub('@[^\s]+','AT_USER',mytext)
    #Remove additional white spaces
    mytext = re.sub('[\s]+', ' ', mytext)
    #Replace #word with word
    mytext = re.sub(r'#([^\s]+)', r'\1',mytext)
    #trim
    mytext = mytext.strip('\'"')
    return mytext

#Polarity marker
def polarity_check(x):
    if x > 0:
        return "Positif"
    elif x < 0:
        return "Negatif"
    else:
        return "Netral"


#Crawling
consumer_key = "****"
consumer_secret = "****"
access_token = "****"
access_token_secret = "****"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)

tweetan=[]
tanggal=[]
teks=[]
Id=[]
sn=[]
source=[]
rtc=[]

for tweet in tweepy.Cursor(api.search, q = ["jokowi","corona"],
                           count = 200,
                           lang = "id").items():
    if not tweet : 
        print('tweet habis')
        break
    if (not tweet.retweeted) and ('RT @' not in tweet.text):
        print(tweet.created_at, tweet.text)
        tweetan.append(tweet)
        tanggal.append(tweet.created_at) 
        teks.append(tweet.text)
        Id.append(tweet.id)
        sn.append(tweet.user.screen_name)
        source.append(tweet.source)
        rtc.append(tweet.retweet_count)

data = pd.DataFrame()
data['Tanggal'] = tanggal
data['Tweets'] = teks
data['ID'] = Id
data['Screen Name'] = sn
data['Banyak Retweet'] = rtc
data['Source'] = source


#Analisis Sentimen
file = data['Tweets'].tolist()
   
tweets = []
polarity = []
subjectivity = []
pos_polarity = 0
neu_polarity = 0
neg_polarity = 0

for tweet in file:
    cleaned = my_preprocessor(tweet)
    analysis = TextBlob(cleaned)
    an = analysis.translate(to='en')
    if an.polarity > 0:
        pos_polarity += 1
    elif an.polarity < 0:
        neg_polarity += 1
    else:
        neu_polarity += 1
    tweets.append(cleaned)
    polarity.append(an.polarity)
    subjectivity.append(an.subjectivity)

avg_pos_polarity = pos_polarity/len(file)
avg_neg_polarity = neg_polarity/len(file)
avg_neu_polarity = neu_polarity/len(file)

jokowi = pd.DataFrame()
jokowi['Tweet'] = tweets
jokowi['Polarity'] = polarity
jokowi['Subjectivity'] = subjectivity
jokowi['Sentiment'] = jokowi.apply(lambda x:
    polarity_check(x['Polarity']), axis = 1)

jokowi.to_csv('jokowi.csv',index=False)


#Visualisasi
pos = jokowi.loc[jokowi['Sentiment'] == "Positif"].count()[0]
neg = jokowi.loc[jokowi['Sentiment'] == "Negatif"].count()[0]
neu = jokowi.loc[jokowi['Sentiment'] == "Netral"].count()[0]

labels = ['Positif','Negatif','Netral']
explode = (0,0.1,0)
colors = ("#5252fa","#eb4034","#27e33d")
          
plt.pie([pos,neg,neu], explode = explode,colors = colors, 
        labels = labels, autopct = "%1.1f %%",
        shadow = True, startangle=90)
plt.axis('equal')
plt.title("Analisis Sentimen Terhadap Jokowi")
plt.legend()
plt.savefig('Jokowi.png', dpi = 100)
plt.show()