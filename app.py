import streamlit as st
import time
import requests
import datetime
import json
import os
import base64
import pandas as pd
from google import genai
import google.auth
from googleapiclient.discovery import build

# =====================================================================
# 0. DIZIONARIO DI TRADUZIONE DINAMICA (i18n) - SOLO INTERFACCIA BACKEND
# =====================================================================
LANGUAGES = {
    "it": {
        "app_title": "Champion's Report",
        "tab_editorial": "📑 Macchina Editoriale",
        "tab_archive": "⏳ Archivio & Scheduler",
        "tab_finance": "📈 Performance & Ricevute",
        "tab_config": "⚙️ Config & Batch",
        "login_lbl": "Inserisci la password amministratore per accedere",
        "login_btn": "Accedi alla Console",
        "login_error": "🚨 Password errata. Accesso negato.",
        "engine_warning": "⚠️ Modello {} saturo o non disponibile. Scalo in corso...",
        "engine_error": "🚨 Tutti i server Gemini sono temporaneamente occupati. Pausa di sbollentamento di 10 secondi...",
        "editor_title": "🚀 Generatore Articoli Lampo",
        "editor_info": "Pronto per ricevere i dati delle partite dei Mondiali o i trend di Calciomercato.",
        "archive_title": "📦 Gestione Bozze e Modifica Contenuti",
        "archive_info": "I tuoi blocchi statici compariranno qui per essere revisionati e corretti prima dell'invio.",
        "finance_title": "💰 Centrale Finanziaria & Analytics Live",
        "finance_section_ledger": "📑 Registro Ricevute e Pagamenti manuali",
        "finance_section_stats": "📊 Statistiche Traffico e Tracciamento Clic Real-Time",
        "finance_lbl_network": "Network Pubblicitario / Fonte",
        "finance_lbl_amount": "Importo Ricevuto ($ / €)",
        "finance_lbl_status": "Stato del Pagamento",
        "finance_status_paid": "Incassato",
        "finance_status_pending": "In Attesa (Pending)",
        "finance_btn_save": "💾 Registra Ricevuta",
        "finance_success_save": "Ricevuta contabile salvata con successo!",
        "finance_no_data": "Nessuna ricevuta registrata nel database CSV locale.",
        "finance_metric_views": "Visualizzazioni totali (Ad Network)",
        "finance_metric_clicks": "Clic Totali Rilevati",
        "finance_metric_cpm": "CPM Medio Generato",
        "finance_metric_balance": "Totale Incassato CSV",
        "finance_api_error": "❌ Chiave Adsterra non valida o non attiva.",
        "finance_analytics_ready": "🔗 Dashboard Analitica di RFL7 Center sincronizzata.",
        "finance_analytics_waiting": "ℹ️ In attesa di configurazione URL Analytics nei Secrets.",
        "config_title": "⚡ Automazioni di Gruppo e Chiavi",
        "config_info": "Pannello tecnico per le pubblicazioni batch del tabellone e aggiornamenti rapidi.",
        "scheduler_section": "🕒 Programmazione Post (Scheduler)",
        "scheduler_date": "Seleziona Data di Pubblicazione",
        "scheduler_time": "Seleziona Ora di Pubblicazione",
        "scheduler_btn": "Pianifica Articolo",
        "scheduler_success": "Articolo pianificato con successo per il {} alle {}!",
        "batch_section": "📦 Elaborazione Massiva (Batch)",
        "batch_label": "Incolla la lista dei match o dei temi (uno per riga)",
        "batch_placeholder": "Esempio:\nJuventus vs Inter\nReal Madrid vs Barcellona\nItalia vs Spagna",
        "batch_btn": "Avvia Generazione in Serie",
        "batch_progress": "Elaborazione articolo {} di {}...",
        "streaming_btn": "🔴 GUARDA IL MATCH IN DIRETTA QUI",
        "input_match_name": "Nome Partita / Argomento Principale",
        "input_title": "Titolo Articolo (H1)",
        "input_cover": "URL Immagine di Copertina (Hero)",
        "input_body": "Corpo dell'Articolo (HTML / Testo)",
        "btn_generate": "🪄 Genera Testo con Gemini",
        "btn_publish_all": "🚀 Pubblica su tutte le lingue",
        "success_published": "Articolo pubblicato con successo in tutte le lingue selezionate!",
        "error_published": "❌ Errore durante la pubblicazione su GitHub. Verifica i token.",
        "nav.home": "Home",
        "nav.matches": "Partite",
        "nav.market": "Mercato",
        "nav.live": "Live",
        "btn.watch_live": "GUARDA IL MATCH IN DIRETTA",
        "preview_live_title": "👁️ Anteprima Live (Come apparirà sul sito)",
        "spinner_gemini_writing": "Gemini sta analizzando e scrivendo il resoconto...",
        "spinner_lang_align": "Generazione e allineamento lingua: {}...",
        "pub_partial_warn": "Pubblicazione completata parzialmente ({} su {} lingue caricate).",
        "batch_success_toast": "✨ Batch completato con successo!",
        "indexing_success": "✅ Notifica di indicizzazione inviata a Google!",
        "indexing_failed": "⚠️ Pubblicato, ma notifica a Google fallita: {}",
        "select_language": "🌐 Lingua",
        "spinner_updating_index": "Aggiornamento Home Page dinamica su GitHub...",
        "spinner_updating_market": "Aggiornamento Indice Mercato su GitHub...",
        "spinner_updating_matches": "Generazione calendario dinamico competizioni...",
        "spinner_updating_live": "Generazione Widget Live ibrido sandwich...",
        "api_football_error": "⚠️ Impossibile recuperare i dati live. Verifica l'API Key.",
        "api_football_empty": "Nessun match in corso per la competizione attiva.",
        "recent_articles_title": "Ultimi Articoli Pubblicati",
        "competition_lbl": "Competizione Attiva / Campionato target per i Widget",
        "comp_auto": "Auto-Switch Temporale (Serie A / Mondiali 2026)"
    },
    "en": {
        "app_title": "Champion's Report",
        "tab_editorial": "📑 Editorial Engine",
        "tab_archive": "⏳ Archive & Scheduler",
        "tab_finance": "📈 Performance & Receipts",
        "tab_config": "⚙️ Config & Batch",
        "login_lbl": "Enter admin password to access the console",
        "login_btn": "Login to Console",
        "login_error": "🚨 Incorrect password. Access denied.",
        "engine_warning": "⚠️ Model {} saturated or unavailable. Scaling down...",
        "engine_error": "🚨 All Gemini servers are temporarily busy. Cooldown pause of 10 seconds...",
        "editor_title": "🚀 Flash Article Generator",
        "editor_info": "Ready to receive World Cup match data or Transfer Market trends.",
        "archive_title": "📦 Draft Management & Content Editing",
        "archive_info": "Your static blocks will appear here to be reviewed and corrected before sending.",
        "finance_title": "💰 Financial Center & Live Analytics",
        "finance_section_ledger": "📑 Manual Receipts & Payments Register",
        "finance_section_stats": "📊 Traffic Statistics & Real-Time Click Tracking",
        "finance_lbl_network": "Ad Network / Source",
        "finance_lbl_amount": "Amount Received ($ / €)",
        "finance_lbl_status": "Payment Status",
        "finance_status_paid": "Received",
        "finance_status_pending": "Pending",
        "finance_btn_save": "💾 Record Receipt",
        "finance_success_save": "Accounting receipt successfully saved!",
        "finance_no_data": "No receipts recorded in the local CSV database.",
        "finance_metric_views": "Total Impressions (Ad Network)",
        "finance_metric_clicks": "Total Clicks Detected",
        "finance_metric_cpm": "Average Global CPM",
        "finance_metric_balance": "Total Collected CSV",
        "finance_api_error": "❌ Invalid or inactive Adsterra API key.",
        "finance_analytics_ready": "🔗 RFL7 Center Analytics Dashboard synchronized.",
        "finance_analytics_waiting": "ℹ️ Waiting for Analytics URL configuration in Secrets.",
        "config_title": "⚡ Bulk Automations & Keys",
        "config_info": "Technical panel for batch publishing of brackets and quick updates.",
        "scheduler_section": "🕒 Post Scheduling (Scheduler)",
        "scheduler_date": "Select Publishing Date",
        "scheduler_time": "Select Publishing Time",
        "scheduler_btn": "Schedule Article",
        "scheduler_success": "Article successfully scheduled for {} at {}!",
        "batch_section": "📦 Bulk Processing (Batch)",
        "batch_label": "Paste the list of matches or topics (one per line)",
        "batch_placeholder": "Example:\nJuventus vs Inter\nReal Madrid vs Barcelona\nItaly vs Spain",
        "batch_btn": "Launch Bulk Generation",
        "batch_progress": "Processing article {} of {}...",
        "streaming_btn": "🔴 WATCH THE MATCH LIVE HERE",
        "input_match_name": "Match Name / Main Topic",
        "input_title": "Article Title (H1)",
        "input_cover": "Cover Image URL (Hero)",
        "input_body": "Article Body (HTML / Text)",
        "btn_generate": "🪄 Generate Content with Gemini",
        "btn_publish_all": "🚀 Publish to All Languages",
        "success_published": "Article successfully published in all selected languages!",
        "error_published": "❌ GitHub deployment failed. Check your tokens.",
        "nav.home": "Home",
        "nav.matches": "Matches",
        "nav.market": "Market",
        "nav.live": "Live",
        "btn.watch_live": "WATCH THE MATCH LIVE",
        "preview_live_title": "👁️ Live Preview (How it will look on the site)",
        "spinner_gemini_writing": "Gemini is analyzing and writing the report...",
        "spinner_lang_align": "Generating and aligning language: {}...",
        "pub_partial_warn": "Publication partially completed ({} out of {} languages uploaded).",
        "batch_success_toast": "✨ Batch completed successfully!",
        "indexing_success": "✅ Indexing notification successfully sent to Google!",
        "indexing_failed": "⚠️ Published, but Google indexing notification failed: {}",
        "select_language": "🌐 Language",
        "spinner_updating_index": "Updating dynamic Home Page on GitHub...",
        "spinner_updating_market": "Updating Market Index on GitHub...",
        "spinner_updating_matches": "Generating dynamic competitions calendar...",
        "spinner_updating_live": "Generating hybrid sandwich Live Widget...",
        "api_football_error": "⚠️ Unable to fetch live data. Check API Key.",
        "api_football_empty": "No live matches available for the active competition.",
        "recent_articles_title": "Latest Published Articles",
        "competition_lbl": "Active Competition / Target League for Leagues",
        "comp_auto": "Time Auto-Switch (Serie A / World Cup 2026)"
    },
    "es": {
        "app_title": "Champion's Report",
        "tab_editorial": "📑 Máquina Editorial",
        "tab_archive": "⏳ Archivo y Planificador",
        "tab_finance": "📈 Rendimiento y Recibos",
        "tab_config": "⚙️ Config y Batch",
        "login_lbl": "Ingrese la contraseña de administrador para acceder",
        "login_btn": "Acceder a la Consola",
        "login_error": "🚨 Contraseña incorrecta. Acceso denegado.",
        "engine_warning": "⚠️ Modelo {} saturado o no disponible. Escalamiento en curso...",
        "engine_error": "🚨 Todos los servidores de Gemini están ocupados. Pausa di enfriamiento de 10 segundos...",
        "editor_title": "🚀 Generador de Artículos Relámpago",
        "editor_info": "Listo para recibir datos de los partidos del Mundial o tendencias del Mercado de Fichajes.",
        "archive_title": "📦 Gestión de Borradores y Edición de Contenido",
        "archive_info": "Sus bloques estáticos aparecerán aquí para ser revisados y corregidos antes del envío.",
        "finance_title": "💰 Centro Financiero y Analítica en Vivo",
        "finance_section_ledger": "📑 Registro Manual de Recibos y Pagos",
        "finance_section_stats": "📊 Dasísticas de Tráfico y Seguimiento de Clics en Tiempo Real",
        "finance_lbl_network": "Red Publicitaria / Fuente",
        "finance_lbl_amount": "Monto Recibido ($ / €)",
        "finance_lbl_status": "Estado del Pago",
        "finance_status_paid": "Cobrado",
        "finance_status_pending": "Pendiente",
        "finance_btn_save": "💾 Registrar Recibo",
        "finance_success_save": "¡Recibo contable guardado con éxito!",
        "finance_no_data": "No hay recibos registrados en la base de datos CSV local.",
        "finance_metric_views": "Impresiones Totales (Ad Network)",
        "finance_metric_clicks": "Clics Totales Detectados",
        "finance_metric_cpm": "CPM Medio Global",
        "finance_metric_balance": "Total Cobrado CSV",
        "finance_api_error": "❌ Clave de API de Adsterra no válida o inactiva.",
        "finance_analytics_ready": "🔗 Panel de Analítica de RFL7 Center sincronizado.",
        "finance_analytics_waiting": "ℹ️ Esperando la configuración de la URL de Analítica en los Secrets.",
        "config_title": "⚡ Automatizaciones Masivas y Claves",
        "config_info": "Panel técnico para publicaciones por lotes de tablas de clasificación y actualizaciones rápidas.",
        "scheduler_section": "🕒 Programación de Publicaciones (Scheduler)",
        "scheduler_date": "Seleccionar Fecha de Publicación",
        "scheduler_time": "Seleccionar Hora de Publicación",
        "scheduler_btn": "Programar Artículo",
        "scheduler_success": "¡Artículo programado con éxito para el {} a las {}!",
        "batch_section": "📦 Procesamiento Masivo (Batch)",
        "batch_label": "Pegue la lista di partidos o temas (uno por línea)",
        "batch_placeholder": "Ejemplo:\nJuventus vs Inter\nReal Madrid vs Barcelona\nItaly vs Spain",
        "batch_btn": "Iniciar Generación en Serie",
        "batch_progress": "Procesando artículo {} de {}...",
        "streaming_btn": "🔴 MIRA EL PARTIDO EN DIRECTO AQUÍ",
        "input_match_name": "Nombre del Partido / Tema Principal",
        "input_title": "Título del Artículo (H1)",
        "input_cover": "URL de la Imagen de Portada (Hero)",
        "input_body": "Cuerpo del Artículo (HTML / Texto)",
        "btn_generate": "🪄 Generar Contenido con Gemini",
        "btn_publish_all": "🚀 Publicar en Todos los Idiomas",
        "success_published": "¡Artículo publicado con éxito en todos los idiomas seleccionados!",
        "error_published": "❌ Error en el desplégue de GitHub. Verifique sus tokens.",
        "nav.home": "Inicio",
        "nav.matches": "Partidos",
        "nav.market": "Mercato",
        "nav.live": "En vivo",
        "btn.watch_live": "MIRA EL PARTIDO EN DIRECTO",
        "preview_live_title": "👁️ Vista previa en vivo (Cómo se verà en el sitio)",
        "spinner_gemini_writing": "Gemini está analizando y writing el informe...",
        "spinner_lang_align": "Generando y alineando idioma: {}...",
        "pub_partial_warn": "Publicación completata parcialmente ({} de {} idiomas cargados).",
        "batch_success_toast": "✨ ¡Lote completado con éxito!",
        "indexing_success": "✅ ¡Notificación di indexación enviada a Google!",
        "indexing_failed": "⚠️ Publicado, pero falló la notificación di indexación a Google: {}",
        "select_language": "🌐 Idioma",
        "spinner_updating_index": "Actualizando Home Page dinámica en GitHub...",
        "spinner_updating_market": "Actualizando Índice de Mercado en GitHub...",
        "spinner_updating_matches": "Generando calendario dinámico de competiciones...",
        "spinner_updating_live": "Generando Widget Live híbrido sandwich...",
        "api_football_error": "⚠️ No se pudieron obtener datos en vivo. Verifique la API Key.",
        "api_football_empty": "No hay partidos en vivo disponibles para la competición activa.",
        "recent_articles_title": "Últimos Artículos Publicados",
        "competition_lbl": "Competición Activa / Liga objetivo para Widgets",
        "comp_auto": "Auto-Cambio Temporal (Serie A / Copa Mundial 2026)"
    },
    "fr": {
        "app_title": "Champion's Report",
        "tab_editorial": "📑 Machine Éditoriale",
        "tab_archive": "⏳ Archive & Planificateur",
        "tab_finance": "📈 Performance & Reçus",
        "tab_config": "⚙️ Config & Batch",
        "login_lbl": "Entrez le mot de passe administrateur pour accéder à la console",
        "login_btn": "Accéder à la Console",
        "login_error": "🚨 Mot de passe incorrect. Accès refusé.",
        "engine_warning": "⚠️ Modèle {} saturo ou indisponible. Basculement en cours...",
        "engine_error": "🚨 Tous les serveurs Gemini sont temporairement occupés. Pause de refroidissement de 10 secondes...",
        "editor_title": "🚀 Générateur d'Articles Flash",
        "editor_info": "Prêt à recevoir les données des matchs de la Coupe du Monde ou les tendances du Mercato.",
        "archive_title": "📦 Gestion des Brouillons et Modification du Contenu",
        "archive_info": "Vos blocs statiques apparaîtront ici pour être révisés et corrigés avant l'envoi.",
        "finance_title": "💰 Centre Financier & Analytics Live",
        "finance_section_ledger": "📑 Registre Manuel des Reçus et Paiements",
        "finance_section_stats": "📊 Statistiques de Trafic & Suivi des Clics en Temps Réel",
        "finance_lbl_network": "Réseau Publicitaire / Source",
        "finance_lbl_amount": "Montant Reçu ($ / €)",
        "finance_lbl_status": "Statut du Paiement",
        "finance_status_paid": "Encaissé",
        "finance_status_pending": "En attente",
        "finance_btn_save": "💾 Enregistrer le Reçu",
        "finance_success_save": "Reçu comptable enregistré avec succès !",
        "finance_no_data": "Aucun reçu enregistré dans la base de datos CSV locale.",
        "finance_metric_views": "Impressions Totales (Ad Network)",
        "finance_metric_clicks": "Total des Clics Détectés",
        "finance_metric_cpm": "CPM Moyen Global",
        "finance_metric_balance": "Total Encaissé CSV",
        "finance_api_error": "❌ Clé API Adsterra invalide ou inactive.",
        "finance_analytics_ready": "🔗 Tableau de bord Analytics de RFL7 Center synchronisé.",
        "finance_analytics_waiting": "ℹ专 En attente de la configuration de l'URL Analytics dans les Secrets.",
        "config_title": "⚡ Automatisations de Groupe & Clés",
        "config_info": "Panneau technique pour les publications de classements par lots et les mises à jour rapides.",
        "scheduler_section": "🕒 Planification des Messages (Scheduler)",
        "scheduler_date": "Sélectionner la Date de Publication",
        "scheduler_time": "Sélectionner l'Heure de Publication",
        "scheduler_btn": "Planifier l'Article",
        "scheduler_success": "Article planifié avec succès pour le {} à {}!",
        "batch_section": "📦 Traitement Massif (Batch)",
        "batch_label": "Collez la liste des matchs ou des thèmes (un par ligne)",
        "batch_placeholder": "Exemple:\nJuventus vs Inter\nReal Madrid vs Barcelone\nItalie vs Espagne",
        "batch_btn": "Lancer la Génération en Série",
        "batch_progress": "Traitement de l'article {} sur {}...",
        "streaming_btn": "🔴 REGARDEZ LE MATCH EN DIRECT ICI",
        "input_match_name": "Nom du Match / Sujet Principal",
        "input_title": "Titre de l'Article (H1)",
        "input_cover": "URL de l'Image de Couverture (Hero)",
        "input_body": "Corps de l'Article (HTML / Tout)",
        "btn_generate": "🪄 Générer le Contenu avec Gemini",
        "btn_publish_all": "🚀 Publier dans Toutes les Langues",
        "success_published": "Article publié avec succès dans toutes les langues sélectionnées!",
        "error_published": "❌ Échec du déploiement GitHub. Vérifiez vos tokens.",
        "nav.home": "Accueil",
        "nav.matches": "Matchs",
        "nav.market": "Mercato",
        "nav.live": "En direct",
        "btn.watch_live": "REGARDEZ LE MATCH EN DIRECT",
        "preview_live_title": "👁️ Aperçu en direct (À quoi cela ressemblera sur le site)",
        "spinner_gemini_writing": "Gemini analyse et écrit le rapport...",
        "spinner_lang_align": "Génération et alignement de la langue: {}...",
        "pub_partial_warn": "Publication partiellement complétée ({} sur {} langues téléchargées).",
        "batch_success_toast": "✨ Lot complété avec succès!",
        "indexing_success": "✅ Notification d'indexation envoyée avec succès à Google!",
        "indexing_failed": "⚠️ Publié, mas la notification d'indexation à Google a échoué: {}",
        "select_language": "🌐 Langue",
        "spinner_updating_index": "Mise à jour de la Home Page dynamique sur GitHub...",
        "spinner_updating_market": "Mise à jour de l'Index du Mercato sur GitHub...",
        "spinner_updating_matches": "Génération du calendrier dynamique des compétitions...",
        "spinner_updating_live": "Génération du Widget Live híbrido sandwich...",
        "api_football_error": "⚠️ Impossible de récupérer les données en direct. Vérifiez la clé API.",
        "api_football_empty": "Aucun match en direct disponible pour la compétition active.",
        "recent_articles_title": "Derniers Articles Publiés"
    }
}

