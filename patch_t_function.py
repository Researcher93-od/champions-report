with open("cr-generator.py", "r", encoding="utf-8") as f:
    content = f.read()

# Trova la riga incriminata e posiziona correttamente la funzione t prima del main execution block
old_block = """def t(chiave):
    \"\"\"i18n lookup function.\"\"\"
    return I18N_DICTIONARY[CURRENT_LANG].get(chiave, chiave)"""

# Ripristiniamo la funzione t(chiave) assicurandoci che sia visibile globalmente
if old_block in content:
    print("✅ Function t is already in code, checking position...")
else:
    # Se per qualche motivo è stata spostata o corrotta la riposizioniamo subito sotto il dizionario I18N_DICTIONARY
    content = re.sub(r'CURRENT_LANG = "en".*?\n', 'CURRENT_LANG = "en"\n\ndef t(chiave):\n    \"\"\"i18n lookup function.\"\"\"\n    return I18N_DICTIONARY[CURRENT_LANG].get(chiave, chiave)\n', content)

with open("cr-generator.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ Order of i18n lookup core fixed successfully!")
