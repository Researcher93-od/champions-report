import re

files = {
    "it.html": ("All. Carlo Ancelotti", "All. Hajime Moriyasu"),
    "en.html": ("Coach: Carlo Ancelotti", "Coach: Hajime Moriyasu"),
    "es.html": ("D.T. Carlo Ancelotti", "D.T. Hajime Moriyasu"),
    "fr.html": ("Sél. Carlo Ancelotti", "Sél. Hajime Moriyasu")
}

for filename, (coach_br, coach_jp) in files.items():
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_block = f"""<div class="lineups">
                <p><strong>Brasile (4-2-3-1):</strong> Alisson; Danilo, Marquinhos, Gabriel, Santos; Guimarães, Casemiro; Rayan, Paquetá, Vinícius Jr.; Cunha.</p>
                <p class="coach">{coach_br}</p>
                <br>
                <p><strong>Giappone (3-4-2-1):</strong> Suzuki; Ito, Tomiyasu, Itakura; Doan, Sano, Tanaka, Nakamura; Kamada, Maeda; Ueda.</p>
                <p class="coach">{coach_jp}</p>
            </div>"""
    
    updated_content = re.sub(r'<div class="lineups">.*?</div>', new_block, content, flags=re.DOTALL)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(updated_content)

print("✅ Formazioni aggiornate chirurgicamente nei 4 file!")
