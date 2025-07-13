from flask_socketio import SocketIO
from database import app

# Initialize SocketIO once
socketio = SocketIO(app, cors_allowed_origins="*")