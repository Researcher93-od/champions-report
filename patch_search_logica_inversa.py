import re

with open("cr-generator.py", "r", encoding="utf-8") as f:
    code = f.read()

nuova_logica_hunter = """
def modulo_hunter_esploratore(iso_data, competizione_filtro=None):
    \"\"\"LOGICA INVERSA: Search (Parola Chiave) -> Extract -> Filter (Data).\"\"\"
    print(f"🔍 [HUNTER-LOGICA-INVERSA] Ricerca generale per: {competizione_filtro or 'Mondiali 2026'}...")
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # Ricerca larga (Set)
    query = f"{competizione_filtro or 'Mondiali 2026'} calendario partite"
    url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        testo_estratto = " ".join([s.get_text() for s in soup.find_all("div", class_="result__snippet")])
        
        # Filtro Temporale (Subset) tramite AI
        prompt_sistema = "Sei un filtro di dati temporali."
        prompt_utente = f\"\"\"Dato il seguente testo estratto dal web:
        {testo_estratto}
        
        COMPITO: Filtra queste informazioni e isola solo le partite programmate per la data {iso_data}.
        REGOLE:
        1. Se la partita non è specificamente per il {iso_data}, ignorala.
        2. Restituisci JSON puro: [ {{"squadra_a": "...", "squadra_b": "...", "ora": "...", "stadio": "..."}} ]
        3. Se non trovi nulla per il {iso_data}, rispondi: []\"\"\"
        
        raw_json = chiedi_raw_ai(prompt_sistema, prompt_utente)
        return json.loads(raw_json.strip().replace("```json", "").replace("```", ""))
    except: return []
"""

# Sostituiamo il vecchio hunter
pattern_hunter = re.compile(r"def modulo_hunter_esploratore.*?return matches_cacciati", re.DOTALL)
code = pattern_hunter.sub(nuova_logica_hunter, code)

with open("cr-generator.py", "w", encoding="utf-8") as f:
    f.write(code)

print("✅ Hunter convertito in logica Inversa (Search -> Filter)!")
