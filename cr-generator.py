import os
import sys
import time
import json
import shutil
import http.server
import socketserver
import threading
import requests
import urllib3
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Disable security warnings for requests without SSL verification (verify=False)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==============================================================================
# AGNOSTIC PATH CONFIGURATION
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if __file__ else os.getcwd()

if BASE_DIR.endswith("champions-report"):
    PROJECT_DIR = BASE_DIR
else:
    PROJECT_DIR = os.path.join(BASE_DIR, "applications", "champions-report")

if os.path.exists("/data/data/com.termux/files/home"):
    DOWNLOADS_DIR = "/storage/emulated/0/Download"
elif os.name == 'nt':  # Windows
    DOWNLOADS_DIR = os.path.join(os.path.expanduser('~'), 'Downloads')
else:
    DOWNLOADS_DIR = os.path.join(os.path.expanduser('~'), 'Downloads')

ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
ARTICLES_OUTPUT_DIR = os.path.join(PROJECT_DIR, "articles")

os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(ARTICLES_OUTPUT_DIR, exist_ok=True)

# ==============================================================================
# API KEY CONFIGURATION FROM .ENV FILE
# ==============================================================================
API_KEY = None
ENV_PATH = os.path.join(PROJECT_DIR, ".env") if os.path.exists(os.path.join(PROJECT_DIR, ".env")) else os.path.join(BASE_DIR, ".env")

if os.path.exists(ENV_PATH):
    try:
        with open(ENV_PATH, "r") as f:
            for line in f:
                if line.strip().startswith("GEMINI_API_KEY"):
                    API_KEY = line.split("=")[1].strip().replace('"', '').replace("'", "")
    except Exception as e:
        print(f"⚠️ Error reading .env file: {e}")

if not API_KEY:
    print("❌ Error: Incomplete configuration.")
    print("Make sure you created a '.env' file containing: GEMINI_API_KEY=your_key_here")
    sys.exit(1)

AI_MODELS_POOL = ["gemini-3.5-flash", "gemini-2.5-pro", "gemini-flash-latest"]

# ==============================================================================
# DYNAMIC TRANSLATION DICTIONARY (I18N SYSTEM)
# ==============================================================================
CURRENT_LANG = "en"  # Default global UI environment language

I18N_DICTIONARY = {
    "en": {
        "locale": "en_US",
        "label_by": "By",
        "label_published": "Published",
        "label_updated": "Updated",
        "nav_home": "Home",
        "nav_matches": "Matches",
        "nav_market": "Market",
        "nav_live": "Live Focus",
        "meta_journal": "Champion's Report Journal",
        # Terminal strings
        "ui_welcome": "      🏆 CHAMPION'S REPORT JOURNAL - AUTOMATED REDACTION 🏆     ",
        "ui_input_keyword": "\n🔍 Enter a Competition, Team or Keyword (e.g., World Cup, Serie A, Barcelona)",
        "ui_input_keyword_help": "[Leave EMPTY and press ENTER for live context auto-discovery]: ",
        "ui_time_horizon": "\n--------------------------------------------------------------------\n📅 Choose the time horizon for match discovery on the web:",
        "ui_opt_today": " [1] TODAY's Matches",
        "ui_opt_tomorrow": " [2] TOMORROW's Matches",
        "ui_select_option": "Select an option [1/2]: ",
        "ui_matches_detected": "\nMatches detected on the web in real-time:",
        "ui_select_match_id": "\nSelect match number [Press ENTER directly for assisted manual entry]: ",
        "ui_manual_mode": "\n📝 Assisted manual entry activated (No target match selected)...",
        "ui_input_home": "Enter Home Team Name (e.g., Spain): ",
        "ui_input_away": "Enter Away Team Name (e.g., Austria): ",
        "ui_input_time": "Kick-off time (e.g., 21:00 CEST): ",
        "ui_input_stadium": "Stadium Name: ",
        "ui_input_city": "City: ",
        "ui_input_slug": "Enter folder slug",
        "ui_input_title": "Enter custom Title (leave empty to let AI generate it): ",
        "ui_input_pub_time": "Enter custom publication time",
        "ui_input_multiline_prompt": "\n✍️ Enter redactor guidelines or copy-paste raw facts and Lineups for the AI.",
        "ui_check_downloads": "\n📂 Checking multimedia files in download directory: ",
        "ui_input_cover": "Enter the cover image filename present in downloads (e.g., match.jpg): ",
        "ui_img_copied": "📸 Image successfully copied and renamed for SEO: ",
        "ui_img_missing": "⚠️ Warning: File '{}' not found in '{}'. Remember to add it manually.",
        "ui_engine_start": "\n🚀 Booting multilingual AI engine with Semantic Dossier analysis...",
        "ui_preview_title": "\n====================================================================\n🌐 GRAPHICAL PREVIEW AVAILABLE (Works in Incognito mode)\n👉 Open real link: http://127.0.0.1:8080/articles/{}/it.html\n====================================================================",
        "ui_generated_title": "Generated IT Title: ",
        "ui_user_satisfaction": "\nSatisfied with the result? [Y] Save and Deploy / [N] Request edits to AI: ",
        "ui_saved_path": "\n📦 Article physically saved in path: ",
        "ui_compressing": "🤐 Compressing assets and articles...",
        "ui_archive_ready": "✅ Archive champions-report.zip ready for upload",
        "ui_cloudflare_pause": "\n--------------------------------------------------------------------\n🚀 PAUSE FOR MANUAL DEPLOY ON CLOUDFLARE PAGES\n1. Grab the newly generated folder on your phone.\n2. Upload/deploy it via Cloudflare Pages dashboard.\n3. Verify that the article is online on the real domain.\n--------------------------------------------------------------------",
        "ui_websub_prompt": "\n👉 Once deploy is completed and live online, press [ENTER] to launch WebSub Indexing Ping...",
        "ui_pinging": "\n📡 Sending instant indexation ping notification...",
        "ui_success_finish": "🏁 Operations completed with total success!",
        "ui_ai_correction": "✍️ Tell the AI what to fix or vary: ",
        "ui_rebuilding": "\n🔄 Generating tactical update structure...",
        "ui_json_error": "❌ Critical Error: AI did not return a valid JSON structure. Restarting generation...",
        "ui_template_error": "❌ Error during template compilation: ",
        "ui_shutdown_clean": "\n\n🛑 Manual interruption caught (Ctrl+C). Clean shutdown of server."
    },
    "it": {
        "locale": "it_IT",
        "label_by": "Di",
        "label_published": "Pubblicato",
        "label_updated": "Aggiornato",
        "nav_home": "Home",
        "nav_matches": "Partite",
        "nav_market": "Mercato",
        "nav_live": "Live",
        "meta_journal": "Champion's Report Journal"
    },
    "es": {
        "locale": "es_ES",
        "label_by": "Por",
        "label_published": "Publicado",
        "label_updated": "Actualizado",
        "nav_home": "Inicio",
        "nav_matches": "Partidos",
        "nav_market": "Mercado",
        "nav_live": "En Vivo",
        "meta_journal": "Champion's Report Journal"
    },
    "fr": {
        "locale": "fr_FR",
        "label_by": "Par",
        "label_published": "Publié",
        "label_updated": "Mis à jour",
        "nav_home": "Accueil",
        "nav_matches": "Matchs",
        "nav_market": "Mercato",
        "nav_live": "En Direct",
        "meta_journal": "Champion's Report Journal"
    }
}