if "lang" not in st.session_state:
    st.session_state.lang = "it"

def t(key):
    """Funzione di traduzione dinamica per la dashboard di amministrazione."""
    return LANGUAGES[st.session_state.lang].get(key, key)

def get_frontend_locale(target_lang):
    """Carica dinamicamente il dizionario JSON del Frontend dalla cartella locales locale di progetto."""
    try:
        base_dir = os.path.dirname(__file__)
        filepath = os.path.join(base_dir, "locales", f"{target_lang.lower()}.json")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"Errore lettura file locale frontend ({target_lang}): {e}")
    return {}

def t_lang(key, target_lang):
    """Esegue il recupero delle chiavi direttamente dal file JSON del Frontend."""
    locale_data = get_frontend_locale(target_lang)
    return locale_data.get(key, key)

def build_rendered_html_package(l_target, section_title, content_structure):
    """Fonde chirurgicamente il template master generale con la pancia della pagina e i testi dei dizionari."""
    frontend_strings = get_frontend_locale(l_target)
    
    # Costruzione dizionario di formattazione robusto contro chiavi mancanti nel JSON locale
    safe_formatting_map = {
        "t_app_title": frontend_strings.get("t_app_title", "Champion's Report"),
        "t_home": frontend_strings.get("t_home", "Home"),
        "t_matches": frontend_strings.get("t_matches", "Partite"),
        "t_market": frontend_strings.get("t_market", "Mercato"),
        "t_live": frontend_strings.get("t_live", "Live")
    }
    safe_formatting_map.update(frontend_strings)

    return TEMPLATE_HTML_MASTER.format(
        lingua=l_target,
        titolo_articolo=section_title,
        script_popunder=st.secrets.get("MONETIZATION", {}).get("ADSTERRA_POPUNDER", ""),
        script_social_bar=st.secrets.get("MONETIZATION", {}).get("ADSTERRA_SOCIAL_BAR", ""),
        sel_it='selected' if l_target == 'it' else '',
        sel_en='selected' if l_target == 'en' else '',
        sel_es='selected' if l_target == 'es' else '',
        sel_fr='selected' if l_target == 'fr' else '',
        page_content=content_structure,
        **safe_formatting_map
    )

