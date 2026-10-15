import os
import sys
import time
import json
import shutil
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
# DYNAMIC TRANSLATION DICTIONARY (I18N SYSTEM - ZHTR COMPLIANT)
# ==============================================================================
CURRENT_LANG = os.environ.get("CR_LANG", "it").lower()

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
        "ui_preview_title": "\n====================================================================\n🌐 PRODUCTION PREVIEW AVAILABLE\n👉 Open real link: https://championsreport-admin.editories.com/articles/{}/it.html\n====================================================================",
        "ui_generated_title": "Generated IT Title: ",
        "ui_user_satisfaction": "\nSatisfied with the result? [Y] Save and Deploy / [N] Request edits to AI: ",
        "ui_saved_path": "\n📦 Article physically saved in path: ",
        "ui_compressing": "🤐 Compressing assets and articles...",
        "ui_archive_ready": "✅ Archive champions-report.zip ready for upload",
        "ui_cloudflare_pause": "\n--------------------------------------------------------------------\n🚀 CLOUDFLARE PAGES WORKFLOW DISPATCH DEPLOY\n--------------------------------------------------------------------",
        "ui_websub_prompt": "\n👉 Once deploy is completed and live online, press [ENTER] to launch WebSub Indexing Ping...",
        "ui_pinging": "\n📡 Sending instant indexation ping notification...",
        "ui_success_finish": "🏁 Operations completed with total success!",
        "ui_ai_correction": "✍️ Tell the AI what to fix or vary: ",
        "ui_rebuilding": "\n🔄 Generating tactical update structure...",
        "ui_json_error": "❌ Critical Error: AI did not return a valid JSON structure. Restarting generation...",
        "ui_template_error": "❌ Error during template compilation: ",
        "ui_shutdown_clean": "\n\n🛑 Manual interruption caught (Ctrl+C). Clean shutdown of process.",
        "tag_already_written": "🔵 [ALREADY WRITTEN]",
        "tag_live_finished": "🟡 Live/Finished",
        "tag_future": "🟢 Future (Not started)",
        "ui_caption_prompt_title": "\n✍️  [INTERACTIVE CAPTION PROMPT] Explain to the AI how to create the caption",
        "ui_caption_prompt_help": "👉 (e.g., 'Translate vision description', 'Highlight the celebration of...').",
        "ui_caption_prompt_confirm": "👉 Press ENTER twice on an empty line to confirm. Leave empty to auto-generate:",
        "ui_fase3_operation_title": "Choose the operation to execute:",
        "ui_fase3_opt_update": " [1] UPDATE (Adds a flash block or modifies metadata without touching the core text)",
        "ui_fase3_opt_rewrite": " [2] REWRITE (Deletes the old article and regenerates it from scratch)",
        "ui_fase3_select_option": "Select an option [1/2 or any other key to cancel]: ",
        "ui_fase3_mode_update": "🔄 SURGICAL UPDATE mode activated.",
        "ui_fase3_input_flash": "✍️ Enter the flash note or variation to apply (times, injuries, live): ",
        "ui_fase3_mode_rewrite": "🔄 TOTAL REWRITE mode activated. The old file will be replaced.",
        "ui_fase3_cancelled_msg": "🛑 Operation cancelled.",
        "ui_fase2_pre_match": "📅 [Time Filter]: Unlocked and automatically set to [1] Pre-Match option.",
        "ui_fase2_post_match": "📅 [Time Filter]: Unlocked and automatically set to [2] Post-Match option.",
        "ui_fase3_alert_pre": "⚠️ [ALERT PRE-MATCH] A Pre-Match preview for {} vs {} is already in the archive!",
        "ui_fase3_alert_post": "⚠️ [ALERT POST-MATCH] A definitive Post-Match article for {} vs {} is already registered!",
        "ui_multiline_advanced_confirm": "👉 Write the text. Press ENTER twice consecutively on an empty line to confirm.",
        "ui_multiline_confirm": "👉 Paste your text below. When done, press ENTER twice (leave an empty line) to confirm.",
        "ui_title_multiline_help": "👉 You can use multiple lines. Press ENTER twice on an empty line to confirm:",
        "ui_saving_draft": "\n💾 Saving current article state to localized draft file...",
        "ui_processing_surgical": "\n🔄 Processing surgical localized edit updates (Saving token payloads)...",
        "ui_production_links": "\n🌐 PRODUCTION CLICKABLE LINKS:",
        "ui_google_prettylinks": "\n✨ GOOGLE SEARCH CONSOLE PRETTYLINKS (SEO OPTIMIZED):",
        "ui_stato4_header": "====================================================================\n📋 [STATO 4 - SYNTHESIS] EDITORIAL ORIENTATION BLUEPRINT GUIDE\n====================================================================",
        "ui_stato4_match": "⚽ MATCH: {} vs {}",
        "ui_stato4_time": "⏰ KICKOFF TIME: {}   📅 TARGET DATE: {} ({})",
        "ui_stato4_venue": "🏟️ VENUE LOCATION: {} ({})",
        "ui_stato4_context": "ℹ️ CONTEXT SCOPE: {}",
        "ui_stato4_dossier_title": "====================================================================\n📝 IN-DEPTH DOSSIER DATA RECORDS (PROBABLE LINEUPS & TEAM NEWS):",
        "ui_stato4_footer": "====================================================================\n",
        "ui_link_it": "🇮🇹 Italian:  ",
        "ui_link_en": "🇬🇧 English:  ",
        "ui_link_es": "🇪🇸 Spanish:  ",
        "ui_link_fr": "🇫🇷 French:   ",
        "ui_link_rss": "📡 RSS Feed:  ",
        "ui_pretty_it": "🇮🇹 IT: ",
        "ui_pretty_en": "🇬🇧 EN: ",
        "ui_pretty_es": "🇪🇸 ES: ",
        "ui_pretty_fr": "🇫🇷 FR: ",
        "ui_env_read_error": "⚠️ Error reading .env file: {}",
        "ui_config_incomplete": "❌ Error: Incomplete configuration.",
        "ui_config_env_instructions": "Make sure GEMINI_API_KEY is configured in your environment or secrets.",
        "ui_port_fallback": "⚠️ Port {} bypass fallback triggered: {}",
        "ui_ai_escalation": "⚠️ [AI ESCALATION] {} is temporarily saturated (Status {}).",
        "ui_ai_trying_fallback": "Trying the next fallback model engine...",
        "ui_api_debug": "⚠️ [API DEBUG] {} responded with Status {}: {}",
        "ui_pool_saturated": "🕒 [POOL SATURATED] All Gemini models are busy. Waiting {} seconds before retrying...",
        "ui_attempting_rest": "🤖 Attempting REST generation with engine model: {}...",
        "ui_api_error_model": "⚠️ API Error on {} (Status {})",
        "ui_connection_failure": "⚠️ Connection failure with model {}: {}",
        "ui_waiting_cycle": "🕒 Waiting {} seconds before renewing the loop cycle...",
        "ui_websub_success": "✅ [WebSub] Indexation ping successfully broadcasted to Googlebot!",
        "ui_websub_anomalous": "⚠️ [WebSub] Anomalous hub response (Status {})",
        "ui_websub_error": "❌ Unable to connect with WebSub Hub: {}",
        "ui_hunter_warmup": "🔄 [HUNTER WARMUP] Scanning web geopolitically to isolate the premium headline competition...",
        "ui_context_found": "🏆 [CONTEXT FOUND] Isolated premium tournament: '{}'",
        "ui_cognitive_prediction": "🔮 [COGNITIVE PREDICTION] Calculating Golden Slot parameters for strategic publication timing...",
        "ui_targeted_discovery": "🔍 [TARGETED DISCOVERY] Targeting query parameters for: '{}' on target date {}...",
        "ui_no_raw_data": "⚠️ No raw data harvested from the web for this specific date criteria.",
        "ui_cognitive_parsing": "🧠 [COGNITIVE PARSING] Sifting and modeling structural records...",
        "ui_stato3_extraction": "🎯 [STATO 3 - TARGETED EXTRACTION] Building laser tactical blueprint for: {} vs {}...",
        "ui_vision_none": "None (File not found)",
        "ui_vision_init": "\n👁️  [VISION ENGINE] Initializing multimodal frame analysis via Gemini...",
        "ui_vision_output": "📸 IMAGE SCAN ANALYSIS OUTPUT:\n{}",
        "ui_vision_breakdown": "Vision processing breakdown: {}",
        "ui_vision_unavailable": "Vision engine temporarily unavailable.",
        "ui_null_input": "❌ Null input field. Aborting process.",
        "ui_cover_name_empty": "⚠️ Error: File name cannot be empty. Specify exact syntax.",
        "ui_no_cover_data": "No cover image analytical data.",
        "ui_no_remote_data": "No remote context data fetched.",
        "ui_editorial_postmatch_note": "\n\n[EDITORIAL NOTE: This match is finished. Do NOT use the lineages block. Focus exclusively on final tactical match review and statistics.]",
        "ui_context_postmatch": "Official Post-Match Review ({})",
        "ui_context_prematch": "Official Pre-Match Fixture ({})",
        "ui_dispatch_inputs_loaded": "📥 [INPUT DISPATCH] Parameters successfully parsed from console trigger payload.",
        "ui_automated_execution": "🤖 Headless automated execution initiated."
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
        "meta_journal": "Champion's Report Journal",
        "ui_welcome": "      🏆 CHAMPION'S REPORT JOURNAL - REDAZIONE AUTOMATIZZATA 🏆     ",
        "ui_input_keyword": "\n🔍 Inserisci Competizione, Squadra o Parola Chiave (es. Mondiali, Serie A, Barcellona)",
        "ui_input_keyword_help": "[Lascia VUOTO e premi INVIO per l'auto-rilevamento live del contesto]: ",
        "ui_time_horizon": "\n--------------------------------------------------------------------\n📅 Scegli l'orizzonte temporale per la ricerca partite sul web:",
        "ui_opt_today": " [1] Partite di OGGI",
        "ui_opt_tomorrow": " [2] Partite di DOMANI",
        "ui_select_option": "Seleziona un'opzione [1/2]: ",
        "ui_matches_detected": "\nPartite rilevate sul web in tempo reale:",
        "ui_select_match_id": "\nSeleziona numero partita [Premi INVIO direttamente per inserimento manuale]: ",
        "ui_manual_mode": "\n📝 Modalità inserimento manuale assistito attivata (Nessun match selezionato)...",
        "ui_input_home": "Inserisci Nome Squadra Casa (es. Spagna): ",
        "ui_input_away": "Inserisci Nome Squadra Ospite (es. Austria): ",
        "ui_input_time": "Orario inizio match (es. 21:00 CEST): ",
        "ui_input_stadium": "Nome Stadio: ",
        "ui_input_city": "Città: ",
        "ui_input_slug": "Inserisci slug cartella",
        "ui_input_title": "Inserisci Titolo personalizzato (lascia vuoto per farlo generare all'IA): ",
        "ui_input_pub_time": "Inserisci orario pubblicazione personalizzato",
        "ui_input_multiline_prompt": "\n✍️ Inserisci direttive redazionali o incolla fatti grezzi e formazioni per l'IA.",
        "ui_check_downloads": "\n📂 Controllo file multimediali nella cartella download: ",
        "ui_input_cover": "Inserisci il nome del file copertina presente nei download (es. match.jpg): ",
        "ui_img_copied": "📸 Immagine copiata e rinominata con successo per la SEO: ",
        "ui_img_missing": "⚠️ Attenzione: File '{}' non trovato in '{}'. Ricordati di aggiungerlo manualmente.",
        "ui_engine_start": "\n🚀 Avvio motore IA multilingua con analisi Dossier Semantico...",
        "ui_preview_title": "\n====================================================================\n🌐 ANTEPRIMA PRODUZIONE DISPONIBILE\n👉 Apri link: https://championsreport-admin.editories.com/articles/{}/it.html\n====================================================================",
        "ui_generated_title": "Titolo IT Generato: ",
        "ui_user_satisfaction": "\nSoddisfatto del risultato? [Y] Salva e Pubblica / [N] Richiedi modifiche all'IA: ",
        "ui_saved_path": "\n📦 Articolo salvato fisicamente nel percorso: ",
        "ui_compressing": "🤐 Compressione asset e articoli in corso...",
        "ui_archive_ready": "✅ Archivio champions-report.zip pronto per il caricamento",
        "ui_cloudflare_pause": "\n--------------------------------------------------------------------\n🚀 DEPLOY CLOUDFLARE PAGES VIA WORKFLOW DISPATCH\n--------------------------------------------------------------------",
        "ui_websub_prompt": "\n👉 A deploy ultimato e visibile online, premi [INVIO] per lanciare il Ping di Indicizzazione WebSub...",
        "ui_pinging": "\n📡 Invio notifica di indicizzazione immediata...",
        "ui_success_finish": "🏁 Operazioni completate con pieno successo!",
        "ui_ai_correction": "✍️ Indica all'IA cosa correggere o variare: ",
        "ui_rebuilding": "\n🔄 Generazione struttura di aggiornamento tattico...",
        "ui_json_error": "❌ Errore Critico: L'IA non ha restituito una struttura JSON valida. Riavvio generazione...",
        "ui_template_error": "❌ Errore durante la compilazione del template: ",
        "ui_shutdown_clean": "\n\n🛑 Interruzione manuale rilevata (Ctrl+C). Arresto pulito del processo.",
        "tag_already_written": "🔵 [GIÀ SCRITTO]",
        "tag_live_finished": "🟡 Live/Terminato",
        "tag_future": "🟢 Futuro (Non iniziato)",
        "ui_caption_prompt_title": "\n✍️  [PROMPT DIDASCALIA INTERATTIVO] Spiega all'IA come creare la didascalia",
        "ui_caption_prompt_help": "👉 (es. 'Traduci la descrizione vision', 'Evidenzia l'esultanza di...').",
        "ui_caption_prompt_confirm": "👉 Premi INVIO due volte su una riga vuota per confermare. Lascia vuoto per autogenerare:",
        "ui_multiline_advanced_confirm": "👉 Scrivi il testo. Premi INVIO due volte consecutive su una riga vuota per confermare.",
        "ui_fase2_pre_match": "📅 [Filtro Temporale]: Sbloccata ed impostata automaticamente opzione [1] Pre-Match.",
        "ui_fase2_post_match": "📅 [Filtro Temporale]: Sbloccata ed impostata automaticamente opzione [2] Post-Match.",
        "ui_fase3_alert_pre": "⚠️ [ALERT PRE-MATCH] Un’anteprima Pre-Match per {} vs {} è già presente in archivio!",
        "ui_fase3_alert_post": "⚠️ [ALERT POST-MATCH] Un articolo definitivo Post-Match per {} vs {} risulta già registrato!",
        "ui_fase3_operation_title": "Scegli l'operazione da eseguire:",
        "ui_fase3_opt_update": " [1] AGGIORNA (Aggiunge un blocco flash o modifica i metadati senza toccare il testo core)",
        "ui_fase3_opt_rewrite": " [2] RISCRIVI (Cancella il vecchio articolo e lo rigenera da zero)",
        "ui_fase3_select_option": "Seleziona un'opzione [1/2 o qualsiasi altro tasto per annullare]: ",
        "ui_fase3_mode_update": "🔄 Modalità AGGIORNAMENTO CHIRURGICO attivata.",
        "ui_fase3_input_flash": "✍️ Inserisci la nota flash o la variazione da apportare (orari, indisponibilità, live): ",
        "ui_fase3_mode_rewrite": "🔄 Modalità RISCRITTURA TOTALE attivata. Il vecchio file verrà rimpiazzato.",
        "ui_fase3_cancelled_msg": "🛑 Operazione annullata.",
        "ui_multiline_confirm": "👉 Incolla il testo sotto. Al termine, premi INVIO due volte (lascia una riga vuota) per confermare.",
        "ui_title_multiline_help": "👉 Puoi usare più linee. Premi INVIO due volte su una riga vuota per confermare:",
        "ui_saving_draft": "\n💾 Salvataggio dello stato attuale dell'articolo nel file bozza locale...",
        "ui_processing_surgical": "\n🔄 Elaborazione degli aggiornamenti editoriali chirurgici localizzati (Salvataggio payload token)...",
        "ui_production_links": "\n🌐 LINK DI PRODUZIONE CLICCABILI:",
        "ui_google_prettylinks": "\n✨ PRETTYLINKS GOOGLE SEARCH CONSOLE (OTTIMIZZATI SEO):",
        "ui_stato4_header": "====================================================================\n📋 [STATO 4 - SINTESI] GUIDA DI ORIENTAMENTO EDITORIALE\n====================================================================",
        "ui_stato4_match": "⚽ PARTITA: {} vs {}",
        "ui_stato4_time": "⏰ ORARIO DETTAGLIO: {}   📅 DATA EVENTO: {} ({})",
        "ui_stato4_venue": "🏟️ LUOGO EVENTO: {} ({})",
        "ui_stato4_context": "ℹ️ AMBITO CONTESTO: {}",
        "ui_stato4_dossier_title": "====================================================================\n📝 DOSSIER INFORMATIVO DETTAGLIATO (FORMAZIONI PROBABILI & NEWS):",
        "ui_stato4_footer": "====================================================================\n",
        "ui_link_it": "🇮🇹 Italian:  ",
        "ui_link_en": "🇬🇧 English:  ",
        "ui_link_es": "🇪🇸 Spanish:  ",
        "ui_link_fr": "🇫🇷 French:   ",
        "ui_link_rss": "📡 RSS Feed:  ",
        "ui_pretty_it": "🇮🇹 IT: ",
        "ui_pretty_en": "🇬🇧 EN: ",
        "ui_pretty_es": "🇪🇸 ES: ",
        "ui_pretty_fr": "🇫🇷 FR: ",
        "ui_env_read_error": "⚠️ Errore lettura file .env: {}",
        "ui_config_incomplete": "❌ Errore: Configurazione incompleta.",
        "ui_config_env_instructions": "Assicurati di aver impostato GEMINI_API_KEY nell'ambiente o nei secrets.",
        "ui_port_fallback": "⚠️ Fallback bypass porta {} innescato: {}",
        "ui_ai_escalation": "⚠️ [SCALATA IA] {} è temporaneamente saturo (Stato {}).",
        "ui_ai_trying_fallback": "Tentativo con il motore fallback successivo...",
        "ui_api_debug": "⚠️ [DEBUG API] {} ha risposto con Stato {}: {}",
        "ui_pool_saturated": "🕒 [POOL SATURO] Tutti i modelli Gemini sono occupati. Attesa di {} secondi prima di ritentare...",
        "ui_attempting_rest": "🤖 Tentativo generazione REST con modello: {}...",
        "ui_api_error_model": "⚠️ Errore API su {} (Stato {})",
        "ui_connection_failure": "⚠️ Errore connessione con modello {}: {}",
        "ui_waiting_cycle": "🕒 Attesa di {} secondi prima di rinnovare il ciclo...",
        "ui_websub_success": "✅ [WebSub] Notifica di indicizzazione inviata a Googlebot!",
        "ui_websub_anomalous": "⚠️ [WebSub] Risposta anomala dall'hub (Stato {})",
        "ui_websub_error": "❌ Impossibile connettersi con l'Hub WebSub: {}",
        "ui_hunter_warmup": "🔄 [WARMUP HUNTER] Scansione geopolitica del web per isolare la competizione di cartello...",
        "ui_context_found": "🏆 [CONTESTO TROVATO] Torneo di cartello isolato: '{}'",
        "ui_cognitive_prediction": "🔮 [PREVISIONE COGNITIVA] Calcolo parametri Slot d'Oro per timing strategico...",
        "ui_targeted_discovery": "🔍 [TARGETED DISCOVERY] Parametri query mirati per: '{}' alla data target {}...",
        "ui_no_raw_data": "⚠️ Nessun dato grezzo estratto dal web per questa data specifica.",
        "ui_cognitive_parsing": "🧠 [PARSING COGNITIVO] Analisi e modellazione dei record strutturati...",
        "ui_stato3_extraction": "🎯 [STATO 3 - ESTRAZIONE MIRATA] Costruzione blueprint tattico per: {} vs {}...",
        "ui_vision_none": "Nessuna (File non trovato)",
        "ui_vision_init": "\n👁️  [MOTORE VISION] Inizializzazione analisi fotogramma multimodale con Gemini...",
        "ui_vision_output": "📸 OUTPUT ANALISI SCANSIONE IMMAGINE:\n{}",
        "ui_vision_breakdown": "Errore durante analisi vision: {}",
        "ui_vision_unavailable": "Motore Vision temporaneamente non disponibile.",
        "ui_null_input": "❌ Campo input vuoto. Processo interrotto.",
        "ui_cover_name_empty": "⚠️ Errore: Il nome file non può essere vuoto. Specifica la sintassi corretta.",
        "ui_no_cover_data": "Nessun dato analitico sull'immagine di copertina.",
        "ui_no_remote_data": "Nessun dato remoto riscontrato.",
        "ui_editorial_postmatch_note": "\n\n[NOTA EDITORIALE: Match terminato. NON usare il blocco formazioni. Concentrati esclusivamente su cronaca e statistiche finali.]",
        "ui_context_postmatch": "Revisione Post-Match Ufficiale ({})",
        "ui_context_prematch": "Match Ufficiale Pre-Partita ({})",
        "ui_dispatch_inputs_loaded": "📥 [INPUT DISPATCH] Parametri letti con successo dal trigger della console.",
        "ui_automated_execution": "🤖 Esecuzione automatizzata headless innescata."
    },
    "es": {
        "locale": "es_ES",
        "label_by": "Por",
        "label_published": "Publicado",
        "label_updated": "Actualizado",
        "nav_home": "Inicio",
        "nav_matches": "Partidos",
        "nav_market": "Mercato",
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
    """i18n lookup function complying strictly with Zero-Hardcoded Texts Rule."""
    return I18N_DICTIONARY.get(CURRENT_LANG, I18N_DICTIONARY["it"]).get(chiave, chiave)

# ==============================================================================
# API KEY CONFIGURATION FROM ENV OR SECRETS
# ==============================================================================
API_KEY = os.environ.get("GEMINI_API_KEY")
ENV_PATH = os.path.join(PROJECT_DIR, ".env") if os.path.exists(os.path.join(PROJECT_DIR, ".env")) else os.path.join(BASE_DIR, ".env")

if not API_KEY and os.path.exists(ENV_PATH):
    try:
        with open(ENV_PATH, "r") as f:
            for line in f:
                if line.strip().startswith("GEMINI_API_KEY"):
                    API_KEY = line.split("=")[1].strip().replace('"', '').replace("'", "")
    except Exception as e:
        print(t("ui_env_read_error").format(e))

if not API_KEY:
    print(t("ui_config_incomplete"))
    print(t("ui_config_env_instructions"))
    sys.exit(1)

AI_MODELS_POOL = ["gemini-3.6-flash", "gemini-3.7-flash", "gemini-flash-latest"]

# ==============================================================================
# REST COGNITIVE CORES & MODEL FAILOVER HANDLING
# ==============================================================================
def chiedi_raw_ai(prompt_sistema, prompt_utente, usa_search=False):
    """Executes a native REST HTTP call to Gemini models with Google Search Grounding support."""
    pool_modelli = AI_MODELS_POOL
    attesa_saturazione = 15
    while True:
        for modello_nome in pool_modelli:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{modello_nome}:generateContent?key={API_KEY}"
                headers = {"Content-Type": "application/json"}

                payload = {
                    "contents": [{"parts": [{"text": prompt_utente}]}]
                }

                if prompt_sistema:
                    payload["systemInstruction"] = {"parts": [{"text": prompt_sistema}]}

                if usa_search:
                    payload["tools"] = [{"googleSearch": {}}]

                response = requests.post(url, headers=headers, json=payload, timeout=30)

                if response.status_code == 200:
                    return response.json()['candidates'][0]['content']['parts'][0]['text']

                elif response.status_code in [503, 429]:
                    print(t("ui_ai_escalation").format(modello_nome, response.status_code))
                    time.sleep(3)
                    print(t("ui_ai_trying_fallback"))
                    continue
                else:
                    print(t("ui_api_debug").format(modello_nome, response.status_code, response.text))
                    continue
            except Exception:
                continue

        print(t("ui_pool_saturated").format(attesa_saturazione))
        time.sleep(attesa_saturazione)
        attesa_saturazione = min(attesa_saturazione * 2, 120)


def genera_con_scalo_ai(prompt_sistema, prompt_utente):
    """Executes multilingual structured JSON object generation using strict object schemas."""
    tentativi_totali = 0
    mentre_attendi = 15

    while True:
        for modello_nome in AI_MODELS_POOL:
            try:
                print(t("ui_attempting_rest").format(modello_nome))
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
                        }
                    }
                }

                response = requests.post(url, headers=headers, json=payload, timeout=60)
                if response.status_code == 200:
                    res_json = response.json()
                    return res_json['candidates'][0]['content']['parts'][0]['text']
                else:
                    print(t("ui_api_error_model").format(modello_nome, response.status_code))
                    time.sleep(2)
            except Exception as e:
                print(t("ui_connection_failure").format(modello_nome, e))
                time.sleep(2)

        tentativi_totali += 1
        print(t("ui_waiting_cycle").format(mentre_attendi))
        time.sleep(mentre_attendi)
        mentre_attendi = min(mentre_attendi * 2, 120)

