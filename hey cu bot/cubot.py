from flask import Flask, redirect, url_for, request,render_template
from flask import Flask, render_template, request
import nltk
import warnings
import sqlite3
import numpy as np
import random
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up","hey",)
GREETING_RESPONSES = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]

f=open('cu_chatbot_data.txt','r',errors = 'ignore')
raw=f.read()
raw=raw.lower()
sent_tokens = nltk.sent_tokenize(raw)
lemmer = nltk.stem.WordNetLemmatizer()
def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]

remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)

def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))


def greeting(sentence):
    """If user's input is a greeting, return a greeting response"""
    global GREETING_INPUTS
    global GREETING_RESPONSES
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)


def response(user_response):
    robo_response=''
    
    #sent_tokens.append(user_response)
    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
    tfidf = TfidfVec.fit_transform(sent_tokens)
    u = TfidfVec.transform([user_response])
    #print(TfidfVec.get_feature_names())
    vals = cosine_similarity(u, tfidf)
    #print(vals.argsort()[0])
    idx=vals.argsort()[0][-1]
    #print(idx)
    flat = vals.flatten()
    flat.sort()
    #print(flat)
    req_tfidf = flat[-1]
    if(req_tfidf==0):
        robo_response=robo_response+"I am sorry! I don't understand you"
        return robo_response
    else:
        robo_response = robo_response+sent_tokens[idx]
        return robo_response


app = Flask(__name__)

@app.route('/')
def home():
   return render_template('index.html')

@app.route('/qus',methods = ['POST', 'GET'])
def qus():
    if request.method == 'POST':
        qustion = request.form['qus']
                 
        if greeting(qustion) != None:
            return render_template('index.html',rows = greeting(qustion))

        if qustion in ['bye','exit','goodbye','thanks','thankyou','thank']:
            return render_template('end.html')
        qus = qustion.lower().translate(remove_punct_dict)
        con = sqlite3.connect("hey_cu.db")
        #con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT answers FROM cu WHERE qustions  LIKE  '%{}%'".format(qustion))
        rows = cur.fetchone();
        if rows != None:
            return render_template('index.html',rows = ''.join(rows))
        else:
            return render_template('index.html',rows = response(qus))
            
            
    else:
      
      return render_template("index.html")
