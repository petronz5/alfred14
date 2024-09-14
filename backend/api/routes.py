from flask import Flask, jsonify, request, render_template
import os
import subprocess
import speech_recognition as sr
import requests
import sqlite3


app = Flask(__name__, static_folder='../../frontend/static', template_folder='../../frontend/templates')

# La tua API key di OpenWeatherMap
API_KEY = "7f70e112b4f209c998d537076514f17b"

# Lista in memoria per gestire gli appuntamenti
appointments = []

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
    

# Rotta per mettere in pausa la riproduzione
@app.route('/api/pause-song', methods=['POST'])
def pause_song():
    try:
        # Esegui AppleScript per mettere in pausa Spotify
        subprocess.run(['osascript', '-e', 'tell application "Spotify" to pause'])
        return jsonify({"result": "Spotify in pausa."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Rotta per accettare comandi
@app.route('/api/command', methods=['POST'])
def handle_command():
    data = request.json
    command = data.get('command')

    # Logica per il comando
    if command == "open_browser":
        subprocess.run(["open", "-a", "Safari"])  # Su macOS, per aprire Safari
        return jsonify({"result": "Opening browser..."})
    elif command == "say_hello":
        return jsonify({"result": "Hello, User!"})
    else:
        return jsonify({"error": "Unknown command"}), 400
    

# Rotta per il riconoscimento vocale
@app.route('/api/voice-command', methods=['POST'])
def voice_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for command...")
        audio = recognizer.listen(source)

    try:
        # Utilizza Google Speech Recognition per interpretare l'audio
        command = recognizer.recognize_google(audio)
        print(f"Recognized command: {command}")
        return jsonify({"command": command})
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand the audio"}), 400
    except sr.RequestError:
        return jsonify({"error": "Error with the recognition service"}), 500



if __name__ == '__main__':
    app.run(debug=True)