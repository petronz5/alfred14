from flask import Flask, jsonify, request, render_template
import os
import subprocess
import speech_recognition as sr
import requests
import sqlite3
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


app = Flask(__name__, static_folder='../../frontend/static', template_folder='../../frontend/templates')

# La tua API key di OpenWeatherMap
API_KEY = "7f70e112b4f209c998d537076514f17b"
# Scopes per accedere a Google Drive e Google Docs
SCOPES = [
    'https://www.googleapis.com/auth/drive', 
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/gmail.readonly',  # Per leggere le email
    'https://www.googleapis.com/auth/gmail.send',  # Per inviare email
    'https://www.googleapis.com/auth/calendar'  # Per gestire il calendario
]

# Lista per gestire la coda di riproduzione
queue = []

# Rotta per servire la pagina principale
@app.route('/')
def index():
    return render_template('index.html')

# Rotta di test per verificare se il backend funziona
@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({"message": "Alfred is working!"})


@app.route('/api/weather', methods=['POST'])
def get_weather():
    data = request.json
    city = data.get('city', 'Rome')  # Se non specificata la città, usa 'Rome' di default

    # Chiamata all'API di OpenWeatherMap
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)

    if response.status_code == 200:
        weather_data = response.json()
        weather_description = weather_data['weather'][0]['description']
        temperature = weather_data['main']['temp']
        city_name = weather_data['name']
        return jsonify({
            'city': city_name,
            'temperature': temperature,
            'description': weather_description
        })
    else:
        return jsonify({'error': 'Unable to get weather data'}), 400
    

# Funzione per ottenere l'ID Spotify della canzone dal database
def get_spotify_track_id(song_name):
    conn = sqlite3.connect('backend/music.db')  # Collegamento al database
    cursor = conn.cursor()

    # Cerca la canzone per nome (insensibile al maiuscolo/minuscolo)
    cursor.execute('SELECT spotify_id FROM songs WHERE name LIKE ?', (f'%{song_name}%',))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]  # Restituisce l'ID di Spotify
    else:
        return None

# Rotta per riprodurre musica su Spotify
@app.route('/api/play-song', methods=['POST'])
def play_song():
    data = request.json
    song_name = data.get('song_name')

    # Cerca l'ID della canzone nel database
    spotify_id = get_spotify_track_id(song_name)

    if spotify_id:
        # Apri l'applicazione Spotify e riproduci la canzone con l'ID specifico
        subprocess.run(['open', '-a', 'Spotify', spotify_id])  # Su macOS, usa il comando 'open'
        return jsonify({"result": f"Riproducendo '{song_name}' su Spotify."})
    else:
        return jsonify({"error": "Canzone non trovata nel database."}), 400
    

