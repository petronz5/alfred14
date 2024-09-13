from flask import Flask, jsonify, request, render_template
import os
import subprocess
import speech_recognition as sr

app = Flask(__name__, static_folder='../../frontend', template_folder='../../frontend')

# Rotta per servire la pagina principale
@app.route('/')
def index():
    return render_template('index.html')

# Rotta di test per verificare se il backend funziona
@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({"message": "Alfred is working!"})

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
