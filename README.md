# Chat Sentiment Analysis Service

##This api analyzes the `public` chat messages \(like slack public channels\) of your team and create sentiment metrics of the  people on your team. 

Heroku link: https://api-recommender.herokuapp.com/

<img src="INPUT/image.png">

### 1. User endpoints

- (GET) `/user/create/<username>`
  - **Purpose:** Create a user and save into DB
  - **Params:** `username` the user name
  - **Returns:** `user_id`
- (GET) `/user/<user_id>/recommend`
  - **Purpose:** Recommend friend to this user based on chat contents
  - **Returns:** json array with top 3 similar users

### 2. Chat endpoints

- (GET) `/chat/create` 
  - **Purpose:** Create a conversation to load messages
  - **Params:** 
        -`ids` : An array of users ids 
        -`name`: The name of the chat 
  - **Returns:** `chat_id`
- (GET) `/chat/<chat_id>/adduser`
  - **Purpose:** Add a user to a chat to add more users to a chat after it's creation.
  - **Params:** `user_id`
  - **Returns:** `chat_id`
- (POST) `/chat/<chat_id>/addmessage`
  - **Purpose:** Add a message to the conversation. Before adding the chat message to the database, check that the incoming user                    is part of this chat id. If not, raise an exception.
  - **Params:**
    - `chat_id`: Chat to store message
    - `user_id`: the user that writes the message
    - `text`: Message text
  - **Returns:** `message_id`
- (GET) `/chat/<chat_id>/list`
  - **Purpose:** Get all messages from `chat_id`
  - **Returns:** json array with all messages from this `chat_id`
- (GET) `/chat/<chat_id>/sentiment` #?lang=<lang>
  - **Purpose:** Analyze messages from `chat_id`. Use `NLTK` sentiment analysis package for this task
  - **Returns:** json with all sentiments from messages in the chat
- (GET) `/chat/ids`
  - **Purpose:** Get all chat_id from the collection `chats`
  - **Returns:** json dict with all `chat_id` in the database'
