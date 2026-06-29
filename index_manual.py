import requests

# URL del file feed che pubblicherai su Cloudflare Pages
feed_url = "https://championsreport.editories.com/manual-articles/brazil-japan-worldcup2026/feed.xml"

# URL dell'Hub WebSub ufficiale di Google
hub_url = "https://pubsubhubbub.appspot.com/"

# Parametri richiesti dal protocollo WebSub
payload = {"hub.mode": "publish", "hub.url": feed_url}

print("🚀 Avvio notifica push tramite WebSub su Google Hub...")
print("-" * 50)

try:
    # Invia la richiesta HTTP POST all'hub pubblico di Google
    response = requests.post(hub_url, data=payload)

    # L'hub risponde con codice 204 (No Content) o 200 quando riceve il ping correttamente
    if response.status_code in [200, 204]:
        print("✅ [WebSub] Notifica inviata con successo!")
        print(
            "Googlebot ha ricevuto l'impulso per scansionare il tuo feed XML immediatamente."
        )
    else:
        print(
            f"❌ [WebSub] Errore dall'hub (Stato {response.status_code}): {response.text}"
        )
except Exception as e:
    print(f"❌ Errore di connessione durante il ping: {e}")

print("-" * 50)
print("🏁 Operazione completata!")
