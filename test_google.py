from googleapiclient.discovery import build
import google.auth

# Carica credenziali
key_file = 'service-account.json' 
creds, _ = google.auth.load_credentials_from_file(key_file, scopes=['https://www.googleapis.com/auth/indexing'])
service = build('indexing', 'v3', credentials=creds)

# Test con il tuo dominio (home page)
url = "https://championsreport.editories.com/"
body = {'url': url, 'type': 'URL_UPDATED'}

try:
    response = service.urlNotifications().publish(body=body).execute()
    print("Successo! Ecco la risposta di Google:")
    print(response)
except Exception as e:
    print(f"Errore riscontrato: {e}")
