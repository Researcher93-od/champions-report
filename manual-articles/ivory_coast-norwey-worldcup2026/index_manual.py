import requests

# ==============================================================================
# 1. CONFIGURAZIONE: Slug reale dell'articolo impostato correttamente
# ==============================================================================
ARTICLE_SLUG = "ivory_coast-norwey-worldcup2026"

# Il link del feed si autogenera dinamicamente usando la variabile sopra
feed_url = f"https://championsreport.editories.com/manual-articles/{ARTICLE_SLUG}/feed.xml"
hub_url = "https://pubsubhubbub.appspot.com/"
payload = {"hub.mode": "publish", "hub.url": feed_url}

print(
    f"🚀 Avvio notifica push tramite WebSub per l'articolo: {ARTICLE_SLUG}..."
)
print("-" * 50)

try:
    response = requests.post(hub_url, data=payload)

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
