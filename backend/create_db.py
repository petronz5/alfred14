import sqlite3

# Crea il database e la tabella
def create_database():
    conn = sqlite3.connect('backend/music.db')
    cursor = conn.cursor()

    # Crea la tabella 'songs'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            spotify_id TEXT NOT NULL
        )
    ''')

    # Aggiungi delle canzoni di esempio con i loro ID Spotify
    cursor.execute('INSERT INTO songs (name, spotify_id) VALUES (?, ?)', ('Shape of You', 'spotify:https://open.spotify.com/track/7qiZfU4dY1lWllzX7mPBI3?si=6d0468eebc0d4bfc'))
    cursor.execute('INSERT INTO songs (name, spotify_id) VALUES (?, ?)', ('I Wanna Be Yours', 'https://open.spotify.com/track/5XeFesFbtLpXzIVDNQP22n?si=76a035263d86469a'))
    cursor.execute('INSERT INTO songs (name, spotify_id) VALUES (?, ?)', ('Beautiful Things', 'https://open.spotify.com/track/5XeFesFbtLpXzIVDNQP22n?si=76a035263d86469a'))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()
