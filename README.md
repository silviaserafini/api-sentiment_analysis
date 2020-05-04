# Chat Sentiment Analysis Service

##This api analyzes the `public` chat messages \(like slack public channels\) of your team and create sentiment metrics of the  people on your team. 

Heroku link: https://api-recommender.herokuapp.com/

<img src="INPUT/image.png">

### 1. User endpoints

- (GET) `/user/create/<username>`
  - **Purpose:** Create a user and save into DB
  - **Params:** `username` the user name
  - **Returns:** `user_id`
  
  ex http://localhost:3500/create/'Pippo'
  
- (GET) `/user/<user_id>/recommend`
  - **Purpose:** Recommend friend to this user based on chat contents
  - **Returns:** json array with top 3 similar users
  
  ex http://localhost:3500/user/5ead3bea1f313a96eed4017b/recommend

### 2. Chat endpoints

- (GET) `/chat/create` 
  - **Purpose:** Create a conversation to load messages
  - **Params:** 
        -`ids` : An array of users ids 
        -`name`: The name of the chat 
        
  ex http://localhost:3500/chat/create?ids=['5ead3bea1f313a96eed4017b','5ead3bea1f313a96eed4017d']&name='myChat'
  - **Returns:** `chat_id`
- (GET) `/chat/<chat_id>/adduser`
  - **Purpose:** Add a user to a chat to add more users to a chat after it's creation.
  - **Params:** `user_id`
  - **Returns:** `chat_id`
  
  ex http://localhost:3500/chat/5eaec9f02908c7e2052a6ad0/adduser?user_id=5ead3bea1f313a96eed40182
- (POST) `/chat/<chat_id>/addmessage`
  - **Purpose:** Add a message to the conversation. Before adding the chat message to the database, check that the incoming user                    is part of this chat id. If not, raise an exception.
  - **Params:**
   - `chat_id`: Chat to store message
   - `user_id`: the user that writes the message
   - `text`: Message text
  - **Returns:** `message_id`
  
  ex http://localhost:3500/chat/5eaec9f02908c7e2052a6ad0/addmessage?text='ciao'&user_id=5ead3bea1f313a96eed40182
- (GET) `/chat/<chat_id>/list`
  - **Purpose:** Get all messages from `chat_id`
  - **Returns:** json array with all messages from this `chat_id`
  
  ex http://localhost:3500/chat/5eaec9f02908c7e2052a6ad0/list
- (GET) `/chat/<chat_id>/sentiment` 
  - **Purpose:** Analyze messages from `chat_id`. Use `NLTK` sentiment analysis package for this task
  - **Params:** 
   - `chat_id`: Chat with the messages to analyze
   - `lang`: language of the chat (en=English, 'es'=Spanish)
  - **Returns:** json with all sentiments from messages in the chat and the avarage sentiment of the chat (last key= 'chat_sentiment'). 
  
  ex http://localhost:3500/chat/5eaec9f02908c7e2052a6ad0/sentiment?lang=es
- (GET) `/chat/ids`
  - **Purpose:** Get all chat_id from the collection `chats`
  - **Returns:** json dict with all `chat_id` in the database'
  
  ex http://localhost:3500/chat/ids