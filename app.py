from flask import *
from datetime import *
from model import getResponds

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db, auth

# Replace with your Firebase project configuration
cred = credentials.Certificate('healthKey.json')  # Download from Firebase console
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://healthai-99da4-default-rtdb.europe-west1.firebasedatabase.app/'
})

ref = db.reference('/')

app = Flask(__name__)


def login_required(func):
    def wrapper_func(*args, **kwargs):
        if 'user' in session:
            return func(*args, **kwargs)
            
        data = {"message":"Please login or signup"}
        return render_template("landingPage.html",**data)
    
    wrapper_func.__name__ = func.__name__  # Preserve the original function name
    return wrapper_func

# send message to database...
def send_message(chat_room_id, sender_id, message):
  """Sends a message to a specific chat room, creating it if it doesn't exist."""
  chat_ref = ref.child('chats').child(chat_room_id)
  # Check if chat room exists
  if not chat_ref.get():
    chat_ref.set({})  # Create an empty chat room object
    message_ref = chat_ref.child('messages').push()  # Push message
    message_ref.set({
      'content': message,
      'sender': sender_id,
      'timestamp': datetime.now().timestamp()  # Server-side timestamp
  })
  else:
    message_ref = chat_ref.child('messages').push()  # Push message
    message_ref.set({
      'content': message,
      'sender': sender_id,
      'timestamp': datetime.now().timestamp()  # Server-side timestamp
  })
    # convert the timestamp to a datetime object in the local timezone
    # dt_object = datetime.fromtimestamp(timestamp)
    
def get_messages(chat_room_id, listener):
  """Listens for new messages in a chat room and calls the provided listener function."""
  chat_ref = ref.child('chats').child(chat_room_id).child('messages')
  chat_ref.listen(listener)
  
def on_message(changes):
  """Listener function to handle new messages."""
  for change in changes:
    print(f"New message: {change.val()['content']}")
    
    
# Example usage
# chat_room_id = 'chatRoom1'
# sender_id = 'user123'
# message = 'Hello, everyone!'

# send_message(chat_room_id, sender_id, message)

# def on_message(snapshot, changes):
  # """Listener function to handle new messages."""
  # for change in changes:
    # print(f"New message: {change.val()['content']}")

# get_messages(chat_room_id, on_message)
  

@app.route("/", methods=['POST'])
def index():
    # Get the user input from the request
    data = request.form["message"]
    user = request.form['user']
    print(data)
    # Send to the model and get it responds
    response = getResponds(data)
    # save user sent message 
    send_message(user, user, data) 
    
    get_messages(user, on_message(response))
    # save bot sent message 
    send_message(user, 'bot', response)
    
    message = {"answer": response}
    
    return jsonify(message)




if __name__ == "__main__":
    app.run(host='localhost',debug=True, port=10000)