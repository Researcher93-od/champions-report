def targeted_discovery_remota_ai(parola_chiave, data_target, anno_corrente):
    """
    Motore Hunter evoluto: Forza il recentismo nel Grounding e rende 
    il parsing cognitivo tollerante sui fusi orari dei match internazionali.
    """
    print(f"🔍 [TARGETED DISCOVERY] Avvio ricerca sul web con Google Grounding contestualizzato...")
    prompt_sistema_cerca = "Sei un giornalista sportivo e un archivista preciso. Il tuo unico scopo è elencare le partite."
    prompt_utente_cerca = f"""Cerca sul web le partite di calcio per la competizione/squadra '{parola_chiave}' programmate, in corso o giocate in data {data_target} (Anno {anno_corrente}).
    Trova i match dei sedicesimi/fasi del torneo di oggi, includendo squadre, orario originario (es. ET o locali negli USA/Messico/Canada) o italiano, stadio e città."""
    
    risultato_ricerca_testuale = chiedi_raw_ai(prompt_sistema_cerca, prompt_utente_cerca, usa_search=True)
    
    if not risultato_ricerca_testuale or len(risultato_ricerca_testuale.strip()) < 10:
        print("⚠️ Nessun dato grezzo estratto dal web. Google Grounding non ha restituito testo.")
        return []

    print(f"🧠 [PARSING COGNITIVO] Organizzazione e normalizzazione fusi orari in formato strutturato...")
    prompt_sistema_parse = "Sei un analista dati. Converti le informazioni fornite in JSON nativo valido e pulito."
    prompt_utente_parse = f"""Analizza questo report di ricerca:
---
{risultato_ricerca_testuale}
---
COMPITO: Estrai le partite di calcio del giorno {data_target} e strutturale in un array JSON nativo:
[ {{"squadra_a": "Nome Squadra Casa", "squadra_b": "Nome Squadra Ospite", "ora": "Orario convertito in CEST o stringa originale", "data_iso": "{data_target}", "stadio": "Nome Stadio", "citta": "Città"}} ]

REGOLE TASSATIVE:
1. Compila i campi basandoti sul testo. Se l'orario è americano (es. 3 p.m. ET), convertilo in ora italiana (21:00 CEST) o lascialo come stringa leggibile.
2. Se non risultano match nel testo, restituisci un array vuoto: []
3. Restituisci SOLO il codice JSON, senza racchiuderlo in markdown."""

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