# ==============================================================================
# BASE HTML LAYOUT TEMPLATE (COMPLETO CON WIDGET TATTICO 3D, CARD E ZHTR)
# ==============================================================================
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="{LANG}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{TITOLO_PAGINA} | {LABEL_META_JOURNAL}</title>
    <link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
    <meta name="robots" content="max-image-preview:large">
    <link rel="canonical" href="https://championsreport.editories.com/articles/{SLUG}/{LANG}.html" />
    <meta property="og:locale" content="{LANG_LOCALE}" />
    <meta property="og:type" content="article" />
    <meta property="og:title" content="{TITOLO_PAGINA} | {LABEL_META_JOURNAL}" />
    <meta property="og:description" content="{META_DESCRIPTION}" />
    <meta property="og:url" content="https://championsreport.editories.com/articles/{SLUG}/{LANG}.html" />
    <meta property="og:site_name" content="{LABEL_META_JOURNAL}" />
    <meta property="og:image" content="https://championsreport.editories.com/assets/{IMMAGINE_FILE}" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="675" />
    <style>
        :root {{
            --primary-blue: #0044ff;
            --hover-blue: #0033cc;
            --bg-light: #f8f9fa;
            --text-dark: #333;
        }}

        * {{ box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background-color: var(--bg-light); color: var(--text-dark); margin: 0; padding: 0; }}

        /* HEADER E LOGO 3D */
        header {{ background: #fff; padding: 30px 0 20px 0; text-align: center; border-bottom: 1px solid #eee; position: relative; }}
        .header-container {{ max-width: 600px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; gap: 15px; position: relative; }}

        .main-title-3d {{
            font-family: 'Dancing Script', cursive;
            font-weight: 700;
            font-size: 3.8rem;
            color: #0044ff;
            display: inline-block;
            letter-spacing: 2px;
            margin: 0;
            -webkit-text-stroke: 1.2px #93c5fd;
            text-shadow:
                1px 1px 0px #0033cc,
                2px 2px 0px #0022aa,
                3px 3px 0px #001188,
                4px 4px 5px rgba(0, 17, 136, 0.4),
                5px 5px 10px rgba(0, 0, 0, 0.15);
        }}

        /* SELETTORE LINGUA */
        .lang-selector {{ position: absolute; top: 10px; right: 20px; font-size: 0.85rem; }}
        .lang-selector select {{ padding: 4px 8px; border-radius: 6px; border: 1px solid #ccc; font-family: 'Inter', sans-serif; cursor: pointer; }}

        /* NAVIGAZIONE */
        nav {{ display: flex; justify-content: center; gap: 20px; padding: 15px; background: #fff; border-bottom: 1px solid #eee; }}
        nav a {{ text-decoration: none; color: #555; font-weight: 400; font-size: 0.9rem; transition: color 0.2s; }}
        nav a:hover {{ color: var(--primary-blue); }}

        /* CONTENITORE CENTRALE */
        .container {{ max-width: 600px; margin: 20px auto; padding: 20px; background: #fff; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
        h1 {{ font-weight: 600; color: #111; line-height: 1.2; font-size: 1.8rem; margin-top: 10px; }}
        h2 {{ font-weight: 400; color: #222; font-size: 1.4rem; }}
        .subtitle {{ color: #666; font-size: 0.95rem; margin-top: -5px; margin-bottom: 20px; }}
        .content {{ font-size: 1.1rem; line-height: 1.7; color: #444; }}
        .cover-hero {{ width: 100%; height: auto; border-radius: 8px; margin: 15px 0; object-fit: cover; }}

        /* MONETIZZAZIONE ADSTERRA SLOTS */
        .ad-slot {{ margin: 25px 0; text-align: center; min-height: 50px; }}
        .btn-cta {{ display: block; background: var(--primary-blue); color: #fff; text-align: center; padding: 15px; border-radius: 8px; text-decoration: none; font-weight: bold; margin: 25px 0; transition: background 0.2s; }}
        .btn-cta:hover {{ background: var(--hover-blue); }}

        /* STRUTTURA CARD ARTICOLI RECENTI */
        .card {{ border-bottom: 1px solid #eee; padding: 15px 0; display: flex; gap: 15px; align-items: center; }}
        .card:last-child {{ border-bottom: none; }}
        .card img {{ width: 120px; height: 80px; border-radius: 6px; object-fit: cover; }}
        .card-title {{ font-size: 1.1rem; font-weight: 600; color: #111; text-decoration: none; transition: color 0.2s; }}
        .card-title:hover {{ color: var(--primary-blue); }}

        /* WIDGET LIVE ED ELEMENTI DEL CAMPO TATTICO 3D */
        .pitch-container {{ perspective: 800px; width: 100%; margin: 30px 0; display: flex; justify-content: center; }}
        .pitch {{ width: 100%; max-width: 500px; height: 350px; background: linear-gradient(180deg, #1b6613 0%, #298c1c 100%); border: 3px solid #fff; box-shadow: 0 20px 40px rgba(0,0,0,0.25); transform: rotateX(25deg); position: relative; overflow: hidden; border-radius: 4px; }}
        .pitch-lines {{ position: absolute; width: 100%; height: 2px; background: rgba(255,255,255,0.6); top: 50%; transform: translateY(-50%); }}
        .center-circle {{ position: absolute; width: 90px; height: 90px; border: 2px solid rgba(255,255,255,0.6); border-radius: 50%; top: 50%; left: 50%; transform: translate(-50%, -50%); }}
        .player-node {{ position: absolute; width: 16px; height: 16px; border-radius: 50%; transform: translate(-50%, -50%); box-shadow: 0 4px 6px rgba(0,0,0,0.3); cursor: pointer; transition: all 0.2s ease; z-index: 10; }}
        .player-node:hover {{ width: 22px; height: 22px; z-index: 20; }}
        .team-home {{ background: #ff3b30; border: 2px solid #fff; }}
        .team-away {{ background: #007aff; border: 2px solid #fff; }}
        .player-tooltip {{ visibility: hidden; background-color: rgba(0, 0, 0, 0.85); color: #fff; text-align: center; padding: 6px 10px; border-radius: 6px; position: absolute; bottom: 130%; left: 50%; transform: translateX(-50%); white-space: nowrap; font-size: 0.75rem; box-shadow: 0 4px 8px rgba(0,0,0,0.2); opacity: 0; transition: opacity 0.2s; font-family: 'Inter', sans-serif; pointer-events: none; }}
        .player-node:hover .player-tooltip {{ visibility: visible; opacity: 1; }}

        /* BOX FORMAZIONI TATTICHE */
        .lineups {{ background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 20px; margin: 20px 0; font-size: 0.95rem; }}
        .lineups p {{ text-align: left; margin-bottom: 8px; line-height: 1.5; }}
        .lineups strong {{ color: #1a202c; }}
        .coach {{ margin-top: 8px; font-style: italic; color: #4a5568; display: block; }}
        .meta-box {{ font-size: 0.85rem; color: #666; margin: 0 0 20px 0; display: flex; flex-wrap: wrap; gap: 12px; border-bottom: 1px solid #eee; padding-bottom: 12px; }}
        .meta-box strong {{ color: #2d3748; font-weight: 600; }}
        h3 {{ font-weight: 600; color: #2d3748; font-size: 1.3rem; margin-top: 25px; margin-bottom: 12px; border-left: 4px solid var(--primary-blue); padding-left: 10px; text-align: justify; }}
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
            <h1 class="main-title-3d">{LABEL_META_JOURNAL}</h1>
        </div>
    </header>
    <nav>
        <a href="/{LANG}/index.html">{NAV_HOME}</a>
        <a href="/{LANG}/partite.html">{NAV_MATCHES}</a>
        <a href="/{LANG}/mercato.html">{NAV_MARKET}</a>
        <a href="/{LANG}/live.html">{NAV_LIVE}</a>
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
<rss version="2.0" xmlns:atom="https://www.w3.org/2005/Atom">
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

    try:
        y_iso, m_iso, d_iso = map(int, dati_partita["data_iso"].split("-"))
    except Exception:
        y_iso, m_iso, d_iso = datetime.now().year, datetime.now().month, datetime.now().day

    mesi_it = ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
    mesi_en = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    mesi_es = ["", "de enero", "de febrero", "de marzo", "de abril", "de mayo", "de junio", "de julio", "de agosto", "de septiembre", "de ottobre", "de noviembre", "de diciembre"]
    mesi_fr = ["", "janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

    for lang in ["it", "en", "es", "fr"]:
        lang_key = lang if lang in I18N_DICTIONARY else "en"
        info = I18N_DICTIONARY[lang_key]

        if lang == "it":
            data_localizzata = f"{d_iso} {mesi_it[m_iso]} {y_iso}"
        elif lang == "es":
            data_localizzata = f"{d_iso} {mesi_es[m_iso]} {y_iso}"
        elif lang == "fr":
            data_localizzata = f"{d_iso} {mesi_fr[m_iso]} {y_iso}"
        else:
            data_localizzata = f"{mesi_en[m_iso]} {d_iso}, {y_iso}" 

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
            DATA_TESTUALE=data_localizzata,
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
    feed_url = f"[https://championsreport.editories.com/articles/](https://championsreport.editories.com/articles/){slug}/feed.xml"
    hub_url = "[https://pubsubhubbub.appspot.com/](https://pubsubhubbub.appspot.com/)"
    try:
        r = requests.post(hub_url, data={"hub.mode": "publish", "hub.url": feed_url}, timeout=10)
        if r.status_code in [200, 204]:
            print(t("ui_websub_success"))
        else:
            print(t("ui_websub_anomalous").format(r.status_code))
    except Exception as e:
        print(t("ui_websub_error").format(e))

# ==============================================================================
# INTERNATIONAL SLUG ALGORITHM GENERATION (SEO CLEAN)
# ==============================================================================
def genera_slug_internazionale_ai(squadra_a, squadra_b, competizione, anno):
    """Translates team names to English on the fly and generates structural international slugs."""
    prompt_slug = f"""Traduci i nomi di queste due squadre di calcio in lingua inglese (es: 'Spagna' diventa 'Spain', 'Stati Uniti' diventa 'USA').
    Restituisci esclusivamente una stringa in minuscolo con le due squadre in inglese separate da un trattino, seguite da un trattino e il nome della competizione compresso senza spaces and l'anno.
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

def estrai_dati_tecnici_ai(squadra_a, squadra_b, anno_corrente):
    """Stato 3: Pulls down probable setups, tactical news, and team conditions."""
    print(t("ui_stato3_extraction").format(squadra_a, squadra_b))
    prompt_sistema = "Sei un analista tattico della redazione sportiva. Generi report tecnici sulle squadre."
    prompt_utente = f"Generate an updated detailed technical scouting dossier for the match {squadra_a} vs {squadra_b} within the tournament context of the year {anno_corrente}. Tightly extract expected probable lineups, open tactical doubts, full injured/suspended players lists, and current team form metrics. The entire output blueprint MUST be written strictly in English."
    return chiedi_raw_ai(prompt_sistema, prompt_utente, usa_search=False)

def genera_guida(match_info, dossier_tecnico):
    """Stato 4: Formats a synthesis layout wrapper to guide localized copywriters."""
    header = t("ui_stato4_header")
    match_str = t("ui_stato4_match").format(match_info['squadra_a'], match_info['squadra_b'])
    time_str = t("ui_stato4_time").format(match_info.get('ora', '20:45 CEST'), match_info.get('data_testo', ''), match_info.get('data_iso', ''))
    venue_str = t("ui_stato4_venue").format(match_info.get('stadio', 'MetLife Stadium'), match_info.get('citta', 'New York'))
    context_str = t("ui_stato4_context").format(match_info.get('dati_contesto', 'Official fixture.'))
    dossier_title = t("ui_stato4_dossier_title")
    footer = t("ui_stato4_footer")
    
    linee = [
        "",
        header,
        match_str,
        time_str,
        venue_str,
        context_str,
        dossier_title,
        dossier_tecnico,
        footer
    ]
    return "\n".join(linee)

# ==============================================================================
# MAIN BACKEND PIPELINE EXECUTION BLOCK (GITHUB ACTIONS HEADLESS / DISPATCH)
# ==============================================================================
if __name__ == "__main__":
    try:
        print("====================================================================")
        print(t("ui_welcome"))
        print("====================================================================")

        data_corrente = datetime.now()
        anno_corrente = data_corrente.year

        # Lettura parametri inviati dalla Console via GitHub Actions Dispatch
        query_comp = os.environ.get("INPUT_COMPETITION") or "FIFA World Cup 2026"
        squadra_a = os.environ.get("INPUT_SQUADRA_A") or "Spagna"
        squadra_b = os.environ.get("INPUT_SQUADRA_B") or "Austria"
        ora_match = os.environ.get("INPUT_ORARIO") or "21:00 CEST"
        stadio_match = os.environ.get("INPUT_STADIO") or "MetLife Stadium"
        citta_match = os.environ.get("INPUT_CITTA") or "New York"
        titolo_custom = os.environ.get("INPUT_CUSTOM_TITLE", "").strip()
        guidelines_utente = os.environ.get("INPUT_GUIDELINES", "").strip()
        opzione_foto = os.environ.get("INPUT_OPZIONE_FOTO", "1")
        photo_author = os.environ.get("INPUT_PHOTO_AUTHOR", "").strip()
        photo_author_link = os.environ.get("INPUT_PHOTO_AUTHOR_LINK", "").strip()
        photo_license = os.environ.get("INPUT_PHOTO_LICENSE", "").strip()
        photo_license_link = os.environ.get("INPUT_PHOTO_LICENSE_LINK", "").strip()
        caption_guideline = os.environ.get("INPUT_CAPTION_GUIDELINE", "").strip()

        print(t("ui_dispatch_inputs_loaded"))
        print(t("ui_automated_execution"))

        target_date = data_corrente
        iso_giorno = target_date.strftime("%Y-%m-%d")

        partita_iniziata_o_terminata = False
        try:
            ora_pulita = ora_match.split()[0]
            ore_m, min_m = map(int, ora_pulita.split(":"))
            ora_match_dt = target_date.replace(hour=ore_m, minute=min_m, second=0, microsecond=0)
            if datetime.now() > ora_match_dt:
                partita_iniziata_o_terminata = True
        except Exception:
            pass

        slug_articolo = genera_slug_internazionale_ai(squadra_a, squadra_b, query_comp, anno_corrente)

        match_selezionato = {
            "id": "1",
            "squadra_a": squadra_a,
            "squadra_b": squadra_b,
            "ora": ora_match,
            "data_iso": iso_giorno,
            "data_testo": target_date.strftime("%B %d, %Y").strip(),
            "stadio": stadio_match,
            "citta": citta_match,
            "partita_iniziata_o_terminata": partita_iniziata_o_terminata
        }

        scelta_modalita = "2" if partita_iniziata_o_terminata else "1"
        if scelta_modalita == "1":
            print(t("ui_fase2_pre_match"))
        else:
            print(t("ui_fase2_post_match"))

        # FASE 4: Dossier e Blueprint
        dossier = estrai_dati_tecnici_ai(match_selezionato["squadra_a"], match_selezionato["squadra_b"], anno_corrente)
        if scelta_modalita == "2":
            dossier += t("ui_editorial_postmatch_note")

        match_selezionato["dossier_match"] = dossier
        match_selezionato["dati_contesto"] = t("ui_context_postmatch").format(query_comp) if scelta_modalita == "2" else t("ui_context_prematch").format(query_comp)

        testo_guida = genera_guida(match_selezionato, match_selezionato["dossier_match"])
        print(testo_guida)

        # Gestione immagine di copertina
        nome_foto_finalizzata = "logo.png"
        didascalia_istruzione = ""

        if opzione_foto == "2":
            nome_foto_finalizzata = f"{slug_articolo}.jpg"
            author_html = f'<a href="{photo_author_link}" target="_blank" rel="noopener noreferrer">{photo_author}</a>' if photo_author_link else photo_author
            license_html = f'<a href="{photo_license_link}" target="_blank" rel="noopener noreferrer">{photo_license}</a>' if photo_license_link else photo_license
            crediti = f" (Foto di {author_html} / {license_html})" if photo_author else ""
            if caption_guideline:
                didascalia_istruzione = f"Usa questa didascalia: '{caption_guideline}'. Appendi: '{crediti}'."
            else:
                didascalia_istruzione = f"Genera una didascalia giornalistica d'alto livello. Appendi: '{crediti}'."
        elif opzione_foto == "3" and guidelines_utente.startswith("http"):
            nome_foto_finalizzata = guidelines_utente.strip()

        match_selezionato["immagine_copertina"] = nome_foto_finalizzata

        prompt_completo_ai = f"""Sviluppa l'articolo giornalistico sportivo multilingua seguendo fedelmente queste linee guida ed informazioni reali riscontrate:
- Incontro: {match_selezionato['squadra_a']} vs {match_selezionato['squadra_b']}
- Data e Ora: {match_selezionato['data_testo']} alle ore {match_selezionato['ora']}
- Stadio: {match_selezionato['stadio']}

DOSSIER INFORMATIVO ESTRATTO IN TEMPO REALE DA PROCESSARE:
{match_selezionato.get('dossier_match', t('ui_no_remote_data'))}

Direttive ed Espansioni fornite dal Redattore:
{guidelines_utente}
"""
        if didascalia_istruzione:
            prompt_completo_ai += f"\n- Istruzione Redazionale Didascalia Foto: {didascalia_istruzione}. Traducila in tutte e 4 le lingue."
        if titolo_custom:
            prompt_completo_ai += f"\n- Vincolo Titolo Italiano: Devi usare tassativamente questo titolo: '{titolo_custom}'. Traducilo in modo coerente e vario for le altre tre lingue."

        print(t("ui_engine_start"))
        raw_ai_output = genera_con_scalo_ai(PROMPT_SISTEMA_EDITORIALE, prompt_completo_ai)

        clean_json_str = raw_ai_output.strip().replace("```json", "").replace("```", "")
        dati_generati_json = json.loads(clean_json_str)

        compila_file_finali(slug_articolo, match_selezionato, dati_generati_json, ora_match.split()[0])

        print(f"{t('ui_saved_path')}{os.path.join(ARTICLES_OUTPUT_DIR, slug_articolo)}/")
        print(f"{t('ui_generated_title')}{dati_generati_json['it']['titolo']}")
        print(t("ui_production_links"))
        print(f"{t('ui_link_it')}[https://championsreport.editories.com/articles/](https://championsreport.editories.com/articles/){slug_articolo}/it.html")
        print(f"{t('ui_link_en')}[https://championsreport.editories.com/articles/](https://championsreport.editories.com/articles/){slug_articolo}/en.html")
        print(f"{t('ui_link_es')}[https://championsreport.editories.com/articles/](https://championsreport.editories.com/articles/){slug_articolo}/es.html")
        print(f"{t('ui_link_fr')}[https://championsreport.editories.com/articles/](https://championsreport.editories.com/articles/){slug_articolo}/fr.html")
        print(f"{t('ui_link_rss')}[https://championsreport.editories.com/articles/](https://championsreport.editories.com/articles/){slug_articolo}/feed.xml")
        print(t("ui_google_prettylinks"))
        print(f"{t('ui_pretty_it')}[https://championsreport.editories.com/articles/](https://championsreport.editories.com/articles/){slug_articolo}/it")
        print(f"{t('ui_pretty_en')}[https://championsreport.editories.com/articles/](https://championsreport.editories.com/articles/){slug_articolo}/en")
        print(f"{t('ui_pretty_es')}[https://championsreport.editories.com/articles/](https://championsreport.editories.com/articles/){slug_articolo}/es")
        print(f"{t('ui_pretty_fr')}[https://championsreport.editories.com/articles/](https://championsreport.editories.com/articles/){slug_articolo}/fr\n")

        print(t("ui_pinging"))
        esegui_ping_websub(slug_articolo)
        print(t("ui_success_finish"))

    except KeyboardInterrupt:
        print(t("ui_shutdown_clean"))
        sys.exit(0)
    except Exception as e:
        print(f"{t('ui_template_error')}{e}")
        sys.exit(1)