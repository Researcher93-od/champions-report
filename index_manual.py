from googleapiclient.discovery import build
import google.auth

# Carica le tue credenziali esistenti
key_file = 'service-account.json'
creds, _ = google.auth.load_credentials_from_file(key_file, scopes=['https://www.googleapis.com/auth/indexing'])
service = build('indexing', 'v3', credentials=creds)

# Elenco dei 4 URL manuali pronti per l'indicizzazione istantanea
urls = [
    "https://championsreport.editories.com/manual-articles/brazil-japan-worldcup2026/it.html",
    "https://championsreport.editories.com/manual-articles/brazil-japan-worldcup2026/en.html",
    "https://championsreport.editories.com/manual-articles/brazil-japan-worldcup2026/es.html",
    "https://championsreport.editories.com/manual-articles/brazil-japan-worldcup2026/fr.html"
]

print("🚀 Avvio notifica push su Google Indexing API...")
print("-" * 50)

for url in urls:
    lang = url.split('/')[-1].upper()
    body = {'url': url, 'type': 'URL_UPDATED'}
    
    try:
        response = service.urlNotifications().publish(body=body).execute()
        print(f"✅ [{lang}] Inviato con successo!")
    except Exception as e:
        print(f"❌ [{lang}] Errore durante l'invio: {e}")

print("-" * 50)
print("🏁 Operazione completata!")