def ping_google_indexing(url):
    """Placeholder nativo per l'invio delle notifiche a Google."""
    pass

QUEUE_FILE = "scheduler_queue.json"
FINANCE_FILE = "finance_register.csv"

# =====================================================================
# 1. CONFIGURAZIONE PAGINA E STRUTTURA GRAFICA 3D SENZA RIQUADRO
# =====================================================================
st.set_page_config(
    page_title="Champion's Report - Console Admin",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed"
)

col_lang_left, col_lang_right = st.columns([4, 1])
with col_lang_right:
    lang_choice = st.selectbox(t("select_language"), ["IT", "EN", "ES", "FR"], index=["it", "en", "es", "fr"].index(st.session_state.lang))
    st.session_state.lang = lang_choice.lower()

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400;700&family=Inter:wght@300;400;600&display=swap');

        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Inter', sans-serif;
            background-color: #f8f9fa;
        }

        h1, h2, h3 {
            font-family: 'Inter', sans-serif;
            font-weight: 300 !important;
            letter-spacing: -0.5px;
        }

        .title-container {
            text-align: center;
            margin-bottom: 40px;
            margin-top: 20px;
        }

        .main-title-3d {
            font-family: 'Dancing Script', cursive;
            font-weight: 400;
            font-size: 4.6rem;
            color: #0044ff;
            display: inline-block;
            letter-spacing: 2px;
            background: none;
            padding: 0;
            border: none;
            box-shadow: none;
            -webkit-text-stroke: 1.2px #93c5fd;
            text-shadow:
                1px 1px 0px #0033cc,
                2px 2px 0px #0022aa,
                3px 3px 0px #001188,
                4px 4px 5px rgba(0, 17, 136, 0.4),
                5px 5px 10px rgba(0, 0, 0, 0.15);
        }

        div.stButton > button:first-child {
            background-color: #0044ff;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 10px 24px;
            font-weight: 400;
            box-shadow: 0 2px 5px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
        }
        div.stButton > button:first-child:hover {
            background-color: #0033cc;
            box-shadow: 0 4px 10px rgba(0,68,255,0.2);
        }
    </style>
