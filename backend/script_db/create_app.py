import sqlite3

# Crea (o collega a) il database website.db
conn = sqlite3.connect('backend/website.db')
cursor = conn.cursor()

# Crea una tabella per i siti web (se non esiste già)
cursor.execute('''
CREATE TABLE IF NOT EXISTS websites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT NOT NULL
)
''')

# Crea una tabella per le applicazioni (se non esiste già)
cursor.execute('''
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    command TEXT NOT NULL,
    path TEXT  -- Aggiungiamo una colonna per memorizzare il percorso completo (opzionale)
)
''')

# Aggiungi alcune applicazioni (puoi modificarle o aggiungerne altre)
applications = [
    ('Spotify', 'spotify', '/Applications/Spotify.app'),
    ('Chrome', 'google-chrome', '/Applications/Google Chrome.app'),
    ('Terminal', 'terminal', '/Applications/Utilities/Terminal.app'),
    ('Visual Studio Code', 'code', '/Applications/Visual Studio Code.app'),
    ('Arduino', 'arduino', '/Applications/Arduino.app'),
    ('Blender', 'blender', '/Applications/Blender.app'),
    ('Discord', 'discord', '/Applications/Discord.app'),
    ('Figma', 'figma', '/Applications/Figma.app'),
    ('OBS', 'obs', '/Applications/OBS.app'),
    ('JetBrains Toolbox', 'jetbrains', '/Applications/JetBrains Toolbox.app')
]

# Inserisci i dati nella tabella delle applicazioni
cursor.executemany('INSERT INTO applications (name, command, path) VALUES (?, ?, ?)', applications)

# Salva e chiudi la connessione
conn.commit()
conn.close()

print("Database created and applications inserted successfully.")
