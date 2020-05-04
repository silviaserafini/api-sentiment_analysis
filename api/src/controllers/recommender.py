import nltk
import ast
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import requests
from sklearn.metrics.pairwise import cosine_similarity as distance
from src.app import app
from pymongo import MongoClient
from src.helpers.errorHandler import errorHandler ,Error404 ,APIError
from src.config import DBURL
from bson.json_util import dumps
from bson import ObjectId
from src.controllers.chats import *
import json


#DBURL='mongodb://192.168.1.73:27017/'
client = MongoClient(DBURL)
print(f"Connected to {DBURL}")
db = client.get_database("dbChat")

nltk.download("vader_lexicon")
sia = SentimentIntensityAnalyzer()

'''- (GET) `/user/<user_id>/recommend`
  - **Purpose:** Recommend friend to this user based on chat contents
  - **Returns:** json array with top 3 similar users'''

@app.route("/user/<user_id>/recommend") 
@errorHandler
def getSimilarUsers(user_id):
    #get all the chats ids
    #r = requests.get(f'http://localhost:3500//chat/ids')
    r=ast.literal_eval(getChatIds())
    chat_ids=list(r.keys())
    
    #get all the messages texts for all the chats
    messages1={}#
    for chat_id in chat_ids:
        #r = requests.get(f'http://localhost:3500//chat/{str(chat_id)}/list')
        r=ast.literal_eval(getMessages(chat_id))
        messages1.update(r)
        
    #concat all the the messages of an user in a unique string
    users_messages={}
    for k,v in messages1.items():
        mes_user=db.messages.find_one({'_id':ObjectId(k)})#fetch the message
        user=mes_user['user_id']#fetch the user
        user_texts=list(db.messages.find({"user_id":user},{'text':1}))#fetch all the messages for the user
        user_text=''
        for text in user_texts:
            try:
                text = ast.literal_eval(text['text'])#some of my texts are lists some no
            except:
                text=list(text)
            txt=''
            for t in text:#put all the messages in a unique string
                txt += t
            user_text=user_text +' '+ txt
            users_messages[user]=user_text   
        
        
    sent1={}#k =user_id, v=text
    for k,v in users_messages.items():    
        sent1[k]=str(v)

    #creation of the similarity matrix for the users
    count_vectorizer = CountVectorizer()

    sparse_matrix = count_vectorizer.fit_transform(sent1.values())
    text_term_matrix = sparse_matrix.todense()
    df = pd.DataFrame(text_term_matrix, 
                  columns=count_vectorizer.get_feature_names(), 
                  index=sent1.keys())
    similarity_matrix = distance(df,df)
    sim_df = pd.DataFrame(similarity_matrix, columns=sent1.keys(), index=sent1.keys())
    
    #recommend the 3 closest users content-wise
    def get3closest(sim_df,user_id):#user is an ObjectId
        col=sim_df[user].sort_values(ascending=False)[1:]
        return list(col[0:3].index)
    output= get3closest(sim_df,ObjectId(user_id))
    output=[str(el) for el in output]
    return json.dumps({'recommended':output})