""", unsafe_allow_html=True)

st.markdown(f'<div class="title-container"><div class="main-title-3d">{t("app_title")}</div></div>', unsafe_allow_html=True)

# =====================================================================
# MURO DI SICUREZZA INIZIALE (LOGIN ATTIVO VIA APP_PASSWORD)
# =====================================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    with st.form("login_form"):
        st.markdown(f"<h5>{t('login_lbl')}</h5>", unsafe_allow_html=True)
        password_input = st.text_input("Password", type="password", label_visibility="collapsed")
        submit_login = st.form_submit_button(t("login_btn"))

        if submit_login:
            if password_input == st.secrets.get("APP_PASSWORD", ""):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error(t("login_error"))
    st.stop()

# =====================================================================
# 2. MOTORE GENERATIVO CICLICO (NUOVO SDK GOOGLE.GENAI)
# =====================================================================
def genera_testo_gemini_ciclico(prompt_sistema, prompt_utente):
    modelli_fallback = ["gemini-3.5-flash", "gemini-2.5-flash", "gemini-2.5-flash-latest"]
    indice = 0
    tentativi = 0
    max_tentativi = 6

    while tentativi < max_tentativi:
        modello_corrente = modelli_fallback[indice]
        try:
            client = genai.Client(api_key=st.secrets["APIS"]["GEMINI_API_KEY"])
            response = client.models.generate_content(
                model=modello_corrente,
                contents=prompt_utente,
                config={"system_instruction": prompt_sistema}
            )
            return response.text
        except Exception as e:
            print(f"--- ERRORE REAL-TIME GEMINI ({modello_corrente}): {str(e)} ---")
            st.warning(t("engine_warning").format(modello_corrente))
            tentativi += 1
            indice = (indice + 1) % len(modelli_fallback)

            if tentativi % len(modelli_fallback) == 0:
                st.error(t("engine_error"))
                time.sleep(5)
            else:
                time.sleep(2)

    return f"Errore di generation dopo {max_tentativi} tentativi."

# =====================================================================
# 3. TEMPLATE STRUTTURALI RIGIDI PER NETWORK AUTOMATICO MULTIPAGINA
# =====================================================================
TEMPLATE_HTML_MASTER = """<!DOCTYPE html>
<html lang="{lingua}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titolo_articolo} | {t_app_title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary-blue: #0044ff;
            --hover-blue: #0033cc;
            --bg-light: #f8f9fa;
            --text-dark: #333;
        }}

        * {{ box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background-color: var(--bg-light); color: var(--text-dark); margin: 0; padding: 0; }}
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

        .lang-selector {{ position: absolute; top: 10px; right: 20px; font-size: 0.85rem; }}
        .lang-selector select {{ padding: 4px 8px; border-radius: 6px; border: 1px solid #ccc; font-family: 'Inter', sans-serif; cursor: pointer; }}
        nav {{ display: flex; justify-content: center; gap: 20px; padding: 15px; background: #fff; border-bottom: 1px solid #eee; }}
        nav a {{ text-decoration: none; color: #555; font-weight: 400; font-size: 0.9rem; transition: color 0.2s; }}
        nav a:hover {{ color: var(--primary-blue); }}

        .container {{ max-width: 600px; margin: 20px auto; padding: 20px; background: #fff; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
        h1 {{ font-weight: 600; color: #111; line-height: 1.2; font-size: 1.8rem; margin-top: 10px; }}
        h2 {{ font-weight: 400; color: #222; font-size: 1.4rem; }}
        .subtitle {{ color: #666; font-size: 0.95rem; margin-top: -5px; margin-bottom: 20px; }}
        .content {{ font-size: 1.1rem; line-height: 1.7; color: #444; }}
        .cover-hero {{ width: 100%; height: auto; border-radius: 8px; margin: 15px 0; object-fit: cover; }}

        .ad-slot {{ margin: 25px 0; text-align: center; min-height: 50px; }}
        .btn-cta {{ display: block; background: var(--primary-blue); color: #fff; text-align: center; padding: 15px; border-radius: 8px; text-decoration: none; font-weight: bold; margin: 25px 0; transition: background 0.2s; }}
        .btn-cta:hover {{ background: var(--hover-blue); }}

        .card {{ border-bottom: 1px solid #eee; padding: 15px 0; display: flex; gap: 15px; align-items: center; }}
        .card:last-child {{ border-bottom: none; }}
        .card img {{ width: 120px; height: 80px; border-radius: 6px; object-fit: cover; }}
        .card-title {{ font-size: 1.1rem; font-weight: 600; color: #111; text-decoration: none; transition: color 0.2s; }}
        .card-title:hover {{ color: var(--primary-blue); }}

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
    </style>
    {script_popunder}
    {script_social_bar}
</head>
<body>
    <header>
        <div class="lang-selector">
            <select onchange="location = '/' + this.value.toLowerCase() + '/' + location.pathname.split('/').pop();">
                <option value="IT" {sel_it}>IT</option>
                <option value="EN" {sel_en}>EN</option>
                <option value="ES" {sel_es}>ES</option>
                <option value="FR" {sel_fr}>FR</option>
            </select>
        </div>
        <div class="header-container">
            <h1 class="main-title-3d">{t_app_title}</h1>
        </div>
    </header>
    <nav>
        <a href="/{lingua}/index.html">{t_home}</a>
        <a href="/{lingua}/partite.html">{t_matches}</a>
        <a href="/{lingua}/mercato.html">{t_market}</a>
        <a href="/{lingua}/live.html">{t_live}</a>
    </nav>
    <main class="container">
        {page_content}
    </main>
</body>
</html>
"""

def fetch_github_file_raw(filename):
    try:
        token = st.secrets["GITHUB"]["REPOSITORIES_TOKEN"]
        repo = st.secrets["GITHUB"]["REPO_NAME"]
        url = f"https://api.github.com/repos/{repo}/contents/{filename}"
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            return base64.b64decode(res.json()["content"]).decode("utf-8"), res.json()["sha"]
        return None, None
    except Exception:
        return None, None

def push_to_github(filename, html_content, sha=None):
    try:
        token = st.secrets["GITHUB"]["REPOSITORIES_TOKEN"]
        repo = st.secrets["GITHUB"]["REPO_NAME"]
        url = f"https://api.github.com/repos/{repo}/contents/{filename}"
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
        base64_content = base64.b64encode(html_content.encode("utf-8")).decode("utf-8")
        payload = {
            "message": f"🤖 Cascade Update: {filename}",
            "content": base64_content,
            "branch": st.secrets["GITHUB"].get("ASTRONOMY_BRANCH", "main")
        }
        if sha:
            payload["sha"] = sha
        put_res = requests.put(url, headers=headers, json=payload, timeout=5)
        if put_res.status_code not in [200, 201]:
            print(f"❌ GITHUB ERROR [{put_res.status_code}]: {put_res.text}")
        return put_res.status_code in [200, 201]
    except Exception as e:
        print(f"💥 GITHUB CRASH EXCEPTION: {str(e)}")
        return False

# =====================================================================
# FUNZIONI DI AGGIORNAMENTO A CASCATA (HOME, MERCATO, PARTITE, LIVE)
# =====================================================================
def cascading_home_and_market_update(l_target, base_slug, localized_title, art_cover, is_market=False):
    target_file = f"{l_target}/mercato.html" if is_market else f"{l_target}/index.html"
    old_content, sha = fetch_github_file_raw(target_file)

    new_card_html = f"""
    <div class="card">
        <img src="{art_cover if art_cover else 'https://via.placeholder.com/120x80'}" alt="Hero">
        <div>
            <a href="/{l_target}/{base_slug}" class="card-title">{localized_title}</a>
        </div>
    </div>
    """

    if old_content:
        if "" in old_content:
            parts = old_content.split("")
            updated_html = parts[0] + "\n" + new_card_html + parts[1]
        else:
            updated_html = old_content.replace('<div id="news-feed">', f'<div id="news-feed">\n{new_card_html}').replace('<div id="market-feed">', f'<div id="market-feed">\n{new_card_html}')
    else:
        frontend_strings = get_frontend_locale(l_target)
        section_title = frontend_strings.get('t_market_title', '') if is_market else frontend_strings.get('t_home_title', '')
        section_sub = frontend_strings.get('t_market_subtitle', '') if is_market else frontend_strings.get('t_home_subtitle', '')

        content_structure = f"""<h1>{section_title}</h1>
        <p class="subtitle">{section_sub}</p>
        <div class="ad-slot">{st.secrets.get("MONETIZATION", {}).get("ADSTERRA_BANNER_300X250_TOP", "")}</div>
        <div id="{"market-feed" if is_market else "news-feed"}">
            {new_card_html}
        </div>
        <div class="ad-slot">{st.secrets.get("MONETIZATION", {}).get("ADSTERRA_BANNER_300X250_BOTTOM", "")}</div>"""

        updated_html = build_rendered_html_package(l_target, section_title, content_structure)
        
    push_to_github(target_file, updated_html, sha)

def update_dynamic_matches_and_live(l_target, selected_league_id=None, selected_league_name=None):
    api_key = st.secrets["APIS"].get("FOOTBALL_API_KEY", "")
    current_month = datetime.date.today().month
    current_year = datetime.date.today().year

    if selected_league_id is None or selected_league_id == "auto":
        if current_year == 2026 and current_month in [6, 7]:
            league_id = "1"
            comp_name = "FIFA World Cup 2026"
        else:
            league_id = "135"
            comp_name = "Serie A"
    else:
        league_id = selected_league_id
        comp_name = selected_league_name

    frontend_strings = get_frontend_locale(l_target)

    matches_widget = f"""
    <div id="wg-api-football-games"
         data-host="v3.football.api-sports.io"
         data-key="{api_key}"
         data-league="{league_id}"
         data-season="{current_year}"
         data-theme="light"
         data-refresh="0"
         data-show-toolbar="true"
         data-show-errors="false">
    </div>
    <script type="module" src="https://widgets.api-sports.io/2.0.3/widgets.js"></script>
    """

    matches_html_content = f"<h1>{frontend_strings.get('t_matches_title', '')}</h1>"
    matches_html_content += f"<p class='subtitle'>{frontend_strings.get('t_matches_subtitle', '')}</p>"
    matches_html_content += f"<h2>⚽ {comp_name} ({current_year})</h2>"
    matches_html_content += f"<div class='ad-slot'>{st.secrets.get('MONETIZATION', {}).get('ADSTERRA_BANNER_300X250_TOP', '')}</div>"
    matches_html_content += matches_widget
    matches_html_content += f"<div class='ad-slot'>{st.secrets.get('MONETIZATION', {}).get('ADSTERRA_BANNER_300X250_BOTTOM', '')}</div>"

    final_matches_html = build_rendered_html_package(l_target, frontend_strings.get('t_matches_title', ''), matches_html_content)
    
    _, sha_m = fetch_github_file_raw(f"{l_target}/partite.html")
    push_to_github(f"{l_target}/partite.html", final_matches_html, sha_m)

    live_pitch_html = f"""
    <h2>{frontend_strings.get('t_live_score_title', '')}</h2>
    <p class="subtitle">{frontend_strings.get('t_live_score_subtitle', '')}</p>
    <div class='ad-slot'>{st.secrets.get('MONETIZATION', {}).get('ADSTERRA_BANNER_300X250_TOP', '')}</div>

    <div class="pitch-container">
        <div class="pitch">
            <div class="pitch-lines"></div>
            <div class="center-circle"></div>
            <div id="players-layout-target"></div>
        </div>
    </div>

    <script>
        async function fetchTacticalLiveEngine() {{
            try {{
                const res = await fetch('https://v3.football.api-sports.io/fixtures?league={league_id}&current=true', {{
                    method: 'GET',
                    headers: {{
                        'x-rapidapi-host': 'v3.football.api-sports.io',
                        'x-rapidapi-key': '{api_key}'
                    }}
                }});
                const data = await res.json();
                if(!data.response || data.response.length === 0) {{
                    document.getElementById('players-layout-target').innerHTML = "<div style='color:white; text-align:center; padding-top:160px; font-size:0.9rem;'>{frontend_strings.get('t_live_waiting_message', '')}</div>";
                    return;
                }}

                const fixtureId = data.response[0].fixture.id;
                const lineupRes = await fetch('https://v3.football.api-sports.io/fixtures/lineups?fixture=' + fixtureId, {{
                    method: 'GET',
                    headers: {{ 'x-rapidapi-host': 'v3.football.api-sports.io', 'x-rapidapi-key': '{api_key}' }}
                }});
                const lineupData = await lineupRes.json();

                const target = document.getElementById('players-layout-target');
                target.innerHTML = '';

                if(lineupData.response && lineupData.response.length >= 2) {{
                    lineupData.response[0].startXI.forEach(p => {{
                        if(p.player.grid) {{
                            const parts = p.player.grid.split(':');
                            const x = parseFloat(parts[0]) * 8;
                            const y = parseFloat(parts[1]) * 22;
                            target.innerHTML += `<div class="player-node team-home" style="left: ${{x}}%; top: ${{y}}px;">
                                <span class="player-tooltip">${{p.player.name}} (${{p.player.number}})</span>
                            </div>`;
                        }
                    }});
                    lineupData.response[1].startXI.forEach(p => {{
                        if(p.player.grid) {{
                            const parts = p.player.grid.split(':');
                            const x = parseFloat(parts[0]) * 8;
                            const y = 340 - (parseFloat(parts[1]) * 22);
                            target.innerHTML += `<div class="player-node team-away" style="left: ${{x}}%; top: ${{y}}px;">
                                <span class="player-tooltip">${{p.player.name}} (${{p.player.number}})</span>
                            </div>`;
                        }
                    }});
                }}
            }} catch(e) {{ console.log('Live Widget Offline'); }}
        }}
        fetchTacticalLiveEngine();
        setInterval(fetchTacticalLiveEngine, 60000);
    </script>

    <div class='ad-slot'>{st.secrets.get('MONETIZATION', {}).get('ADSTERRA_BANNER_300X250_BOTTOM', '')}</div>
    <a href='{st.secrets.get("MONETIZATION", {}).get("STREAMING_AFFILIATE_URL", "#")}' class='btn-cta'>🔴 {frontend_strings.get('t_btn_watch_live', '')}</a>
    """

    final_live_html = build_rendered_html_package(l_target, frontend_strings.get('t_live', ''), live_pitch_html)
    old_l, sha_l = fetch_github_file_raw(f"{l_target}/live.html")
    push_to_github(f"{l_target}/live.html", final_live_html, sha_l)

# =====================================================================
# 4. INTERFACCIA DASHBOARD MULTITASKING (STRUTTURA WITH TAB ALLINEATA)
# =====================================================================
tab_editoriale, tab_archive, tab_finanze, tab_config = st.tabs([
    t("tab_editorial"), t("tab_archive"), t("tab_finance"), t("tab_config")
])

# --- TAB 1: MACCHINA EDITORIALE ---
with tab_editoriale:
    st.subheader(t("editor_title"))

    league_options = {
        t("comp_auto"): ("auto", "Auto"),
        "Serie A (Italia)": ("135", "Serie A"),
        "Premier League (Inghilterra)": ("39", "Premier League"),
        "LaLiga (Spagna)": ("140", "LaLiga"),
        "UEFA Champions League": ("2", "UEFA Champions League"),
        "FIFA World Cup 2026": ("1", "FIFA World Cup 2026")
    }
    selected_comp_lbl = st.selectbox(t("competition_lbl"), list(league_options.keys()))
    chosen_league_id, chosen_league_name = league_options[selected_comp_lbl]

    match_name = st.text_input(t("input_match_name"), placeholder="Es: Real Madrid vs Milan")
    art_title = st.text_input(t("input_title"))
    art_cover = st.text_input(t("input_cover"), placeholder="https://images.unsplash.com/...")

    if "generated_body" not in st.session_state:
        st.session_state.generated_body = ""

    if st.button(t("btn_generate")):
        if match_name:
            with st.spinner(t("spinner_gemini_writing")):
                sys_prompt = "Sei un giornalista sportivo esperto SEO. Scrivi in HTML puro usando solo p, h2, strong, ul, li. Output rigidissimo: restituisci SOLO il testo finale in HTML, senza introduzioni o opzioni alternative."
                user_prompt = f"Scrivi una cronaca o un articolo di calciomercato su: {match_name}. Sii avvincente."
                st.session_state.generated_body = genera_testo_gemini_ciclico(sys_prompt, user_prompt)

    art_body = st.text_area(t("input_body"), value=st.session_state.generated_body, height=250)

    if art_title or art_body or art_cover:
        with st.expander(t("preview_live_title"), expanded=True):
            if art_title:
                st.markdown(f"<h1 style='font-family: Inter, sans-serif; font-weight:600; color: #111; font-size: 1.8rem; margin-bottom:10px;'>{art_title}</h1>", unsafe_allow_html=True)
            if art_cover:
                st.image(art_cover, use_container_width=True)
            if art_body:
                st.markdown(art_body, unsafe_allow_html=True)

    if st.button(t("btn_publish_all")):
        if art_title and art_body and match_name:
            base_slug = match_name.lower().replace(" vs ", "-").replace(" ", "-") + ".html"
            is_market_article = any(keyword in match_name.lower() or keyword in art_title.lower() for keyword in ["mercato", "calciomercato", "transfer", "fichajes", "mercato"])
            list_langs = ["it", "en", "es", "fr"]
            success_count = 0

            progress_pub = st.progress(0)
            for index_l, l_target in enumerate(list_langs):
                with st.spinner(t("spinner_lang_align").format(l_target.upper())):
                    sys_p = f"Sei un giornalista sportivo esperto SEO. Scrivi l'articolo interamente in lingua: {l_target}. Usa HTML puro (p, h2, strong, ul, li). Output rigidissimo: restituisci SOLO l'HTML senza testo descrittivo aggiuntivo prima o dopo."
                    user_p = f"Traduci o riscrivi in modo fluido e giornalistico questo contenuto: {art_body}. Il titolo è: {art_title}"
                    localized_body = genera_testo_gemini_ciclico(sys_p, user_p)

                    sys_t = f"Sei un traduttore perfetto. Traduci questo titolo in {l_target} per un giornale SEO. Restituisci TASSATIVAMENTE SOLO la stringa del titolo tradotto. Non aggiungere introduzioni, non dare opzioni numerate, non mettere virgolette e non scrivere note di spiegazione."
                    localized_title = genera_testo_gemini_ciclico(sys_t, art_title).replace('"', '').replace("'", "")

                    article_html_rendered = f"""
                    <h1>{localized_title}</h1>
                    <img src="{art_cover if art_cover else 'https://via.placeholder.com/600x350'}" class="cover-hero" alt="Hero">
                    <div class="ad-slot">{st.secrets.get("MONETIZATION", {}).get("ADSTERRA_BANNER_300X250_TOP", "")}</div>
                    <div class="content">{localized_body}</div>
                    <div class="ad-slot">{st.secrets.get("MONETIZATION", {}).get("ADSTERRA_BANNER_300X250_BOTTOM", "")}</div>
                    """

                    final_html = build_rendered_html_package(l_target, localized_title, article_html_rendered)

                    full_filename = f"{l_target}/{base_slug}"
                    if push_to_github(full_filename, final_html):
                        success_count += 1

                        with st.spinner(t("spinner_updating_index")):
                            cascading_home_and_market_update(l_target, base_slug, localized_title, art_cover, is_market=False)

                        if is_market_article:
                            with st.spinner(t("spinner_updating_market")):
                                cascading_home_and_market_update(l_target, base_slug, localized_title, art_cover, is_market=True)

                        with st.spinner(t("spinner_updating_matches")):
                            update_dynamic_matches_and_live(l_target, chosen_league_id, chosen_league_name)

                        full_url = f"https://championsreport.editories.com/{full_filename}"
                        ping_google_indexing(full_url)

                time.sleep(1.2)
                progress_pub.progress((index_l + 1) / len(list_langs))

            if success_count == len(list_langs):
                st.success(t("success_published"))
            else:
                st.warning(t("pub_partial_warn").format(success_count, len(list_langs)))

# --- TAB 2: ARCHIVIO & SCHEDULER ---
with tab_archive:
    st.subheader(t("archive_title"))
    st.markdown("---")
    st.subheader(t("scheduler_section"))
    col_date, col_time = st.columns(2)
    with col_date:
        data_pub = st.date_input(t("scheduler_date"), datetime.date.today())
    with col_time:
        ora_pub = st.time_input(t("scheduler_time"), datetime.time(12, 0))

    if st.button(t("scheduler_btn")):
        if art_title:
            queue_data = {
                "title": art_title,
                "cover": art_cover,
                "body": art_body,
                "publish_at": f"{data_pub.strftime('%Y-%m-%d')} {ora_pub.strftime('%H:%M:%S')}"
            }
            with open(QUEUE_FILE, "a") as f:
                f.write(json.dumps(queue_data) + "\n")
            st.success(t("scheduler_success").format(data_pub.strftime('%d/%m/%Y'), ora_pub.strftime('%H:%M')))

# --- TAB 3: PERFORMANCE & RICEVUTE ---
with tab_finanze:
    st.subheader(t("finance_title"))
    st.markdown("---")
    st.markdown(f"### {t('finance_section_stats')}")

    live_views, live_clicks, live_cpm = "0", "0", "€ 0.00"
    adsterra_api_key = ""
    analytics_shared_url = ""
    if "APIS" in st.secrets:
        adsterra_api_key = st.secrets["APIS"].get("ADSTERRA_API_KEY", "").strip()
        analytics_shared_url = st.secrets["APIS"].get("ANALYTICS_SHARED_URL", "").strip()

    if adsterra_api_key and "La_Tua_Chiave" not in adsterra_api_key:
        try:
            api_url = f"https://api3.adsterra.com/publisher/{adsterra_api_key}/stats.json"
            response = requests.get(api_url, timeout=5)
            if response.status_code == 200:
                api_data = response.json()
                if isinstance(api_data, dict) and "error" not in api_data:
                    live_views = f"{api_data.get('total_impressions', 0):,}"
                    live_clicks = f"{api_data.get('total_clicks', 0):,}"
                    try:
                        live_cpm = f"€ {float(api_data.get('avg_cpm', 0.0)):,.2f}"
                    except (ValueError, TypeError): pass
                else: live_views, live_clicks, live_cpm = "Chiave Errata", "Chiave Errata", "Chiave Errata"
            else: live_views, live_clicks, live_cpm = "Errore API", "Errore API", "Errore API"
        except Exception:
            live_views, live_clicks, live_cpm = "Offline", "Offline", "Offline"
            st.caption(t("finance_api_error"))

    total_csv_amount = 0.0
    if os.path.exists(FINANCE_FILE) and os.path.getsize(FINANCE_FILE) > 0:
        df_f = pd.read_csv(FINANCE_FILE)
        total_csv_amount = float(df_f[df_f["Stato"] == t("finance_status_paid")]["Importo"].sum())

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1: st.metric(label=t("finance_metric_views"), value=live_views)
    with m_col2: st.metric(label=t("finance_metric_clicks"), value=live_clicks)
    with m_col3: st.metric(label=t("finance_metric_cpm"), value=live_cpm)
    with m_col4: st.metric(label=t("finance_metric_balance"), value=f"€ {total_csv_amount:,.2f}")

    if analytics_shared_url:
        st.write(f"✅ {t('finance_analytics_ready')}")
        st.components.v1.iframe(analytics_shared_url, height=450, scrolling=True)
    else: st.info(t("finance_analytics_waiting"))

    st.markdown("---")
    st.markdown(f"### {t('finance_section_ledger')}")
    with st.form("registro_ricevute_form", clear_on_submit=True):
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1: net_name = st.selectbox(t("finance_lbl_network"), ["Adsterra", "PropellerAds", "Awin (DAZN)", "Altri Guadagni"])
        with col_f2: amount = st.number_input(t("finance_lbl_amount"), min_value=0.0, step=10.0)
        with col_f3: status = st.selectbox(t("finance_lbl_status"), [t("finance_status_paid"), t("finance_status_pending")])
        submit_finance = st.form_submit_button(t("finance_btn_save"))
        if submit_finance:
            new_row = pd.DataFrame([{"Data": datetime.date.today().strftime("%Y-%m-%d"), "Network": net_name, "Importo": amount, "Stato": status}])
            if not os.path.exists(FINANCE_FILE): new_row.to_csv(FINANCE_FILE, index=False)
            else: new_row.to_csv(FINANCE_FILE, mode='a', header=False, index=False)
            st.success(t("finance_success_save"))
            st.rerun()

    if os.path.exists(FINANCE_FILE) and os.path.getsize(FINANCE_FILE) > 0:
        df_finance = pd.read_csv(FINANCE_FILE)
        col_table, col_chart = st.columns([5, 4])
        with col_table: st.dataframe(df_finance, use_container_width=True, height=200)
        with col_chart: st.bar_chart(df_finance.groupby("Network")["Importo"].sum(), height=200)
    else:
        st.info(t("finance_no_data"))

# --- TAB 4: CONFIG & BATCH ---
with tab_config:
    st.subheader(t("config_title"))
    st.markdown("---")
    st.subheader(t("batch_section"))
    lista_batch = st.text_area(t("batch_label"), height=150, placeholder=t("batch_placeholder"))

    if st.button(t("batch_btn")):
        if lista_batch.strip():
            match_items = [item.strip() for item in lista_batch.split("\n") if item.strip()]
            progress_bar = st.progress(0)
            for i, match in enumerate(match_items):
                st.write(f"🔄 {t('batch_progress').format(i+1, len(match_items))} ({match})")
                sys_p = "Sei un cronista sportivo SEO. Scrivi in HTML puro (p, h2). Output rigidissimo: restituisci SOLO l'HTML, senza introduzioni o commenti."
                user_p = f"Genera un report pre-partita per {match}."
                generated_text = genera_testo_gemini_ciclico(sys_p, user_p)

                batch_article_content = f"<h1>{match}</h1><div class='content'>{generated_text}</div>"

                lang_current = st.session_state.lang
                batch_html = build_rendered_html_package(lang_current, match, batch_article_content)
                
                slug_batch = f"{lang_current}/{match.lower().replace(' vs ', '-').replace(' ', '-')}.html"
                if push_to_github(slug_batch, batch_html):
                    cascading_home_and_market_update(lang_current, f"{match.lower().replace(' vs ', '-').replace(' ', '-')}.html", match, "https://via.placeholder.com/120x80", is_market=False)
                    ping_google_indexing(f"https://championsreport.editories.com/{slug_batch}")

                time.sleep(1.2)
                progress_bar.progress((i + 1) / len(match_items))
            st.success(t("batch_success_toast"))
