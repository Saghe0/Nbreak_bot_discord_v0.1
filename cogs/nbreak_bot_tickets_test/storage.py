import json
import os

#______________________ Archivo para guardar datos de tickets
TICKETS_FILE = 'tickets_data.json'

def load_tickets_data():
    if os.path.exists(TICKETS_FILE):
        try:
            with open(TICKETS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_tickets_data(data):#___________________Guardar datos de tickets en archivo
    with open(TICKETS_FILE, 'w') as f:
        json.dump(data, f, indent=2)