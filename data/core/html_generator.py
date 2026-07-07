import os
import re
import html

def generate_html(menu_fr, translations):
    css = """
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Inter', sans-serif; background: #0a0a0a; padding: 20px; min-height: 100vh; color: #fafafa; }
    .container { max-width: 900px; margin: 0 auto; background: #1a1a1a; border-radius: 20px; padding: 40px; box-shadow: 0 20px 60px rgba(0,0,0,0.6); border: 1px solid rgba(255,255,255,0.05); }
    h1 { text-align: center; color: #10b981; margin-bottom: 32px; font-size: 2.5rem; font-weight: 800; }
    .tabs { display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; margin-bottom: 32px; border-bottom: 3px solid rgba(255,255,255,0.1); padding-bottom: 16px; }
    .tab { padding: 8px 12px; border-radius: 8px; cursor: pointer; font-weight: 700; color: #a3a3a3; background: rgba(255,255,255,0.05); transition: all 0.3s; font-size: 0.9rem; }
    .tab.active { background: #10b981; color: #0a0a0a; box-shadow: 0 4px 12px rgba(16,185,129,0.4); }
    .tab:hover:not(.active) { background: rgba(16,185,129,0.15); color: #10b981; }
    .lang-section { display: none; }
    .lang-section.active { display: block; }
    .section { margin-bottom: 32px; background: rgba(255,255,255,0.03); padding: 24px; border-radius: 12px; border-left: 5px solid #10b981; }
    .section-title { color: #10b981; font-size: 1.4rem; font-weight: 800; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 0.5px; }
    .menu-item { padding: 16px 0; border-bottom: 1px dashed rgba(255,255,255,0.1); }
    .menu-item:last-child { border-bottom: none; }
    .item-top-row { display: flex; justify-content: space-between; align-items: baseline; gap: 15px; width: 100%%; }
    .dish-title { font-weight: 800; color: #fafafa; font-size: 1.15rem; flex: 1; line-height: 1.3; }
    .dish-desc { font-style: italic; font-weight: 400; color: #a3a3a3; font-size: 0.95rem; display: block; margin-top: 6px; line-height: 1.5; }
    .item-price { font-weight: 800; color: #34d399; font-size: 1.1rem; white-space: nowrap; min-width: 60px; text-align: right; }
    .footer { text-align: center; margin-top: 32px; padding-top: 20px; border-top: 3px solid rgba(255,255,255,0.1); color: #6b7280; font-size: 0.9rem; font-weight: 600; }
    """

    page_titles = {
        'fr': '🍽️ Le Menu',
        'en': '🍽️ The Menu',
        'es': '🍽️ El Menú',
        'de': '🍽️ Die Speisekarte',
        'it': '🍽️ Il Menu',
        'ru': '🍽️ Меню'
    }

    section_titles = {
        'fr': {'entrees': 'Entrées', 'plats': 'Plats', 'desserts': 'Desserts', 'formules': 'Formules'},
        'en': {'entrees': 'Starters', 'plats': 'Dishes', 'desserts': 'Desserts', 'formules': 'Formulas'},
        'es': {'entrees': 'Entrantes', 'plats': 'Platos', 'desserts': 'Postres', 'formules': 'Fórmulas'},
        'de': {'entrees': 'Vorspeisen', 'plats': 'Gerichte', 'desserts': 'Desserts', 'formules': 'Formeln'},
        'it': {'entrees': 'Antipasti', 'plats': 'Piatti', 'desserts': 'Dolci', 'formules': 'Menu'},
        'ru': {'entrees': 'Закуски', 'plats': 'Блюда', 'desserts': 'Десерты', 'formules': 'Меню'}
    }

    langs = ['fr', 'en', 'es', 'de', 'it', 'ru']
    tabs_html = ''
    for l in langs:
        cls = 'tab active' if l == 'fr' else 'tab'
        tabs_html += '<div class="' + cls + '" data-lang="' + l + '">' + l.upper() + '</div>'

    content_html = ''
    for lang in langs:
        cls = 'lang-section active' if lang == 'fr' else 'lang-section'
        content_html += '<div class="' + cls + '" id="lang-' + lang + '"><h1>' + page_titles.get(lang, '🍽️ Le Menu') + '</h1>'

        for key in ['entrees', 'plats', 'desserts', 'formules']:
            items = menu_fr.get(key, [])
            if not items:
                continue
            title = section_titles.get(lang, section_titles['fr']).get(key, key.title())
            content_html += '<div class="section"><h2 class="section-title">' + title + '</h2><div class="items">'

            for item in items:
                item_id = item.get('id', '')
                nom_fr = item.get('nom', '')
                prix = item.get('prix', '')

                tr = translations.get(item_id, {})
                nom = tr.get(lang, nom_fr)

                lines = nom.split('\n')
                # PROTECTION XSS : html.escape() nettoie les balises HTML/JS malveillantes
                dish_title = html.escape(re.sub(r'\[\[(.*?)\]\]', r'\1', lines[0].strip()))
                dish_desc = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ''
                
                price_str = str(prix).strip()
                if price_str and not any(price_str.endswith(s) for s in ['€', '$', '£', 'CHF']):
                    price_str += ' €'

                content_html += '<div class="menu-item"><div class="item-top-row"><div class="dish-title">' + dish_title + '</div><div class="item-price">' + price_str + '</div></div>'
                if dish_desc:
                    # PROTECTION XSS sur la description aussi
                    content_html += '<div class="dish-desc">' + html.escape(dish_desc).replace('\n', '<br>') + '</div>'
                content_html += '</div>'

            content_html += '</div></div>'

        content_html += '</div>'

    js = """<script>
    document.querySelectorAll('.tab').forEach(function(tab) {
        tab.addEventListener('click', function() {
            var lang = this.getAttribute('data-lang');
            document.querySelectorAll('.tab').forEach(function(t) { t.classList.remove('active'); });
            document.querySelectorAll('.lang-section').forEach(function(s) { s.classList.remove('active'); });
            this.classList.add('active');
            document.getElementById('lang-' + lang).classList.add('active');
        });
    });
    </script>"""

    html_doc = '<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8"><meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate"><meta http-equiv="Pragma" content="no-cache"><meta http-equiv="Expires" content="0"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Menu</title><style>' + css + '</style></head><body>'
    html_doc += '<div class="container"><div class="tabs">' + tabs_html + '</div>' + content_html
    html_doc += '<div class="footer">ArdoiseDigitale</div></div>' + js + '</body></html>'
    return html_doc
