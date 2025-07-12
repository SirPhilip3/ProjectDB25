# test socketio per fare l'update in tempo reale dei posti

from database import app
from flask_socketio import SocketIO, emit, join_room, leave_room
import psycopg2
import threading
import json
import time
import sys

socketio = SocketIO(app, cors_allowed_origins="*")

conn = psycopg2.connect("postgresql://postgres:1234@localhost:5432/Project-DB-test")
conn.autocommit = True

def listen() :
    with conn.cursor() as cur :
        cur.execute("LISTEN new_airplane;")
        print("🎧 Listener avviato e in ascolto per 'new_airplane'")
        sys.stdout.flush()
        
        while True:
            conn.poll()
            if conn.notifies:
                print("📬 Nuove notifiche in arrivo...")
                sys.stdout.flush()
            while conn.notifies:
                notify = conn.notifies.pop(0)
                data = notify.payload
                print("📨 Notifica ricevuta:", data)
                sys.stdout.flush() 
                with app.app_context():
                    socketio.emit('new_airplane_{id}', {'data': data})
                
            time.sleep(1)  # leggero sleep per evitare busy-waiting

# Avvia il listener in background
listener_thread = threading.Thread(target=listen, daemon=True)
listener_thread.start()

if __name__ == '__main__':
    # Use socketio.run() instead of app.run() to enable Socket.IO
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

# <!--! TEST DA ELIMINARE -->
# <script>
#     // Socket.io connection
#     const socket = io.connect('http://' + document.domain + ':' + location.port);
    
#     // Listen for new airplane notifications
#     socket.on('new_airplane_{id}', function(data) {
#         console.log("New airplane added:", data);
#         // You can update the UI here if needed
#     });
# </script>