def t(chiave):
    """i18n lookup function."""
    return I18N_DICTIONARY[CURRENT_LANG].get(chiave, chiave)

# ==============================================================================
# UTILITY HELPER FUNCTIONS (DECLARED BEFORE CALL SCOPE)
# ==============================================================================
def avvia_server_anteprima(percorso_progetto, port=8080):
    """Starts a lightweight python background thread preview server."""
    os.chdir(percorso_progetto)
    handler = http.server.SimpleHTTPRequestHandler
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("", port), handler)
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()
    return httpd

def leggi_input_multilinea(messaggio_iniziale):
    print(messaggio_iniziale)
    print("👉 Paste your text below. When done, press ENTER twice (leave an empty line) to confirm.")
    linee = []
    while True:
        try:
            linea = input()
            if linea == "":
                break
            linee.append(linea)
        except EOFError:
            break
    return "\n".join(linee)

# ==============================================================================
# REST COGNITIVE CORES & MODEL FAILOVER HANDLING
# ==============================================================================
def chiedi_raw_ai(prompt_sistema, prompt_utente, usa_search=False):
    """
    Executes a native REST HTTP call to Gemini models with Google Search Grounding support,
    managing cyclic models failover and exponential backoff on 503/429 concurrency errors.
    """
    pool_modelli = ["gemini-3.5-flash", "gemini-2.5-flash", "gemini-flash-latest"]
    attesa_saturazione = 15
    while True:
        for modello_nome in pool_modelli:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{modello_nome}:generateContent?key={API_KEY}"
                headers = {"Content-Type": "application/json"}
                
                payload = {
                    "contents": [{"parts": [{"text": prompt_utente}]}],
                    "generationConfig": {"temperature": 0.2}
                }
                
                if prompt_sistema:
                    payload["systemInstruction"] = {"parts": [{"text": prompt_sistema}]}
                
                if usa_search:
                    payload["tools"] = [{"googleSearch": {}}]

                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    return response.json()['candidates'][0]['content']['parts'][0]['text']
                
                elif response.status_code in [503, 429]:
                    print(f"⚠️ [AI ESCALATION] {modello_nome} is temporarily saturated (Status {response.status_code}).")
                    time.sleep(3)
                    print("Trying the next fallback model engine...")
                    continue
                else:
                    print(f"⚠️ [API DEBUG] {modello_nome} responded with Status {response.status_code}: {response.text}")
                    continue
            except Exception:
                continue
                
        print(f"🕒 [POOL SATURATED] All Gemini models are busy. Waiting {attesa_saturazione} seconds before retrying...")
        time.sleep(attesa_saturazione)
        attesa_saturazione = min(attesa_saturazione * 2, 120)


def genera_con_scalo_ai(prompt_sistema, prompt_utente):
    """Executes multilingual structured JSON object generation using strict object schemas."""
    tentativi_totali = 0
    mentre_attendi = 15
    
    while True:
        for modello_nome in AI_MODELS_POOL:
            try:
                print(f"🤖 Attempting REST generation with engine model: {modello_nome}...")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{modello_nome}:generateContent?key={API_KEY}"
                headers = {"Content-Type": "application/json"}
                
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt_utente}]
                    }],
                    "systemInstruction": {
                        "parts": [{"text": prompt_sistema}]
                    },
                    "generationConfig": {
                        "responseMimeType": "application/json",
                        "responseSchema": {
                            "type": "OBJECT",
                            "properties": {
                                "it": {"type": "OBJECT", "properties": {"titolo": {"type": "STRING"}, "meta_description": {"type": "STRING"}, "didascalia_foto": {"type": "STRING"}, "corpo_html": {"type": "STRING"}, "titolo_update": {"type": "STRING"}, "corpo_update": {"type": "STRING"}}, "required": ["titolo", "meta_description", "didascalia_foto", "corpo_html", "titolo_update", "corpo_update"]},
                                "en": {"type": "OBJECT", "properties": {"titolo": {"type": "STRING"}, "meta_description": {"type": "STRING"}, "didascalia_foto": {"type": "STRING"}, "corpo_html": {"type": "STRING"}, "titolo_update": {"type": "STRING"}, "corpo_update": {"type": "STRING"}}, "required": ["titolo", "meta_description", "didascalia_foto", "corpo_html", "titolo_update", "corpo_update"]},
                                "es": {"type": "OBJECT", "properties": {"titolo": {"type": "STRING"}, "meta_description": {"type": "STRING"}, "didascalia_foto": {"type": "STRING"}, "corpo_html": {"type": "STRING"}, "titolo_update": {"type": "STRING"}, "corpo_update": {"type": "STRING"}}, "required": ["titolo", "meta_description", "didascalia_foto", "corpo_html", "titolo_update", "corpo_update"]},
                                "fr": {"type": "OBJECT", "properties": {"titolo": {"type": "STRING"}, "meta_description": {"type": "STRING"}, "didascalia_foto": {"type": "STRING"}, "corpo_html": {"type": "STRING"}, "titolo_update": {"type": "STRING"}, "corpo_update": {"type": "STRING"}}, "required": ["titolo", "meta_description", "didascalia_foto", "corpo_html", "titolo_update", "corpo_update"]}
                            },
                            "required": ["it", "en", "es", "fr"]
                        },
                        "temperature": 0.65
                    }
                }
                
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                if response.status_code == 200:
                    res_json = response.json()
                    return res_json['candidates'][0]['content']['parts'][0]['text']
                else:
                    print(f"⚠️ API Error on {modello_nome} (Status {response.status_code})")
                    time.sleep(2)
            except Exception as e:
                print(f"⚠️ Connection failure with model {modello_nome}: {e}")
                time.sleep(2)
                
        tentativi_totali += 1
        print(f"🕒 Waiting {mentre_attendi} seconds before renewing the loop cycle...")
        time.sleep(mentre_attendi)
        mentre_attendi = min(mentre_attendi * 2, 120)

