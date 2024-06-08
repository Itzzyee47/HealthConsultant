from flask import *
from datetime import *
from model import getResponds

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

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
def send_message(chat_room_id, sender_id, message, response):
  """Sends a message to a specific chat room, which must exist."""
  try:
    chat_ref = ref.child('messages')
    chat_ref.set({})
    message_ref = chat_ref.push()  # Push message
    message_ref.set({
      'chat': chat_room_id,
      'question': message,
      'response':response,
      'sender': sender_id,
      'timestamp': datetime.now().timestamp()  # Server-side timestamp
    })
  except :
    return KeyError
    # convert the timestamp to a datetime object in the local timezone
    # dt_object = datetime.fromtimestamp(timestamp)
    
def get_messages(chat_room_id, listener):
  """Listens for new messages in a chat room and calls the provided listener function."""
  chat_ref = ref.child('chats').child(chat_room_id).child('messages')
  chat_ref.listen(listener)
  
def on_message(changes):
  """Listener function to handle new messages."""
  print(f"New message: {changes}" )
    

@app.route("/getResponse", methods=['POST'])
def converse():
  # Get the user input from the request
  convoID = request.form["convoID"]
  data = request.form["message"]
  user = request.form['user']
  print(data)
  try:
    # Send to the model and get it responds
    response = getResponds(data)
    # save user sent message 
    send_message(convoID, user, data, response) 
    
    message = {"answer": response}
    
    return jsonify(message)
  except Exception as e:
    return f'An error occured: {e}', 500

@app.route("/createConvo", methods=['POST'])
def create():
  # Get the user input from the request
  user = request.form['user']
  chat_ref = ref.child('chats')
  # error handelling
  try: 
    chat_ref.set({})  # Create an empty chat room object with uniuqe id
    convoRef = chat_ref.push()  # Push creation data by who and when
    convoRef.set({
      'sender': user,
      'time': datetime.now().timestamp()  # Server-side timestamp
    })
    
    message = {"chatID": chat_ref}
    
    return jsonify(message)
  except Exception as e:
    return 500
  
@app.route("/getConversations", methods=['POST'])
def getConvos():
  # Get the user input from the request
  user = request.form['user']
  chat_ref = ref.child('chats')
  # error handelling
  try: 
    # Get all coversations belonging to a specofic user....
    convos = chat_ref.order_by_child('user').equal_to(user).get()  

    message = {"convos": convos}
    
    return jsonify(message)
  except Exception as e:
    return f'An error occured: {e}', 500
  
@app.route("/getMessagesOfChat", methods=['POST'])
def getMessages():
  # Get the user input from the request
  convoID = request.form["convoID"]
  mess_ref = ref.child('messages')
  # error handelling
  try: 
    # Get all messages belonging to a specific conversation
    convos = mess_ref.order_by_child('chat').equal_to(convoID).get()  

    message = {"messages": convos}
    
    return jsonify(message)
  except Exception as e:
    return f'An error occured: {e}', 500


if __name__ == "__main__":
  app.run(host='localhost',debug=True, port=10000)