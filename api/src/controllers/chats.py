from src.app import app
from pymongo import MongoClient
from src.helpers.errorHandler import errorHandler ,Error404 ,APIError
from src.config import DBURL
from bson.json_util import dumps
from flask import request
from datetime import datetime
from bson import ObjectId
import requests
import re
import json
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer







client = MongoClient(DBURL)
print(f"Connected to {DBURL}")
db = client.get_database("dbChat")#["users"]


'''- (GET) `/user/create/<username>`
  - **Purpose:** Create a user and save into DB
  - **Params:** `username` the user name
  - **Returns:** `user_id`
'''
@app.route("/user/create/<username>")
@errorHandler
def insertUser(username):
    name = username
    if name:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        dic={'user_name':name,
        'insertion_date':dt_string,
        'chats_list ': []
        }
        user_id=db.users.insert_one(dic)
    if not name:
        print("ERROR")
        raise Error404("name not found")
    return json.dumps({'user_id':str(user_id.inserted_id)})



'''- (GET) `/chat/create`
  - **Purpose:** Create a conversation to load messages
  - **Params:** An array of users ids `[user_id]`
  - **Returns:** `chat_id`'''   
@app.route("/chat/create") #?ids=<arr>&name=<chatname>
@errorHandler
def insertChat():
    arr = request.args.get("ids")
    try:
        name= request.args.get("name")
    except:
        name=''
    #creation of a new chat with the users included in arr
    if arr:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        dic={   
            'chat_name': name,
            'creation_date':dt_string,
            'users_list':arr
     
             }

        chat_id=db.chats.insert_one(dic)
        
        #update of the users chats_list by adding the chat id
        for user_id in arr:
            post=db.users.find_one({'_id':ObjectId(user_id)})
            post['chats_list'].append(chat_id)
            db.users.update_one({'_id':ObjectId(user_id)}, {"$set": post}, upsert=False)

    if not arr:
        print("ERROR")
        raise APIError("Tienes que mandar un query parameter ?ids=<arr>&name=<chatname>")
    
    return json.dumps({'chat_id':str(chat_id.inserted_id)})



'''- (GET) `/chat/<chat_id>/adduser`
  - **Purpose:** Add a user to a chat, this is optional just in case you want to add more users to a chat after it's creation.
  - **Params:** `user_id`
  - **Returns:** `chat_id`'''

@app.route("/chat/<chat_id>/adduser") #?user_id=<user_id>
@errorHandler
def addChatUser(chat_id):
    user_id= request.args.get("user_id")
    if user_id!=None and chat_id!=None:
        #update of the chat document by adding the user id
        post=db.chats.find_one({'_id':ObjectId(chat_id)})
        if ObjectId(user_id) not in post['users_list']:
            post['users_list'].append(ObjectId(user_id))
        db.chats.update_one({'_id':ObjectId(chat_id)}, {"$set": post}, upsert=False)
        
        #update of the user permissions by adding the chat id
        post=db.users.find_one({'_id':ObjectId(user_id)})
        if OjectId(chat_id) not in post['chats_list']:
            post['chats_list'].append(ObjectId(chat_id))
        db.users.update_one({'_id':ObjectId(user_id)}, {"$set": post}, upsert=False)
    elif not chat_id:
        print("ERROR")
        raise Error404("chat_id not found")
    elif not user_id:
        print("ERROR")
        raise APIError("You should send these query parameters ?user_id=<user_id>")

    return json.dumps({'chat_id': str(chat_id)})



'''(POST) `/chat/<chat_id>/addmessage`
  - **Purpose:** Add a message to the conversation. 
  Help: Before adding the chat message to the database, 
  check that the incoming user is part of this chat id. If not, raise an exception.
  - **Params:**
    - `chat_id`: Chat to store message
    - `user_id`: the user that writes the message
    - `text`: Message text
  - **Returns:** `message_id`
    '''

@app.route("/chat/<chat_id>/addmessage") #?user_id=<user_id>&text=<text>
@errorHandler
def addMessage(chat_id):
    user_id= request.args.get("user_id")
    text= request.args.get("text")
    
    #check if the user has the permission to post in the chat or raise an exception
    get=db.chats.find_one({"_id":ObjectId(chat_id) })
    if not ObjectId(user_id) in get['users_list']:
        raise PermissionError("Permission denied")

    #add the message to the messages collection and get the id
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    dic={'user_id': ObjectId(user_id),
         'text':text,
         'time':dt_string,
         'chat_id':ObjectId(chat_id)
        }
    message_id=db.messages.insert_one(dic)
    
    #add the message text to the messages_list of the chat

    post=db.chats.find_one({"_id":ObjectId(chat_id)})
    post['messages_list'].append(message_id.inserted_id)
    db.chats.update_one({'_id':ObjectId(chat_id)}, {"$set": post}, upsert=False)
    
    return json.dumps({'message_id':str(message_id.inserted_id)})


'''- (GET) `/chat/<chat_id>/list`
- **Purpose:** Get all messages from `chat_id`
- **Returns:** json array with all messages from this `chat_id`'''

@app.route("/chat/<chat_id>/list") 
@errorHandler
def getMessages(chat_id):
    #try:
    get=db.chats.find_one({"_id":ObjectId(chat_id)})
    messages_ids=[]
    for el in get['messages_list']:
        messages_ids.append(str(el))
    diz={}
    for m in messages_ids:
        r=db.messages.find_one({'_id':ObjectId(m)})
        diz[m]=r['text']
    #except:
    #   raise APIError("chat id not found")
    return json.dumps(diz)

'''- (GET) `/chat/<chat_id>/sentiment`
  - **Purpose:** Analyze messages from `chat_id`. Use `NLTK` sentiment analysis package for this task
  - **Returns:** json with all sentiments from messages in the chat
'''
nltk.download("vader_lexicon")
sia = SentimentIntensityAnalyzer()
@app.route("/chat/<chat_id>/sentiment") 
@errorHandler
def getSentiment(chat_id):  
    mess=requests.get(f'http://localhost:3500//chat/{chat_id}/list').json()
    sentiments={}
    for id, text in mess.items():
        sentiments[id]={'text':text,"score":sia.polarity_scores(text)} 
    return json.dumps(sentiments)



'''- (GET) `/user/<user_id>/recommend`
  - **Purpose:** Recommend friend to this user based on chat contents
  - **Returns:** json array with top 3 similar users'''

'''@app.route("/user/<user_id>/recommend") 
@errorHandler
def getSimilarUsers(user_id):  '''
