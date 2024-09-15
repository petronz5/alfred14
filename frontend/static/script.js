let isPlaying = true;  // Per tracciare lo stato della riproduzione

function playSong() {
    const songName = document.getElementById('songInput').value;
    fetch('/api/play-song', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ song_name: songName })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('songResponse').innerText = data.result || data.error;
        isPlaying = true;
        document.getElementById('playPauseButton').innerText = "Pause";  // Imposta il testo su "Pause"
    })
    .catch(error => console.error('Error:', error));
}

function togglePlayPause() {
    // Questo endpoint alterna tra play e pausa senza riavviare la canzone
    fetch('/api/pause-song', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('songResponse').innerText = data.result || data.error;
        isPlaying = !isPlaying;  // Alterna lo stato
        document.getElementById('playPauseButton').innerText = isPlaying ? "Pause" : "Play";  // Cambia testo
    })
    .catch(error => console.error('Error:', error));
}

function nextSong() {
fetch('/api/next-song', {
    method: 'POST'
})
.then(response => response.json())
.then(data => {
    document.getElementById('songResponse').innerText = data.result || data.error;
})
.catch(error => console.error('Error:', error));
}


function addToQueue() {
    const songName = document.getElementById('songInput').value;
    fetch('/api/add-to-queue', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ song_name: songName })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('songResponse').innerText = data.result || data.error;
    })
    .catch(error => console.error('Error:', error));
}

function playNextInQueue() {
    fetch('/api/play-next-in-queue', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('songResponse').innerText = data.result || data.error;
    })
    .catch(error => console.error('Error:', error));
}

function showQueue() {
    fetch('/api/get-queue', {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('queue').innerText = data.join(', ');  // Mostra la coda
    })
    .catch(error => console.error('Error:', error));
}


// Funzione per ottenere il meteo
function getWeather() {
    const city = document.getElementById('cityInput').value;
    fetch('/api/weather', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ city: city })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById('weatherResponse').innerText = data.error;
        } else {
            document.getElementById('weatherResponse').innerText = 
                `In ${data.city}, it's currently ${data.temperature}°C with ${data.description}.`;
        }
    })
    .catch(error => console.error('Error:', error));
}


// Funzione per inviare un comando al backend
function sendCommand() {
    const command = document.getElementById('commandInput').value;
    fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: command })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('response').innerText = data.result || data.error;
    })
    .catch(error => console.error('Error:', error));
}

function voiceCommand() {
    fetch('/api/voice-command-action', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('songResponse').innerText = data.result || data.error;
    })
    .catch(error => console.error('Error:', error));
}

// Funzione per ottenere data e ora in tempo reale
function updateDateTime() {
    const now = new Date();
    
    // Opzioni per formattare giorno e mese abbreviati
    const dateOptions = { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' };
    const timeOptions = { hour: '2-digit', minute: '2-digit', second: '2-digit' };

    const formattedDate = now.toLocaleDateString('en-US', dateOptions);
    const formattedTime = now.toLocaleTimeString('en-US', timeOptions);

    // Aggiorna gli elementi HTML con la data e l'ora formattate
    document.getElementById('date').innerText = formattedDate;
    document.getElementById('time').innerText = formattedTime;
}

// Esegui updateDateTime ogni secondo
setInterval(updateDateTime, 1000);

// Chiamata iniziale per mostrare subito la data e l'ora all'apertura della pagina
updateDateTime();

document.getElementById('create-doc-btn').addEventListener('click', function() {
    fetch('/api/create-google-doc', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.url) {
            // Apri il documento in una nuova finestra
            window.open(data.url, '_blank');
        } else {
            alert('Errore nella creazione del documento');
        }
    })
    .catch(error => console.error('Errore:', error));
});




