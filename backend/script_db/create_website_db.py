import sqlite3

# Crea (o collega a) il database website.db
conn = sqlite3.connect('backend/website.db')
cursor = conn.cursor()

# Crea una tabella per i siti web (se non esiste)
cursor.execute('''
CREATE TABLE IF NOT EXISTS websites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT NOT NULL
)
''')

# Aggiungi alcune voci (puoi modificarle o aggiungerne altre)
websites = [
    ('Google', 'https://www.google.com'),
    ('YouTube', 'https://www.youtube.com'),
    ('Wikipedia', 'https://www.wikipedia.org'),
    ('Netflix', 'https://www.wikipedia.org'),
    ('Prime Video', 'https://www.primevideo.com/-/it/offers/nonprimehomepage/ref=atv_dp_mv_c_9zZ8D2_hom?language=it'),
    ('Amazon', 'https://www.amazon.it/?&tag=goitab-21&ref=pd_sl_781ozcfkw6_e&adgrpid=156928205950&hvpone=&hvptwo=&hvadid=710580145406&hvpos=&hvnetw=g&hvrand=13149751851097425168&hvqmt=e&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=1008463&hvtargid=kwd-10573980&hydadcr=10841_2239539'),
    ('Whatsapp', 'https://web.whatsapp.com/'),
    ('ChatGPT', 'https://chatgpt.com/'),
    ('Github', 'https://github.com/'),
    ('Streaming Community', 'https://streamingcommunity.buzz/'),
    ('Booking', 'https://www.booking.com/index.it.html?aid=2311236&label=it-it-booking-desktop-VRZD0IC5lt9Ulq*ajTZ_bgS652829000338%3Apl%3Ata%3Ap1%3Ap2%3Aac%3Aap%3Aneg%3Afi%3Atikwd-65526620%3Alp1008463%3Ali%3Adec%3Adm&gclid=CjwKCAjw6JS3BhBAEiwAO9waFwTZtl5tdTULroeRGXnCy5Y5PN8gX3OgFpR2m_7nW6lZcbsR6SSYexoCbA8QAvD_BwE&auth_success=1'),
    ('Trip Advisor', 'https://www.tripadvisor.it/'),
    ('Google Meet', 'https://meet.google.com/landing'),
    ('Gmail', 'https://mail.google.com/mail/u/0/?pli=1#inbox'),
    ('Google Maps', 'https://www.google.it/maps/@45.0025226,7.5578055,15z?entry=ttu&g_ep=EgoyMDI0MDkxMS4wIKXMDSoASAFQAw%3D%3D'),
    ('Linkedin', 'https://www.linkedin.com/in/davide-petroni-980155216/'),
    ('Stack Overflow', 'https://stackoverflow.com/'),
    ('Trasfermarkt', 'https://www.transfermarkt.it/'),
    ('Moodle', 'https://informatica.i-learn.unito.it/'),
    ('Google Drive', 'https://drive.google.com/drive/u/0/home'),
    ('Google Docs', 'https://docs.google.com/document/d/1CN3UJZiYOELptEFV9QZVPyBQmDFNpNbEipdsJ7vyiog/edit?hl=it'),
    ('Google Sheets', 'https://docs.google.com/spreadsheets/d/1v-O7d_meW1FKYLBrgtzajoskT0S--2r7A1GDGAmEk8Y/edit?gid=0#gid=0')

]

# Inserisci i dati nella tabella
cursor.executemany('INSERT INTO websites (name, url) VALUES (?, ?)', websites)

# Salva e chiudi la connessione
conn.commit()
conn.close()

print("Database created and websites inserted successfully.")
