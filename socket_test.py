# test socketio per fare l'update in tempo reale dei posti

from database import app
from flask_socketio import SocketIO, emit, join_room, leave_room
import psycopg2
import threading
import json
import time
import sys
from socket_io_init import socketio
from flask import request

conn = psycopg2.connect("postgresql://postgres:1234@localhost:5432/Project-DB-test")
conn.autocommit = True

active_rooms = {}
rooms_lock = threading.Lock()

# quando un client si connette, viene chiamato questo handler
@socketio.on('join_flight')
def handle_join_flight(data):
    flight_id = data.get('flight_id')
    room_name = f'flight_{flight_id}'
    join_room(room_name)
    print(f"Client {request.sid} joined room {room_name}")
    
    # Avvia listener solo se non esiste già
    start_listening_for_room(flight_id, room_name)
    
    emit('joined_flight', {'flight_id': flight_id, 'room': room_name})

# quando un client lascia la room, viene chiamato questo handler
@socketio.on('leave_flight')
def handle_leave_flight(data):
    """Client lascia la room del volo"""
    flight_id = data['flight_id']
    room_name = f'flight_{flight_id}'
    
    leave_room(room_name)
    print(f"Client {request.sid} left room {room_name}")
    
    # Controlla se la room è vuota e ferma il listener se necessario
    check_and_stop_listener(room_name)


def start_listening_for_room(flight_id, room_name):
    """Avvia listener per una specifica room"""
    flight_id = str(flight_id)
    safe_flight_id = flight_id.replace("-", "_")
    channel_name = f'seat_availability_{safe_flight_id}'
    
    with rooms_lock:
        if room_name in active_rooms:
            print(f"Listener for {room_name} is already running.")
            return
            
        # Crea stop event per terminazione pulita
        stop_event = threading.Event()
        
        def listen():
            try:
                with conn.cursor() as cur:
                    cur.execute(f"LISTEN {channel_name};")
                    print(f"Listener avviato per {channel_name} -> room {room_name}")
                    sys.stdout.flush()
                    
                    while not stop_event.is_set():
                        conn.poll()
                        if conn.notifies:
                            print("Nuove notifiche in arrivo...")
                            sys.stdout.flush()
                            
                            while conn.notifies:
                                notify = conn.notifies.pop(0)
                                try:
                                    data = json.loads(notify.payload)
                                    print(f"Notifica ricevuta per room {room_name}:", data)
                                    sys.stdout.flush()
                                    
                                    # Emit solo ai client nella room specifica
                                    with app.app_context():
                                        socketio.emit('seat_update', {'data': data, 'flight_id': flight_id}, room=room_name)
                                        
                                except json.JSONDecodeError as e:
                                    print(f"Error parsing notification: {e}")
                        
                        time.sleep(0.1)  # Polling 
                        
            except Exception as e:
                print(f"Listener error for {room_name}: {e}")
            finally:
                with rooms_lock:
                    active_rooms.pop(room_name, None)
                print(f"Listener terminato per {room_name}")

        listener_thread = threading.Thread(target=listen, daemon=True)
        active_rooms[room_name] = {
            'thread': listener_thread,
            'stop_event': stop_event,
            'flight_id': flight_id
        }
        listener_thread.start()

def check_and_stop_listener(room_name):
    """Ferma il listener se la room è vuota"""
    print(f"Controllo se la room {room_name} è vuota...")
    with rooms_lock:
        if room_name in active_rooms:
            # Controlla se ci sono ancora client nella room
            room_clients = socketio.server.manager.get_participants('/', room_name)
            
            if not room_clients:  # Room vuota
                print(f"Room {room_name} è vuota, fermando listener...")
                active_rooms[room_name]['stop_event'].set()

@socketio.on('disconnect')
def handle_disconnect():
    """Gestisce disconnessione client"""
    print(f"🔌 Client {request.sid} disconnected")


# def stop_all_listeners():
#     """Ferma tutti i listener attivi"""
#     with rooms_lock:
#         for room_name, room_info in active_rooms.items():
#             room_info['stop_event'].set()
#         active_rooms.clear()
#     print("Tutti i listener fermati")