# ==============================================================================
# BASE HTML LAYOUT TEMPLATE (NAVIGATION HIDDEN VIA COMMENTS)
# ==============================================================================
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="{LANG}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{TITOLO_PAGINA} | Champion's Report</title>
    <link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
    <meta name="robots" content="max-image-preview:large">
    <link rel="canonical" href="https://championsreport.editories.com/articles/{SLUG}/{LANG}.html" />
    <meta property="og:locale" content="{LANG_LOCALE}" />
    <meta property="og:type" content="article" />
    <meta property="og:title" content="{TITOLO_PAGINA} | Champion's Report" />
    <meta property="og:description" content="{META_DESCRIPTION}" />
    <meta property="og:url" content="https://championsreport.editories.com/articles/{SLUG}/{LANG}.html" />
    <meta property="og:site_name" content="Champion's Report" />
    <meta property="og:image" content="https://championsreport.editories.com/assets/{IMMAGINE_FILE}" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="675" />
    <style>
        :root {{ --primary-blue: #0044ff; --hover-blue: #0033cc; --bg-light: #f8f9fa; --text-dark: #333; }}
        * {{ box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background-color: var(--bg-light); color: var(--text-dark); margin: 0; padding: 0; }}
        header {{ background: #fff; padding: 30px 0 20px 0; text-align: center; border-bottom: 1px solid #eee; position: relative; }}
        .header-container {{ max-width: 600px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; gap: 15px; position: relative; }}
        .main-title-3d {{ font-family: 'Dancing Script', cursive; font-weight: 700; font-size: 2.4rem; text-align: center; width: 100%; color: #0044ff; display: inline-block; letter-spacing: 2px; margin: 0; -webkit-text-stroke: 1.2px #93c5fd; text-shadow: 1px 1px 0px #0033cc, 2px 2px 0px #0022aa, 3px 3px 0px #001188, 4px 4px 5px rgba(0, 17, 136, 0.4), 5px 5px 10px rgba(0, 0, 0, 0.15); }}
        .lang-selector {{ position: absolute; top: 10px; right: 20px; font-size: 0.85rem; }}
        .lang-selector select {{ padding: 4px 8px; border-radius: 6px; border: 1px solid #ccc; font-family: 'Inter', sans-serif; cursor: pointer; }}
        nav {{ display: flex; justify-content: center; gap: 20px; padding: 15px; background: #fff; border-bottom: 1px solid #eee; }}
        nav a {{ text-decoration: none; color: #555; font-weight: 600; font-size: 0.95rem; transition: color 0.2s; }}
        nav a:hover {{ color: var(--primary-blue); }}
        .container {{ max-width: 600px; margin: 20px auto; padding: 20px; background: #fff; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
        h1 {{ font-weight: 600; color: #111; line-height: 1.25; font-size: 1.7rem; margin-top: 10px; margin-bottom: 8px; text-align: justify; text-justify: inter-word; word-spacing: -1px; }}
        .meta-box {{ font-size: 0.85rem; color: #666; margin: 0 0 20px 0; display: flex; flex-wrap: wrap; gap: 12px; border-bottom: 1px solid #eee; padding-bottom: 12px; }}
        .meta-box strong {{ color: #2d3748; font-weight: 600; }}
        h3 {{ font-weight: 600; color: #2d3748; font-size: 1.3rem; margin-top: 25px; margin-bottom: 12px; border-left: 4px solid var(--primary-blue); padding-left: 10px; text-align: justify; text-justify: inter-word; word-spacing: -0.5px; }}
        .content {{ font-size: 1.1rem; line-height: 1.7; color: #444; text-align: justify; }}
        .content p {{ text-align: justify; text-justify: inter-word; letter-spacing: -0.2px; word-break: break-word; -webkit-hyphens: auto; hyphens: auto; margin-bottom: 16px; }}
        .cover-hero {{ width: 100%; height: auto; border-radius: 8px; margin: 15px 0; object-fit: cover; }}
        .ad-slot {{ margin: 25px 0; text-align: center; min-height: 50px; }}
        .lineups {{ background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 20px; margin: 20px 0; font-size: 0.95rem; }}
        .lineups p {{ text-align: left; margin-bottom: 8px; line-height: 1.5; }}
        .lineups strong {{ color: #1a202c; }}
        .coach {{ margin-top: 8px; font-style: italic; color: #4a5568; display: block; }}
    </style>
    <link rel="alternate" hreflang="it" href="https://championsreport.editories.com/articles/{SLUG}/it.html" />
    <link rel="alternate" hreflang="en" href="https://championsreport.editories.com/articles/{SLUG}/en.html" />
    <link rel="alternate" hreflang="es" href="https://championsreport.editories.com/articles/{SLUG}/es.html" />
    <link rel="alternate" hreflang="fr" href="https://championsreport.editories.com/articles/{SLUG}/fr.html" />
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "LiveBlogPosting",
      "@id": "https://championsreport.editories.com/articles/{SLUG}/{LANG}.html",
      "headline": "{TITOLO_PAGINA}",
      "description": "{META_DESCRIPTION_CLEAN}",
      "coverageStartTime": "{DATA_ISO}T{ORARIO_MATCH_24}:00+02:00",
      "coverageEndTime": "{DATA_ISO}T{ORARIO_FINE_ISO}:00+02:00",
      "datePublished": "{DATA_ISO}T{ORARIO_PUBBLICAZIONE_24}:00+02:00",
      "dateModified": "{DATA_ISO}T{ORARIO_PUBBLICAZIONE_24}:00+02:00",
      "author": {{
        "@type": "Organization",
        "name": "{LABEL_META_JOURNAL}",
        "url": "https://championsreport.editories.com"
      }},
      "publisher": {{
        "@type": "Organization",
        "name": "{LABEL_META_JOURNAL}",
        "logo": {{
          "@type": "ImageObject",
          "url": "https://championsreport.editories.com/assets/logo.png"
        }}
      }},
      "image": "https://championsreport.editories.com/assets/{IMMAGINE_FILE}",
      "liveBlogUpdate": [
        {{
          "@type": "BlogPosting",
          "@id": "https://championsreport.editories.com/articles/{SLUG}/{LANG}.html#update1",
          "headline": "{TITOLO_UPDATE_JSON}",
          "datePublished": "{DATA_ISO}T{ORARIO_PUBBLICAZIONE_24}:00+02:00",
          "articleBody": "{CORPO_UPDATE_JSON}"
        }}
      ]
    }}
    </script>
    <script type="text/javascript" src="//pl24036573.highperformanceformat.com/59/e2/be/59e2be2897fb5bbfdfa336336ff3d8b5.js"></script>
</head>
<body>
    <header>
        <div class="lang-selector">
            <select onchange="location = './' + this.value.toLowerCase() + '.html';">
                <option value="IT" {SEL_IT}>IT</option>
                <option value="EN" {SEL_EN}>EN</option>
                <option value="ES" {SEL_ES}>ES</option>
                <option value="FR" {SEL_FR}>FR</option>
            </select>
        </div>
        <div class="header-container">
            <h1 class="main-title-3d">Champion's Report</h1>
        </div>
    </header>
    <nav>
        </nav>
    <main class="container">
        <h1>{TITOLO_PAGINA}</h1>
        <div class="meta-box">
            <span>{LABEL_BY} : <strong>{LABEL_META_JOURNAL}</strong></span>
            <span>{LABEL_PUBLISHED} : <strong>{DATA_TESTUALE}</strong></span>
            <span>{LABEL_UPDATED} : <strong>{ORARIO_PUBBLICAZIONE_CEST}</strong></span>
        </div>
        <div class="ad-slot">
            <script>atOptions = {{ 'key' : '4f733990b106119b14a43ee4fc1d1f9a', 'format' : 'iframe', 'height' : 50, 'width' : 320, 'params' : {{}} }};</script>
            <script src="https://www.highperformanceformat.com/4f733990b106119b14a43ee4fc1d1f9a/invoke.js"></script>
        </div>
        <img src="../../assets/{IMMAGINE_FILE}" class="cover-hero" alt="{ALT_IMRAPIDE}">
        <p style="text-align: center; font-size: 0.85rem; color: #666; font-style: italic; margin-top: -8px; margin-bottom: 20px;">{DIDASCALIA_SOTTO_FOTO}</p>
        <div class="content">
            {CORPO_ARTICOLO_HTML}
        </div>
        <div class="ad-slot">
            <script>atOptions = {{ 'key' : '4f733990b106119b14a43ee4fc1d1f9a', 'format' : 'iframe', 'height' : 50, 'width' : 320, 'params' : {{}} }};</script>
            <script src="https://www.highperformanceformat.com/4f733990b106119b14a43ee4fc1d1f9a/invoke.js"></script>
        </div>
    </main>
</body>
</html>
"""

FEED_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
    <title>Champions Report Mondiali 2026</title>
    <link>https://championsreport.editories.com</link>
    <description>Notizie flash e cronaca live dei Mondiali 2026</description>
    <atom:link rel="hub" href="https://pubsubhubbub.appspot.com/" />
    <atom:link rel="self" href="https://championsreport.editories.com/articles/{SLUG}/feed.xml" type="application/rss+xml" />
    <item>
        <title>{TITOLO_IT}</title>
        <link>https://championsreport.editories.com/articles/{SLUG}/it.html</link>
        <guid isPermaLink="true">https://championsreport.editories.com/articles/{SLUG}/it.html</guid>
        <description>{DESCRIZIONE_IT}</description>
    </item>
    <item>
        <title>{TITOLO_EN}</title>
        <link>https://championsreport.editories.com/articles/{SLUG}/en.html</link>
        <guid isPermaLink="true">https://championsreport.editories.com/articles/{SLUG}/en.html</guid>
        <description>{DESCRIZIONE_EN}</description>
    </item>
    <item>
        <title>{TITOLO_ES}</title>
        <link>https://championsreport.editories.com/articles/{SLUG}/es.html</link>
        <guid isPermaLink="true">https://championsreport.editories.com/articles/{SLUG}/es.html</guid>
        <description>{DESCRIZIONE_ES}</description>
    </item>
    <item>
        <title>{TITOLO_FR}</title>
        <link>https://championsreport.editories.com/articles/{SLUG}/fr.html</link>
        <guid isPermaLink="true">https://championsreport.editories.com/articles/{SLUG}/fr.html</guid>
        <description>{DESCRIZIONE_FR}</description>
    </item>
</channel>
</rss>
"""

# ==============================================================================
# GLOBAL COMPREHENSIVE EDITORIAL SYSTEM PROMPTS
# ==============================================================================
PROMPT_SISTEMA_EDITORIALE = """Sei il redattore capo e traduttore multilingua del Champion's Report Journal. Il tuo compito è generare un articolo giornalistico sportivo di alto livello espandendo le informazioni fornite.
Devi generare l'articolo contemporaneamente in quattro lingue: Italiano, Inglese, Spagnolo e Francese.
L'output finale DEVE essere un oggetto JSON valido, contenente le chiavi per ciascuna lingua. Non includere blocchi di testo fuori dal JSON, né markdown tipo ```json.

Regole editoriali tassative per tutte le lingue:
1. Stile giornalistico d'alto respiro SEO-oriented, fluido, narrative ed evoluto.
2. DIVIETO ASSOLUTO DI COPIARE TITOLI GREZZI DELLA PARTITA. È severamente vietato usare espressioni pigre o didascaliche per i titoli dei paragrafi. Inventa invece per i tag <h3> dei titoli creativi, originali, metaforici, giornalistici ed accattivanti legati alle squadre.
3. Sviluppa discorsivamente la cronaca, l'atmosfera e i duelli sul campo in modo approfondito ed esteso. Evita elenchi di dati.
4. Formattazione: Usa esclusivamente paragrafi giustificati con <p> e inserisci tag <strong> accurati attorno dei nomi dei giocatori chiave, orari, stadi e concetti cruciali.
5. Il testo deve contenere tre capitoli fluidi introdotti da tag <h3> con i titoli creativi generati ad hoc, seguiti dall'ultimo box <h3> dedicato alle formazioni.
6. Il primo paragrafo dell'articolo DEVE iniziare subito dopo il titolo principale, parlando del contesto emotivo e del clima della vigilia.
7. Nella sezione dedicata alle probabili formazioni, DEVI riprodurere le linee guida o formazioni ipotizzate inserendole esattamente in questo schema HTML grigio:

<div class="lineups">
    <p><strong>Nome Squadra A (Modulo-Tattico):</strong> Portiere; Difensore1, Difensore2, Difensore3, Difensore4; Centrocampista1, Centrocampista2; Attaccante1, Attaccante2, Attaccante3; Attaccante4.</p>
    <p class="coach">Ct: Nome Allenatore A</p>
    <br>
    <p><strong>Nome Squadra B (Modulo-Tattico):</strong> Portiere; Difensore1, Difensore2, Difensore3, Difensore4; Centrocampista1, Centrocampista2, Centrocampista3, Centrocampista4; Attaccante1, Attaccante2.</p>
    <p class="coach">Ct: Nome Allenatore B</p>
</div>
Sostituisci i nomi delle squadre, i moduli e i giocatori con quelli reali dell'incontro, rispettando la punteggiatura.

Struttura del JSON richiesto in output:
{{
  "it": {{ "titolo": "...", "meta_description": "...", "didascalia_foto": "...", "corpo_html": "...", "titolo_update": "...", "corpo_update": "..." }},
  "en": {{ "titolo": "...", "meta_description": "...", "didascalia_foto": "...", "corpo_html": "...", "titolo_update": "...", "corpo_update": "..." }},
  "es": {{ "titolo": "...", "meta_description": "...", "didascalia_foto": "...", "corpo_html": "...", "titolo_update": "...", "corpo_update": "..." }},
  "fr": {{ "titolo": "...", "meta_description": "...", "didascalia_foto": "...", "corpo_html": "...", "titolo_update": "...", "corpo_update": "..." }}
}}
"""

def compila_file_finali(slug, dati_partita, dati_generati_json, orario_pubblicazione_custom="16:00"):
    cartella_articolo = os.path.join(ARTICLES_OUTPUT_DIR, slug)
    os.makedirs(cartella_articolo, exist_ok=True)

    ora_match_pulita = dati_partita["ora"].split()[0]
    ora_pubblicazione = orario_pubblicazione_custom
    try:
        ore, minuti = map(int, ora_match_pulita.split(':'))
        ora_fine = f"{(ore + 2) % 24:02d}:{minuti:02d}"
    except Exception:
        ora_fine = "23:45"

    for lang in ["it", "en", "es", "fr"]:
        lang_key = lang if lang in I18N_DICTIONARY else "en"
        info = I18N_DICTIONARY[lang_key]
        
        sel_it = "selected" if lang == "it" else ""
        sel_en = "selected" if lang == "en" else ""
        sel_es = "selected" if lang == "es" else ""
        sel_fr = "selected" if lang == "fr" else ""

        art_lang = dati_generati_json[lang]
        meta_clean = BeautifulSoup(art_lang["meta_description"], "html.parser").get_text()

        html_compilato = HTML_TEMPLATE.format(
            LANG=lang,
            SLUG=slug,
            LANG_LOCALE=info["locale"],
            TITOLO_PAGINA=art_lang["titolo"],
            META_DESCRIPTION=art_lang["meta_description"],
            META_DESCRIPTION_CLEAN=meta_clean,
            IMMAGINE_FILE=dati_partita["immagine_copertina"],
            DATA_ISO=dati_partita["data_iso"],
            ORARIO_MATCH_24=ora_match_pulita,
            ORARIO_FINE_ISO=ora_fine,
            ORARIO_PUBBLICAZIONE_24=ora_pubblicazione.split()[0],
            TITOLO_UPDATE_JSON=art_lang["titolo_update"],
            CORPO_UPDATE_JSON=art_lang["corpo_update"],
            SEL_IT=sel_it, SEL_EN=sel_en, SEL_ES=sel_es, SEL_FR=sel_fr,
            LABEL_BY=info["label_by"], LABEL_PUBLISHED=info["label_published"], LABEL_UPDATED=info["label_updated"],
            LABEL_META_JOURNAL=info["meta_journal"],
            NAV_HOME=info["nav_home"], NAV_MATCHES=info["nav_matches"], NAV_MARKET=info["nav_market"], NAV_LIVE=info["nav_live"],
            DATA_TESTUALE=dati_partita["data_testo"],
            ORARIO_PUBBLICAZIONE_CEST=ora_pubblicazione if "CEST" in ora_pubblicazione else f"{ora_pubblicazione} CEST",
            ALT_IMRAPIDE=meta_clean,
            DIDASCALIA_SOTTO_FOTO=art_lang["didascalia_foto"],
            CORPO_ARTICOLO_HTML=art_lang["corpo_html"]
        )
        
        with open(os.path.join(cartella_articolo, f"{lang}.html"), "w", encoding="utf-8") as f:
            f.write(html_compilato)

    feed_compilato = FEED_TEMPLATE.format(
        SLUG=slug,
        TITOLO_IT=dati_generati_json["it"]["titolo"],
        DESCRIZIONE_IT=BeautifulSoup(dati_generati_json["it"]["meta_description"], "html.parser").get_text(),
        TITOLO_EN=dati_generati_json["en"]["titolo"],
        DESCRIZIONE_EN=BeautifulSoup(dati_generati_json["en"]["meta_description"], "html.parser").get_text(),
        TITOLO_ES=dati_generati_json["es"]["titolo"],
        DESCRIZIONE_ES=BeautifulSoup(dati_generati_json["es"]["meta_description"], "html.parser").get_text(),
        TITOLO_FR=dati_generati_json["fr"]["titolo"],
        DESCRIZIONE_FR=BeautifulSoup(dati_generati_json["fr"]["meta_description"], "html.parser").get_text()
    )
    with open(os.path.join(cartella_articolo, "feed.xml"), "w", encoding="utf-8") as f:
        f.write(feed_compilato)

def esegui_ping_websub(slug):
    """Broadcast XML maps pings instantly."""
    feed_url = f"https://championsreport.editories.com/articles/{slug}/feed.xml"
    hub_url = "https://pubsubhubbub.appspot.com/"
    try:
        r = requests.post(hub_url, data={"hub.mode": "publish", "hub.url": feed_url}, timeout=10)
        if r.status_code in [200, 204]:
            print("✅ [WebSub] Indexation ping successfully broadcasted to Googlebot!")
        else:
            print(f"⚠️ [WebSub] Anomalous hub response (Status {r.status_code})")
    except Exception as e:
        print(f"❌ Unable to connect with WebSub Hub: {e}")


# ==============================================================================
# 1. LIVE CONTEXT AUTO-DISCOVERY SCANNER (HUNTER WARMUP)
# ==============================================================================
def rileva_contesto_calcio_del_giorno(data_target):
    """Executes a grounding micro-call to isolate the main football tournament running live."""
    print("🔄 [HUNTER WARMUP] Scanning web geopolitically to isolate the premium headline competition...")
    prompt_contesto = f"""Quali sono i tornei o le competizioni di calcio principali (nazionali o internazionali) in corso di svolgimento nella data del {data_target}? 
    Rispondi unicamente con il nome della competizione più importante in lingua inglese (es: FIFA World Cup 2026, UEFA Euro 2026, UEFA Champions League). Non aggiungere altre parole."""
    
    try:
        competizione_rilevata = chiedi_raw_ai(None, prompt_contesto, usa_search=True)
        if competizione_rilevata and len(competizione_rilevata.strip()) > 3:
            contesto_pulito = competizione_rilevata.strip().split('\n')[0].replace('*', '').strip()
            print(f"🏆 [CONTEXT FOUND] Isolated premium tournament: '{contesto_pulito}'")
            return contesto_pulito
    except Exception:
        pass
    return "World Cup"


# ==============================================================================
# 2. INTERNATIONAL SLUG ALGORITHM GENERATION (SEO CLEAN)
# ==============================================================================
def genera_slug_internazionale_ai(squadra_a, squadra_b, competizione, anno):
    """Translates team names to English on the fly and generates structural international slugs."""
    prompt_slug = f"""Traduci i nomi di queste due squadre di calcio in lingua inglese (es: 'Spagna' diventa 'Spain', 'Stati Uniti' diventa 'USA'). 
    Restituisci esclusivamente una stringa in minuscolo con le due squadre in inglese separate da un trattino, seguite da un trattino e il nome della competizione compresso senza spaces e l'anno.
    Esempio di output: spain-austria-worldcup2026
    Dati: Squadra A: {squadra_a}, Squadra B: {squadra_b}, Competizione: {competizione}, Anno: {anno}.
    Fornisci SOLO la stringa dello slug pulita, senza markdown o punti fermi."""
    try:
        slug_raw = chiedi_raw_ai(None, prompt_slug, usa_search=False)
        if slug_raw:
            slug_clean = slug_raw.strip().lower().replace(" ", "")
            slug_clean = "".join(c for c in slug_clean if c.isalnum() or c in "-_")
            return slug_clean
    except Exception:
        pass
    fallback = f"{squadra_a.lower()}-{squadra_b.lower()}-match{anno}".replace(" ", "")
    return "".join(c for c in fallback if c.isalnum() or c in "-_")


# ==============================================================================
# 3. QUALITATIVE TRAFFIC ANALYSIS FOR PREDICTIVE GOLDEN SLOT TIMING
# ==============================================================================
def calcola_slot_oro_pubblicazione_ai(squadra_a, squadra_b, orario_match, stadio, citta, data_testo):
    """Analyzes kickoff data metrics and locations to compute strategic high-volume traffic slots."""
    print("🔮 [COGNITIVE PREDICTION] Calculating Golden Slot parameters for strategic publication timing...")
    prompt_orario = f"""Sei un esperto SEO e data analyst sportivo. Analizza questo evento:
    Match: {squadra_a} vs {squadra_b}
    Calcio d'inizio: {orario_match}
    Luogo: {stadio}, {citta} ({data_testo})
    
    COMPITO: Calcola l'orario di pubblicazione strategico (Slot d'Oro) per massimizzare le visite prima che l'attenzione sul web esploda (es: 2-3 ore prima del calcio d'inizio se in Europa, o calcolato sul fuso orario nativo se d'oltreoceano).
    CONVERTI TASSATIVAMENTE questo orario finale nel formato fuso italiano (es: 18:30 CEST o 14:15 CEST).
    Fornisci SOLO l'orario convertito in formato 'HH:MM CEST'. Nessun commento o testo aggiuntivo."""
    try:
        orario_calcolato = chiedi_raw_ai(None, prompt_orario, usa_search=False)
        if orario_calcolato and ":" in orario_calcolato:
            return orario_calcolato.strip().replace("*", "")
    except Exception:
        pass
    return "19:00 CEST"


# ==============================================================================
# TARGETED DISCOVERY WEB ENGINE (LASER TIME-FILTERED HUNTER ELEMENT)
# ==============================================================================
def targeted_discovery_remota_ai(parola_chiave, data_target, anno_corrente):
    """Injects deterministic time restrictions directly into Google queries to narrow the search footprint."""
    print(f"🔍 [TARGETED DISCOVERY] Targeting query parameters for: '{parola_chiave}' on target date {data_target}...")
    
    # Costringiamo Google e l'AI a basarsi solo sugli orari sincronizzati con il fuso italiano (CEST/CET)
    query_iper_mirata = f"partite calcio oggi {data_target} competizione {parola_chiave} {anno_corrente} orario italia"
    prompt_utente_cerca = f"""Effettua una ricerca sul web in tempo reale usando questa query: '{query_iper_mirata}'.
    Trova unicamente i match programmati o giocati in questa data specifica ({data_target}).
    Normalizza tassativamente gli orari dei match convertendoli tutti nel fuso orario italiano (CEST).
    Esempio: se una partita si gioca a Los Angeles alle 17:00 del 1 luglio, calcola che l'ora italiana corrisponde alle 02:00 del 2 luglio CEST, quindi mostrala sotto la data del 2 luglio.
    Elenca in lingua inglese le squadre coinvolte, l'orario finale convertito in ora italiana (CEST), lo stadio e la città."""
    
    risultato_ricerca_testuale = chiedi_raw_ai(None, prompt_utente_cerca, usa_search=True)
    if not risultato_ricerca_testuale or len(risultato_ricerca_testuale.strip()) < 10:
        print("⚠️ No raw data harvested from the web for this specific date criteria.")
        return []

    print(f"🧠 [COGNITIVE PARSING] Sifting and modeling structural records...")
    
    prompt_sistema_parse = "Sei un analista dati. Converti le informazioni fornite in un array JSON nativo valido e pulito."
    prompt_utente_parse = f"""Analizza questo blocco informativo raccolto dal web:
---
{risultato_ricerca_testuale}
---
COMPITO: Isola i match che appartengono alla data del {data_target} secondo il fuso orario italiano/CEST e strutturali in un array JSON nativo.
Assicurati che il campo 'ora' rifletta chirurgicamente l'orario italiano (es: '02:00 CEST' o '21:00 CEST'), risolvendo le discrepanze orarie dei report grezzi internazionali.

Struttura esatta richiesta (nomi dei campi e valori strutturali rigorosamente in inglese):
[ {{
    "squadra_a": "Nome Squadra Casa",
    "squadra_b": "Nome Squadra Ospite",
    "ora": "Orario convertito in ora italiana (es. 02:00 CEST o 21:00 CEST)",
    "data_iso": "{data_target}",
    "data_testo": "Data estesa in inglese (es. July 2, {anno_corrente})",
    "stadio": "Nome Stadio",
    "citta": "Città"
}} ]

REGOLE TASSATIVE:
1. Se nel testo non ci sono partite per il {data_target}, restituisci un array vuoto: []
2. Fornisci SOLO il JSON puro, senza markdown."""

    raw_json = chiedi_raw_ai(prompt_sistema_parse, prompt_utente_parse, usa_search=False)
    
    try:
        clean_json_str = raw_json.strip()
        if "```json" in clean_json_str:
            clean_json_str = clean_json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json_str:
            clean_json_str = clean_json_str.split("```")[1].split("```")[0].strip()
            
        match_json = re.search(r'\[\s*\{.*\}\s*\]', clean_json_str, re.DOTALL)
        if match_json:
            return json.loads(match_json.group(0))
        return json.loads(clean_json_str)
    except Exception:
        return []

def estrai_dati_tecnici_ai(squadra_a, squadra_b, anno_corrente):
    """Stato 3: Pulls down probable setups, tactical news, and team conditions."""
    print(f"🎯 [STATO 3 - TARGETED EXTRACTION] Building laser tactical blueprint for: {squadra_a} vs {squadra_b}...")
    prompt_sistema = "Sei un analista tattico della redazione sportiva. Generi report tecnici sulle squadre."
    prompt_utente = f"Genera un report di dettaglio aggiornato per il match {squadra_a} vs {squadra_b} inserito nel contesto della competizione dell'anno {anno_corrente}. Estrai le probabili formazioni, i ballottaggi aperti, l'elenco degli indisponibili o squalificati e lo stato di forma delle due squadre."
    return chiedi_raw_ai(prompt_sistema, prompt_utente, usa_search=False)

def genera_guida(match_info, dossier_tecnico):
    """Stato 4: Formats a synthesis layout wrapper to guide localized copywriters."""
    testo_guida = f"""
====================================================================
📋 [STATO 4 - SYNTHESIS] EDITORIAL ORIENTATION BLUEPRINT GUIDE
====================================================================
⚽ MATCH: {match_info['squadra_a']} vs {match_info['squadra_b']}
⏰ KICKOFF TIME: {match_info.get('ora', '20:45 CEST')}   📅 TARGET DATE: {match_info.get('data_testo', '')} ({match_info.get('data_iso', '')})
🏟️ VENUE LOCATION: {match_info.get('stadio', 'MetLife Stadium')} ({match_info.get('citta', 'New York')})
ℹ️ CONTEXT SCOPE: {match_info.get('dati_contesto', 'Official fixture.')}
====================================================================
📝 IN-DEPTH DOSSIER DATA RECORDS (PROBABLE LINEUPS & TEAM NEWS):
{dossier_tecnico}
====================================================================
"""
    return testo_guida

# ==============================================================================
# MAIN REDACTION PIPELINE EXECUTION BLOCK
# ==============================================================================
if __name__ == "__main__":
    try:
        print("====================================================================")
        print(t("ui_welcome"))
        print("====================================================================")

        data_corrente = datetime.now()
        anno_corrente = data_corrente.year

        # STEP 1: KEYWORD SEARCH SELECTION
        print(t("ui_input_keyword"))
        query_input = input(t("ui_input_keyword_help")).strip()
        
        if not query_input:
            query_comp = rileva_contesto_calcio_del_giorno(data_corrente.strftime("%d %B %Y"))
        else:
            query_comp = query_input

        # STEP 2: TIME BOUNDARY CONFIGURATION
        print(t("ui_time_horizon"))
        print(t("ui_opt_today"))
        print(t("ui_opt_tomorrow"))
        scelta_tempo = input(t("ui_select_option")).strip() or "1"

        target_date = data_corrente + timedelta(days=1) if scelta_tempo == "2" else data_corrente
        iso_giorno = target_date.strftime("%Y-%m-%d")

        # STEP 3: RAW HARVESTING RUN
        match_filtrati = targeted_discovery_remota_ai(query_comp, iso_giorno, anno_corrente)
        
        match_selezionato = None
        lista_match = []

        if match_filtrati:
            for idx, m in enumerate(match_filtrati[:6]):
                sq_a = m.get('squadra_a', 'Unknown')
                sq_b = m.get('squadra_b', 'Unknown')
                
                dossier = estrai_dati_tecnici_ai(sq_a, sq_b, anno_corrente)
                
                lista_match.append({
                    "id": str(idx + 1),
                    "squadra_a": sq_a,
                    "squadra_b": sq_b,
                    "ora": m.get('ora', '18:00 CEST'),
                    "data_iso": m.get('data_iso', iso_giorno),
                    "data_testo": m.get('data_testo', target_date.strftime("%B %d, %Y")),
                    "stadio": m.get('stadio', 'MetLife Stadium'),
                    "citta": m.get('citta', 'International Arena'),
                    "dati_contesto": f"Official fixture ({query_comp} {anno_corrente}).",
                    "dossier_match": dossier if dossier else "Data package ready for deployment."
                })

        if lista_match:
            print(t("ui_matches_detected"))
            for m in lista_match:
                print(f" [{m['id']}] {m['squadra_a']} vs {m['squadra_b']} ({m['ora']} - {m['data_testo']})")
            scelta = input(t("ui_select_match_id")).strip()
            try:
                if scelta:
                    match_selezionato = lista_match[int(scelta) - 1]
            except Exception:
                pass
        
        if not match_selezionato:
            print(t("ui_manual_mode"))
            sq_a = input(t("ui_input_home")).strip()
            if not sq_a:
                print("❌ Null input field. Aborting process.")
                sys.exit(0)
            sq_b = input(t("ui_input_away")).strip()
            ora_m = input(t("ui_input_time")).strip() or "20:45 CEST"
            stadio_m = input(t("ui_input_stadium")).strip() or "MetLife Stadium"
            citta_m = input(t("ui_input_city")).strip() or "New York"
            dossier = estrai_dati_tecnici_ai(sq_a, sq_b, anno_corrente)
            
            match_selezionato = {
                "id": "1", "squadra_a": sq_a, "squadra_b": sq_b, "ora": ora_m,
                "data_iso": iso_giorno,
                "data_testo": target_date.strftime("%B %d, %Y").strip(),
                "stadio": stadio_m, "citta": citta_m, "dati_contesto": f"Direct clash between {sq_a} and {sq_b}.",
                "dossier_match": dossier if dossier else "Data package ready for deployment."
            }

        # Print briefing outline guide
        testo_guida_definitivo = genera_guida(match_selezionato, match_selezionato.get('dossier_match', 'No technical dossier records matched.'))
        print(testo_guida_definitivo)

        # AI English slug translation step
        slug_pulito = genera_slug_internazionale_ai(match_selezionato['squadra_a'], match_selezionato['squadra_b'], query_comp, anno_corrente)
        slug_articolo = input(f"{t('ui_input_slug')} [{slug_pulito}]: ").strip() or slug_pulito

        # AI Predictive timing slot suggestion
        orario_predetto_default = calcola_slot_oro_pubblicazione_ai(
            match_selezionato['squadra_a'], match_selezionato['squadra_b'], 
            match_selezionato['ora'], match_selezionato['stadio'], 
            match_selezionato['citta'], match_selezionato['data_testo']
        )
        
        titolo_custom = input(t("ui_input_title")).strip()
        orario_pub_custom = input(f"{t('ui_input_pub_time')} [leave empty for AI suggestion: {orario_predetto_default}]: ").strip() or orario_predetto_default

        # Gather customized structural lines
        prompt_redazionale_utente = leggi_input_multilinea(t("ui_input_multiline_prompt"))

        print(f"{t('ui_check_downloads')}{DOWNLOADS_DIR}")
        nome_foto = ""
        while not nome_foto:
            nome_foto = input(t("ui_input_cover")).strip()
            if not nome_foto:
                print("⚠️ Error: File name cannot be empty. Specify exact syntax.")
        
        estensione = os.path.splitext(nome_foto)[1] or ".jpg"
        nome_foto_finalizzat_assets = f"{slug_articolo}{estensione}"
        
        percorso_foto_origine = os.path.join(DOWNLOADS_DIR, nome_foto)
        if os.path.exists(percorso_foto_origine):
            shutil.copy(percorso_foto_origine, os.path.join(ASSETS_DIR, nome_foto_finalizzat_assets))
            print(f"{t('ui_img_copied')}{nome_foto_finalizzat_assets}")
        else:
            print(t("ui_img_missing").format(nome_foto, DOWNLOADS_DIR))
        
        match_selezionato["immagine_copertina"] = nome_foto_finalizzat_assets

        prompt_completo_ai = f"""Sviluppa l'articolo giornalistico sportivo multilingua seguendo fedelmente queste linee guida ed informazioni reali riscontrate:
- Incontro: {match_selezionato['squadra_a']} vs {match_selezionato['squadra_b']}
- Data e Ora: {match_selezionato['data_testo']} alle ore {match_selezionato['ora']}
- Stadio: {match_selezionato['stadio']}

DOSSIER INFORMATIVO ESTRATTO IN TEMPO REALE DA PROCESSARE:
{match_selezionato.get('dossier_match', 'Nessun dato remoto riscontrato.')}

Direttive ed Espansioni fornite dal Redattore:
{prompt_redazionale_utente}
"""
        if titolo_custom:
            prompt_completo_ai += f"\n- Vincolo Titolo Italiano: Devi usare tassativamente questo titolo: '{titolo_custom}'. Traducilo in modo coerente e vario per le altre tre lingue."

        print(t("ui_engine_start"))
        raw_ai_output = genera_con_scalo_ai(PROMPT_SISTEMA_EDITORIALE, prompt_completo_ai)
        
        revisione_attiva = True
        while revisione_attiva:
            try:
                clean_json_str = raw_ai_output.strip().replace("```json", "").replace("```", "")
                dati_generati_json = json.loads(clean_json_str)
                
                compila_file_finali(slug_articolo, match_selezionato, dati_generati_json, orario_pub_custom)
                
                server_preview = avvia_server_anteprima(PROJECT_DIR, port=8080)
                
                print(t("ui_preview_title").format(slug_articolo))
                print(f"{t('ui_generated_title')}{dati_generati_json['it']['titolo']}")
                
                scelta_utente = input(t("ui_user_satisfaction")).strip().lower()
                
                server_preview.shutdown()
                
                if scelta_utente == 'y':
                    revisione_attiva = False
                    print(f"{t('ui_saved_path')}{os.path.join(ARTICLES_OUTPUT_DIR, slug_articolo)}/")
                    print(t("ui_compressing"))
                    os.system("rm -f champions-report.zip")
                    os.system("zip -r champions-report.zip assets articles > /dev/null")
                    print(t("ui_archive_ready"))
                    
                    print(t("ui_cloudflare_pause"))
                    print("\n🌐 PRODUCTION PRETTYLINKS FOR THIS DEPLOYMENT:")
                    print(f"🇮🇹 Italian:  https://championsreport.editories.com/articles/{slug_articolo}/it.html")
                    print(f"🇬🇧 English:  https://championsreport.editories.com/articles/{slug_articolo}/en.html")
                    print(f"🇪🇸 Spanish:  https://championsreport.editories.com/articles/{slug_articolo}/es.html")
                    print(f"🇫🇷 French:   https://championsreport.editories.com/articles/{slug_articolo}/fr.html")
                    print(f"📡 RSS Feed:  https://championsreport.editories.com/articles/{slug_articolo}/feed.xml\n")
                    input(t("ui_websub_prompt"))
                    
                    print(t("ui_pinging"))
                    esegui_ping_websub(slug_articolo)
                    print(t("ui_success_finish"))
                else:
                    modifica_richiesta = input(t("ui_ai_correction")).strip()
                    prompt_correzione = f"Ecco l'output precedente:\n{raw_ai_output}\n\nApplica rigorosamente queste modifiche mantenendo intatta la struttura JSON, creando titoli originali descrittivi ed elaborando lo schieramento lineups:\n{modifica_richiesta}"
                    print("\n🔄 Generating update structure...")
                    raw_ai_output = genera_con_scalo_ai(PROMPT_SISTEMA_EDITORIALE, prompt_correzione)
                    
            except json.JSONDecodeError:
                print(t("ui_json_error"))
                raw_ai_output = genera_con_scalo_ai(PROMPT_SISTEMA_EDITORIALE, prompt_completo_ai)
            except Exception as e:
                print(f"{t('ui_template_error')}{e}")
                revisione_attiva = False

    except KeyboardInterrupt:
        print(t("ui_shutdown_clean"))
        try:
            server_preview.shutdown()
        except NameError:
            pass
        sys.exit(0)