# Rotta per mettere in pausa o riprendere la riproduzione
@app.route('/api/pause-song', methods=['POST'])
def pause_song():
    try:
        # Esegui AppleScript per mettere in pausa o riprendere Spotify
        subprocess.run(['osascript', '-e', 'tell application "Spotify" to playpause'])
        return jsonify({"result": "Spotify in pausa o ripresa."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/next-song', methods=['POST'])
def next_song():
    try:
        subprocess.run(['osascript', '-e', 'tell application "Spotify" to next track'])
        return jsonify({"result": "Canzone successiva avviata."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    



# Rotta per aggiungere una canzone alla coda
@app.route('/api/add-to-queue', methods=['POST'])
def add_to_queue():
    data = request.json
    song_name = data.get('song_name')

    # Cerca l'ID della canzone nel database
    spotify_id = get_spotify_track_id(song_name)

    if spotify_id:
        queue.append(spotify_id)  # Aggiungi la canzone alla coda
        return jsonify({"result": f"Canzone '{song_name}' aggiunta alla coda."})
    else:
        return jsonify({"error": "Canzone non trovata nel database."}), 400


# Rotta per riprodurre la prossima canzone in coda
@app.route('/api/play-next-in-queue', methods=['POST'])
def play_next_in_queue():
    if queue:
        spotify_id = queue.pop(0)  # Rimuovi e ottieni la prossima canzone
        subprocess.run(['open', '-a', 'Spotify', spotify_id])  # Riproduci la canzone
        return jsonify({"result": "Riproducendo la prossima canzone in coda."})
    else:
        return jsonify({"error": "La coda è vuota."}), 400

# Rotta per vedere la coda
@app.route('/api/get-queue', methods=['GET'])
def get_queue():
    return jsonify(queue)



@app.route('/api/command', methods=['POST'])
def handle_command():
    data = request.json
    command = data.get('command').lower()

    # Logica per il comando
    if command.startswith("apri app"):
        app_name = command.replace("apri app", "").strip()  # Estrai il nome dell'app
        app_path = get_application_command(app_name)  # Ottiene il percorso dell'applicazione dal database

        if app_path:
            subprocess.run(["open", app_path])  # Su macOS, usa 'open' per aprire l'applicazione
            return jsonify({"result": f"Apertura di {app_name}"})
        else:
            return jsonify({"error": f"Applicazione '{app_name}' non trovata."}), 400
        
     # Chiudi un'applicazione
    elif command.startswith("chiudi app"):
        app_name = command.replace("chiudi app", "").strip()
        app_command = get_application_command(app_name)

        if app_command:
            subprocess.run(["pkill", "-f", app_command])
            return jsonify({"result": f"Chiusura di {app_name}"})
        else:
            return jsonify({"error": f"Applicazione '{app_name}' non trovata."}), 400
        
    # Comando per elencare le applicazioni disponibili
    elif command == "mostra app":
        apps = get_all_applications()
        return jsonify({"applications": apps})
    
    # Aggiungere una nuova applicazione
    elif command.startswith("aggiungi app"):
        app_data = data.get('app_data', {})
        name = app_data.get('name')
        path = app_data.get('path')
        command = app_data.get('command')

        if name and path and command:
            add_application(name, command, path)
            return jsonify({"result": f"Applicazione {name} aggiunta con successo!"})
        else:
            return jsonify({"error": "Dati dell'applicazione mancanti."}), 400
    
    elif command.startswith("apri sito"):
        site_name = command.replace("apri sito", "").strip()  # Estrai il nome del sito
        url = get_website_url(site_name)

        if url:
            subprocess.run(["open", url])  # Su macOS, usa 'open' per aprire l'URL nel browser
            return jsonify({"result": f"Apertura di {site_name} ({url})"})
        else:
            return jsonify({"error": f"Sito '{site_name}' non trovato."}), 400

    else:
        return jsonify({"error": "Comando non riconosciuto."}), 400
  

# Rotta per il riconoscimento vocale
@app.route('/api/voice-command-action', methods=['POST'])
def voice_command_action():
    try:
        # Metti in pausa la musica prima di attivare l'assistente vocale
        subprocess.run(['osascript', '-e', 'tell application "Spotify" to pause'])

        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening for command...")
            audio = recognizer.listen(source)

        # Riconoscimento del comando vocale in italiano
        command = recognizer.recognize_google(audio, language='it-IT').lower()
        print(f"Recognized command: {command}")

        # Apertura sito
        if "apri sito" in command:
            site_name = command.replace("apri sito", "").strip()
            url = get_website_url(site_name)
            if url:
                subprocess.run(["open", url])  # Apri il sito nel browser
                return jsonify({"result": f"Apertura di {site_name} ({url})"})
            else:
                return jsonify({"error": f"Sito '{site_name}' non trovato."}), 400

        # Apertura applicazione
        elif "apri app" in command:
            app_name = command.replace("apri app", "").strip()
            app_path = get_application_command(app_name)
            if app_path:
                subprocess.run(["open", app_path])  # Apri l'applicazione
                return jsonify({"result": f"Apertura di {app_name}"})
            else:
                return jsonify({"error": f"Applicazione '{app_name}' non trovata."}), 400

        # Controllo di Spotify (play, pause, next)
        elif "play" in command:
            song_name = command.replace("play", "").strip()  # Estrai il nome della canzone
            spotify_id = get_spotify_track_id(song_name)
            if spotify_id:
                subprocess.run(['open', '-a', 'Spotify', spotify_id])
                return jsonify({"result": f"Riproducendo '{song_name}' su Spotify."})
            else:
                return jsonify({"error": "Canzone non trovata."}), 400

        elif "pause" in command:
            subprocess.run(['osascript', '-e', 'tell application "Spotify" to pause'])
            return jsonify({"result": "Spotify in pausa."})

        elif "next" in command:
            subprocess.run(['osascript', '-e', 'tell application "Spotify" to next track'])
            return jsonify({"result": "Canzone successiva avviata."})

        else:
            return jsonify({"error": "Comando non riconosciuto."}), 400

    except sr.UnknownValueError:
        return jsonify({"error": "Comando vocale non capito."}), 400
    except sr.RequestError:
        return jsonify({"error": "Errore con il servizio di riconoscimento vocale."}), 500


@app.route('/api/applications', methods=['GET'])
def list_applications():
    conn = sqlite3.connect('backend/website.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT name FROM applications')
    apps = cursor.fetchall()
    
    conn.close()
    
    return jsonify({"applications": [app[0] for app in apps]})


# Rotta per creare un documento Google Docs
@app.route('/api/create-google-doc', methods=['POST'])
def create_google_doc():
    creds = authenticate_google()  # Autentica l'utente
    service = build('docs', 'v1', credentials=creds)

    # Crea un nuovo documento Google Docs
    document = service.documents().create(body={'title': 'Nuovo Documento'}).execute()
    
    doc_id = document.get('documentId')

    # URL del documento su Google Docs
    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    return jsonify({"url": url})



# Funzione per ottenere l'URL del sito dal database
def get_website_url(site_name):
    conn = sqlite3.connect('backend/website.db')  # Collegamento al database
    cursor = conn.cursor()

    # Cerca il sito per nome (insensibile al maiuscolo/minuscolo)
    cursor.execute('SELECT url FROM websites WHERE name LIKE ?', (f'%{site_name}%',))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]  # Restituisce l'URL
    else:
        return None

def get_application_command(app_name):
    conn = sqlite3.connect('backend/website.db')
    cursor = conn.cursor()
    
    # Cerca sia nel nome che nel comando
    cursor.execute('''
        SELECT path FROM applications WHERE name LIKE ? OR command LIKE ?
    ''', (f"%{app_name}%", f"%{app_name}%"))
    
    result = cursor.fetchone()
    
    conn.close()
    
    if result and result[0]:
        return result[0]  # Restituisce il percorso completo dell'applicazione
    else:
        return None

def get_all_applications():
    conn = sqlite3.connect('backend/website.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM applications')
    apps = [row[0] for row in cursor.fetchall()]
    conn.close()
    return apps

def add_application(name, command, path):
    conn = sqlite3.connect('backend/website.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO applications (name, command, path) VALUES (?, ?, ?)', (name, command, path))
    conn.commit()
    conn.close()

def authenticate_google():
    """Autentica l'utente con Google OAuth2 e restituisce le credenziali."""
    creds = None
    token_file = 'token.json'  # Il token verrà memorizzato qui dopo l'autenticazione

    # Se abbiamo già un token, lo carichiamo
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    # Se le credenziali non esistono o non sono valide, richiediamo il login all'utente
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # Rinnova il token scaduto
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials/client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)  # Lancia un server locale per ottenere l'autorizzazione

        # Salviamo le credenziali per il prossimo utilizzo
        with open(token_file, 'w') as token:
            token.write(creds.to_json())

    return creds


if __name__ == '__main__':
    app.run(debug=True)